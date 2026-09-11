import io
import tempfile
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.storage_service import StorageService

client = TestClient(app)

def test_storage_service_save_and_retrieve_txt():
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = StorageService(storage_dir=tmp_dir, db_path=":memory:")
        
        test_content = b"Candidate Name: Yash Anand\nSkills: Python, ESP32, BLE, Embedded AI\nExperience: Smart Glasses Developer."
        res = storage.save_file(
            file_bytes=test_content,
            filename="Yash_Resume.txt",
            content_type="text/plain",
            source="web"
        )

        assert res["file_id"].startswith("file_")
        assert res["filename"] == "Yash_Resume.txt"
        assert res["size_bytes"] == len(test_content)
        assert res["has_extracted_text"] is True

        # Retrieve metadata
        meta = storage.get_file(res["file_id"])
        assert meta is not None
        assert "Yash Anand" in meta["extracted_text"]

        # Retrieve raw bytes
        raw_data, fname, mime = storage.get_file_bytes(res["file_id"])
        assert raw_data == test_content
        assert fname == "Yash_Resume.txt"
        assert mime == "text/plain"

        # Delete
        deleted = storage.delete_file(res["file_id"])
        assert deleted is True
        assert storage.get_file(res["file_id"]) is None

def test_storage_path_traversal_protection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = StorageService(storage_dir=tmp_dir, db_path=":memory:")
        
        # Attempt path traversal in filename
        malicious_filename = "../../../etc/passwd.txt"
        res = storage.save_file(
            file_bytes=b"root:x:0:0:root:/root:/bin/bash",
            filename=malicious_filename,
            content_type="text/plain"
        )

        # Sanitized filename should NOT contain directory traversal
        assert ".." not in res["filename"]
        assert "/" not in res["filename"]
        assert "\\" not in res["filename"]
        assert res["filename"] == "passwd.txt"

def test_storage_file_size_limit():
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = StorageService(storage_dir=tmp_dir, db_path=":memory:")
        
        # 25 MB payload (exceeds 20MB limit)
        large_payload = b"X" * (25 * 1024 * 1024)
        with pytest.raises(ValueError, match="exceeds maximum allowed limit"):
            storage.save_file(
                file_bytes=large_payload,
                filename="large_file.pdf",
                content_type="application/pdf"
            )

def test_api_upload_and_download_flow():
    # 1. Upload TXT Document
    test_text = "Project Specifications: LARA Smart Glasses Context Engine v1.0. High performance BLE and Audio."
    files = {"file": ("project_spec.txt", io.BytesIO(test_text.encode("utf-8")), "text/plain")}
    data = {"source": "web"}
    
    resp = client.post("/api/v1/files/upload", files=files, data=data)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["success"] is True
    file_id = res_data["file_id"]

    # 2. Get Metadata
    get_resp = client.get(f"/api/v1/files/{file_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["filename"] == "project_spec.txt"

    # 3. Download File
    dl_resp = client.get(f"/api/v1/files/{file_id}/download")
    assert dl_resp.status_code == 200
    assert dl_resp.content.decode("utf-8") == test_text

    # 4. List Files
    list_resp = client.get("/api/v1/files")
    assert list_resp.status_code == 200
    assert any(f["file_id"] == file_id for f in list_resp.json()["files"])

    # 5. Delete File
    del_resp = client.delete(f"/api/v1/files/{file_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True

def test_structured_error_contract():
    # Trigger 404
    resp = client.get("/api/v1/files/non_existent_file_9999")
    assert resp.status_code == 404
    err_json = resp.json()
    assert err_json["success"] is False
    assert "error_code" in err_json
    assert "message" in err_json
    assert "retryable" in err_json
