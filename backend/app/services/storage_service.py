import os
import re
import uuid
import time
import json
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from backend.app.config import settings, PROJECT_ROOT

logger = logging.getLogger("SmartGlasses.StorageService")

ALLOWED_DOCUMENT_MIMES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc"
}

ALLOWED_IMAGE_MIMES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif"
}

ALLOWED_ALL_MIMES = {**ALLOWED_DOCUMENT_MIMES, **ALLOWED_IMAGE_MIMES}

MAX_DOCUMENT_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024     # 10 MB

class StorageService:
    """
    Unified Storage and Document Pipeline for Smart Glasses AI.
    
    Responsibilities:
    - Securely stores files in local filesystem (`storage/uploads/`).
    - Enforces path traversal protection and filename sanitization.
    - Validates MIME types, extensions, and file sizes.
    - Persists file metadata in SQLite (`uploaded_files` table).
    - Extracts searchable text from PDF, TXT, Markdown, CSV, and DOCX documents.
    - Provides context injection for LARA when answering questions about user files.
    """

    def __init__(self, storage_dir: Optional[str] = None, db_path: Optional[str] = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = PROJECT_ROOT / "storage" / "uploads"
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)


        if db_path:
            self.db_path = db_path
        elif settings.DATABASE_URL.startswith("sqlite:///"):
            self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        else:
            self.db_path = "./smart_glasses.db"

        self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False) if self.db_path == ":memory:" else None
        if self._mem_conn:
            self._mem_conn.row_factory = sqlite3.Row

        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create uploaded_files table if it does not exist."""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    file_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    extracted_text TEXT,
                    metadata_json TEXT,
                    created_at REAL NOT NULL,
                    created_at_iso TEXT NOT NULL
                )
            """)
            conn.commit()

    def sanitize_filename(self, raw_filename: str) -> str:
        """Strip directory paths, null bytes, and unsafe characters."""
        if not raw_filename:
            return "unnamed_file"
        # Take basename only to prevent directory traversal
        basename = os.path.basename(raw_filename)
        # Remove dangerous characters
        sanitized = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', basename).strip()
        return sanitized if sanitized else "unnamed_file"

    def extract_text_from_file(self, file_path: Path, mime_type: str) -> str:
        """Extracts plain text content from documents for LARA context indexing."""
        try:
            if not file_path.exists():
                return ""

            # 1. Plain Text / Markdown / CSV
            if mime_type in ["text/plain", "text/markdown", "text/csv"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(50000)  # Max 50KB text
                    return content.strip()

            # 2. PDF Extraction
            if mime_type == "application/pdf":
                extracted_pages = []
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(file_path))
                    for i, page in enumerate(reader.pages[:10]):  # First 10 pages
                        text = page.extract_text()
                        if text:
                            extracted_pages.append(text.strip())
                    return "\n\n".join(extracted_pages)
                except ImportError:
                    pass

                # Fallback basic PDF text stream extractor
                try:
                    with open(file_path, "rb") as f:
                        raw = f.read(100000)
                    matches = re.findall(rb"\(([\x20-\x7E]{3,})\)", raw)
                    if matches:
                        return b" ".join(matches).decode("latin-1", errors="ignore")[:3000]
                except Exception as e:
                    logger.warning(f"PDF fallback text extraction failed: {e}")

            # 3. DOCX Extraction
            if "wordprocessingml" in mime_type or file_path.suffix.lower() == ".docx":
                try:
                    import zipfile
                    import xml.etree.ElementTree as ET
                    with zipfile.ZipFile(str(file_path)) as docx_zip:
                        xml_content = docx_zip.read('word/document.xml')
                        tree = ET.fromstring(xml_content)
                        paragraphs = []
                        for elem in tree.iter():
                            if elem.tag.endswith('}t') and elem.text:
                                paragraphs.append(elem.text)
                        return " ".join(paragraphs)[:30000]
                except Exception as e:
                    logger.warning(f"DOCX extraction failed: {e}")

        except Exception as e:
            logger.error(f"Error during document text extraction for {file_path}: {e}")
        return ""

    def save_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        source: str = "web",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validates, securely stores, and indexes an uploaded file.
        """
        if not file_bytes:
            raise ValueError("Uploaded file is empty (0 bytes).")

        size_bytes = len(file_bytes)
        clean_name = self.sanitize_filename(filename)
        ext = os.path.splitext(clean_name)[1].lower()

        # Resolve MIME type
        resolved_mime = content_type or "application/octet-stream"
        if resolved_mime == "application/octet-stream" or not resolved_mime:
            for mime, valid_ext in ALLOWED_ALL_MIMES.items():
                if ext == valid_ext:
                    resolved_mime = mime
                    break

        is_image = resolved_mime.startswith("image/") or ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]
        max_allowed = MAX_IMAGE_SIZE_BYTES if is_image else MAX_DOCUMENT_SIZE_BYTES

        if size_bytes > max_allowed:
            limit_mb = max_allowed / (1024 * 1024)
            raise ValueError(f"File size exceeds maximum allowed limit of {limit_mb:.0f} MB.")

        # Generate unique ID and safe storage path
        file_id = f"file_{uuid.uuid4().hex[:12]}"
        safe_stored_name = f"{file_id}{ext if ext else '.bin'}"
        dest_path = self.storage_dir / safe_stored_name

        # Write file securely
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        # Extract text if document
        extracted_text = ""
        if not is_image:
            extracted_text = self.extract_text_from_file(dest_path, resolved_mime)

        now = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        meta_dict = metadata or {}
        meta_json = json.dumps(meta_dict)

        # Save record in SQLite
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO uploaded_files (
                    file_id, filename, mime_type, size_bytes, source,
                    storage_path, extracted_text, metadata_json, created_at, created_at_iso
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id, clean_name, resolved_mime, size_bytes, source,
                str(dest_path), extracted_text, meta_json, now, now_iso
            ))
            conn.commit()

        logger.info(f"Stored file '{clean_name}' (ID: {file_id}, size: {size_bytes}B, MIME: {resolved_mime})")

        return {
            "file_id": file_id,
            "filename": clean_name,
            "mime_type": resolved_mime,
            "size_bytes": size_bytes,
            "source": source,
            "created_at": now_iso,
            "has_extracted_text": bool(extracted_text),
            "text_preview": (extracted_text[:200] + "...") if extracted_text else None
        }

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve file metadata by ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM uploaded_files WHERE file_id = ?",
                (file_id,)
            ).fetchone()

        if not row:
            return None

        return {
            "file_id": row["file_id"],
            "filename": row["filename"],
            "mime_type": row["mime_type"],
            "size_bytes": row["size_bytes"],
            "source": row["source"],
            "storage_path": row["storage_path"],
            "extracted_text": row["extracted_text"],
            "metadata": json.loads(row["metadata_json"] or "{}"),
            "created_at": row["created_at_iso"]
        }

    def get_file_bytes(self, file_id: str) -> Optional[Tuple[bytes, str, str]]:
        """Retrieve raw file content bytes, filename, and mime type."""
        file_info = self.get_file(file_id)
        if not file_info:
            return None
        path = Path(file_info["storage_path"])
        if not path.exists():
            return None
        with open(path, "rb") as f:
            data = f.read()
        return (data, file_info["filename"], file_info["mime_type"])

    def delete_file(self, file_id: str) -> bool:
        """Deletes file from storage and database."""
        file_info = self.get_file(file_id)
        if not file_info:
            return False

        path = Path(file_info["storage_path"])
        if path.exists():
            try:
                path.unlink()
            except Exception as e:
                logger.warning(f"Error removing physical file {path}: {e}")

        with self._get_conn() as conn:
            conn.execute("DELETE FROM uploaded_files WHERE file_id = ?", (file_id,))
            conn.commit()

        logger.info(f"Deleted file ID {file_id}")
        return True

    def list_files(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent uploaded files."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT file_id, filename, mime_type, size_bytes, source, created_at_iso FROM uploaded_files ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()

        return [
            {
                "file_id": r["file_id"],
                "filename": r["filename"],
                "mime_type": r["mime_type"],
                "size_bytes": r["size_bytes"],
                "source": r["source"],
                "created_at": r["created_at_iso"]
            }
            for r in rows
        ]

    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search uploaded documents by filename and extracted text content."""
        clean_q = query.strip()
        if not clean_q:
            return self.list_files(limit=limit)

        pattern = f"%{clean_q}%"
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT file_id, filename, mime_type, size_bytes, source, extracted_text, created_at_iso
                FROM uploaded_files
                WHERE filename LIKE ? OR extracted_text LIKE ?
                ORDER BY created_at DESC LIMIT ?
            """, (pattern, pattern, limit)).fetchall()

        results = []
        for r in rows:
            text = r["extracted_text"] or ""
            preview = text[:250] + "..." if len(text) > 250 else text
            results.append({
                "file_id": r["file_id"],
                "filename": r["filename"],
                "mime_type": r["mime_type"],
                "size_bytes": r["size_bytes"],
                "source": r["source"],
                "created_at": r["created_at_iso"],
                "text_preview": preview if preview else None
            })
        return results

    def get_latest_document_context(self) -> Optional[Dict[str, Any]]:
        """Returns the most recently uploaded document and its extracted text for LARA reasoning."""
        with self._get_conn() as conn:
            row = conn.execute("""
                SELECT file_id, filename, mime_type, extracted_text, created_at_iso
                FROM uploaded_files
                WHERE extracted_text IS NOT NULL AND length(extracted_text) > 0
                ORDER BY created_at DESC LIMIT 1
            """).fetchone()

        if not row:
            return None

        return {
            "file_id": row["file_id"],
            "filename": row["filename"],
            "mime_type": row["mime_type"],
            "extracted_text": row["extracted_text"],
            "created_at": row["created_at_iso"]
        }

storage_service = StorageService()
