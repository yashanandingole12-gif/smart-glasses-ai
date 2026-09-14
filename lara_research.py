"""
LARA — Research Engine (Phase 1)
================================
A multilingual academic-paper search module. This is the "brain" that a
mobile/wearable app, a web app, or a desktop app can all call into later —
right now it runs as a CLI / importable Python library.

WHAT IT DOES
------------
1. Takes a research query in ANY language.
2. Detects the language and translates it to English (most academic
   databases index metadata in English).
3. Searches four free academic sources in parallel-ish fashion:
      - arXiv            (no key needed)
      - Semantic Scholar  (works without a key; optional key = higher rate limit)
      - CrossRef          (no key needed, just a polite email header)
      - PubMed / NCBI     (no key needed; optional key = higher rate limit)
4. Merges + de-duplicates results by DOI/title similarity.
5. Prints/returns a unified, ranked list: title, authors, year, abstract,
   source, and link.

API KEYS — WHERE TO GET THEM (all free)
----------------------------------------
- SEMANTIC_SCHOLAR_API_KEY : https://www.semanticscholar.org/product/api  (optional, raises rate limit)
- NCBI_API_KEY             : https://www.ncbi.nlm.nih.gov/account/settings/ (optional, raises rate limit)
- CROSSREF_MAILTO          : just your email, no signup — CrossRef asks for it to be polite to their servers.
- arXiv needs NO key at all.

Set these as environment variables (see .env.example generated alongside this file).
No paid/private API key is required for academic search — if anyone tries
to sell you a "research API key," it's not needed for this use case.

USAGE
-----
    python lara_research.py "quantum computing error correction" --lang auto --limit 10
    python lara_research.py "प्रकाश संश्लेषण के नए तरीके" --limit 5      # Hindi query works too

Or import it:
    from lara_research import LaraResearch
    lara = LaraResearch()
    results = lara.search("CRISPR gene editing off-target effects", limit=10)
"""

import os
import re
import time
import json
import argparse
import concurrent.futures as cf
from dataclasses import dataclass, field, asdict
from typing import List, Optional

import requests

try:
    from langdetect import detect
except ImportError:
    def detect(text: str) -> str:
        return "en"

try:
    from deep_translator import GoogleTranslator
except ImportError:
    class GoogleTranslator:
        def __init__(self, source="auto", target="en"):
            self.source = source
            self.target = target
        def translate(self, text: str) -> str:
            return text


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Paper:
    title: str
    authors: List[str]
    year: Optional[int]
    abstract: str
    source: str
    url: str
    doi: Optional[str] = None
    score: float = 0.0  # simple relevance/recency heuristic

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------------------
# Language handling
# ---------------------------------------------------------------------------

class LanguageBridge:
    """Detects query language and translates to/from English so a person can
    search in Hindi, Spanish, Mandarin, etc. and still hit English-indexed
    academic databases."""

    @staticmethod
    def detect_lang(text: str) -> str:
        try:
            return detect(text)
        except Exception:
            return "en"

    @staticmethod
    def to_english(text: str, source_lang: str) -> str:
        if source_lang == "en":
            return text
        try:
            return GoogleTranslator(source=source_lang, target="en").translate(text)
        except Exception:
            return text  # fall back to original if translation fails

    @staticmethod
    def translate_back(text: str, target_lang: str) -> str:
        if target_lang == "en" or not text:
            return text
        try:
            return GoogleTranslator(source="en", target=target_lang).translate(text)
        except Exception:
            return text


# ---------------------------------------------------------------------------
# Individual source connectors
# ---------------------------------------------------------------------------

class ArxivConnector:
    BASE = "https://export.arxiv.org/api/query"

    def search(self, query: str, limit: int) -> List[Paper]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
        }
        headers = {"User-Agent": "LARA-Academic-Research/1.0 (https://smartglasses.ai; mailto:research@smartglasses.ai)"}
        try:
            resp = requests.get(self.BASE, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.RequestException:
            return []

        import xml.etree.ElementTree as ET
        ns = {"a": "http://www.w3.org/2005/Atom"}
        try:
            root = ET.fromstring(resp.text)
        except Exception:
            return []
        papers = []
        for entry in root.findall("a:entry", ns):
            title = entry.findtext("a:title", default="", namespaces=ns).strip()
            summary = entry.findtext("a:summary", default="", namespaces=ns).strip()
            published = entry.findtext("a:published", default="", namespaces=ns)
            year = int(published[:4]) if published else None
            authors = [a.findtext("a:name", default="", namespaces=ns)
                       for a in entry.findall("a:author", ns)]
            link = entry.findtext("a:id", default="", namespaces=ns)
            papers.append(Paper(title=title, authors=authors, year=year,
                                 abstract=summary, source="arXiv", url=link))
        return papers


class SemanticScholarConnector:
    BASE = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self):
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    def search(self, query: str, limit: int) -> List[Paper]:
        headers = {"User-Agent": "LARA-Academic-Research/1.0 (mailto:research@smartglasses.ai)"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,year,authors,externalIds,url",
        }
        try:
            resp = requests.get(self.BASE, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.RequestException:
            return []

        data = resp.json().get("data", [])
        papers = []
        for item in data:
            authors = [a.get("name", "") for a in item.get("authors", [])]
            doi = (item.get("externalIds") or {}).get("DOI")
            papers.append(Paper(
                title=item.get("title") or "",
                authors=authors,
                year=item.get("year"),
                abstract=item.get("abstract") or "",
                source="Semantic Scholar",
                url=item.get("url") or "",
                doi=doi,
            ))
        return papers


class CrossrefConnector:
    BASE = "https://api.crossref.org/works"

    def __init__(self):
        self.mailto = os.getenv("CROSSREF_MAILTO", "researcher@example.com")

    def search(self, query: str, limit: int) -> List[Paper]:
        params = {"query": query, "rows": limit, "mailto": self.mailto}
        headers = {"User-Agent": f"LARA-Academic-Research/1.0 (mailto:{self.mailto})"}
        try:
            resp = requests.get(self.BASE, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.RequestException:
            return []

        items = resp.json().get("message", {}).get("items", [])
        papers = []
        for item in items:
            title = (item.get("title") or [""])[0]
            authors = [f"{a.get('given','')} {a.get('family','')}".strip()
                       for a in item.get("author", [])] if item.get("author") else []
            year = None
            date_parts = item.get("issued", {}).get("date-parts", [[None]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]
            papers.append(Paper(
                title=title,
                authors=authors,
                year=year,
                abstract=item.get("abstract", "") or "",
                source="CrossRef",
                url=item.get("URL", ""),
                doi=item.get("DOI"),
            ))
        return papers


class PubMedConnector:
    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self):
        self.api_key = os.getenv("NCBI_API_KEY")

    def search(self, query: str, limit: int) -> List[Paper]:
        params = {"db": "pubmed", "term": query, "retmax": limit, "retmode": "json"}
        headers = {"User-Agent": "LARA-Academic-Research/1.0 (mailto:research@smartglasses.ai)"}
        if self.api_key:
            params["api_key"] = self.api_key
        try:
            resp = requests.get(self.SEARCH_URL, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            ids = resp.json().get("esearchresult", {}).get("idlist", [])
        except requests.RequestException:
            return []

        if not ids:
            return []

        sum_params = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        if self.api_key:
            sum_params["api_key"] = self.api_key
        try:
            resp = requests.get(self.SUMMARY_URL, params=sum_params, headers=headers, timeout=15)
            resp.raise_for_status()
            result = resp.json().get("result", {})
        except requests.RequestException:
            return []

        papers = []
        for pmid in ids:
            item = result.get(pmid, {})
            if not item:
                continue
            authors = [a.get("name", "") for a in item.get("authors", [])]
            year = None
            pubdate = item.get("pubdate", "")
            m = re.search(r"\d{4}", pubdate)
            if m:
                year = int(m.group())
            papers.append(Paper(
                title=item.get("title", ""),
                authors=authors,
                year=year,
                abstract="",  # esummary doesn't include abstract; efetch would be needed
                source="PubMed",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                doi=item.get("elocationid"),
            ))
        return papers


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class LaraResearch:
    def __init__(self):
        self.connectors = {
            "arxiv": ArxivConnector(),
            "semantic_scholar": SemanticScholarConnector(),
            "crossref": CrossrefConnector(),
            "pubmed": PubMedConnector(),
        }
        self.lang_bridge = LanguageBridge()

    def search(self, query: str, limit: int = 10, sources: Optional[List[str]] = None,
               translate_results_back: bool = False) -> List[Paper]:
        """
        query: research question/topic in any language
        limit: max results PER source before merging
        sources: subset of ['arxiv','semantic_scholar','crossref','pubmed']; None = all
        translate_results_back: if True, translate titles/abstracts back to the
                                 original query language
        """
        source_lang = self.lang_bridge.detect_lang(query)
        english_query = self.lang_bridge.to_english(query, source_lang)

        active = sources or list(self.connectors.keys())
        all_papers: List[Paper] = []

        with cf.ThreadPoolExecutor(max_workers=len(active)) as executor:
            futures = {
                executor.submit(self.connectors[name].search, english_query, limit): name
                for name in active if name in self.connectors
            }
            for future in cf.as_completed(futures):
                try:
                    all_papers.extend(future.result())
                except Exception as e:
                    pass

        deduped = self._dedupe(all_papers)
        ranked = self._rank(deduped, english_query)

        if translate_results_back and source_lang != "en":
            for p in ranked:
                p.title = self.lang_bridge.translate_back(p.title, source_lang)
                p.abstract = self.lang_bridge.translate_back(p.abstract, source_lang)

        return ranked

    @staticmethod
    def _dedupe(papers: List[Paper]) -> List[Paper]:
        seen_dois = set()
        seen_titles = set()
        unique = []
        for p in papers:
            key_doi = p.doi.lower() if p.doi else None
            key_title = re.sub(r"[^a-z0-9]", "", p.title.lower())[:80]
            if key_doi and key_doi in seen_dois:
                continue
            if key_title and key_title in seen_titles:
                continue
            if key_doi:
                seen_dois.add(key_doi)
            seen_titles.add(key_title)
            unique.append(p)
        return unique

    @staticmethod
    def _rank(papers: List[Paper], query: str) -> List[Paper]:
        terms = set(re.findall(r"\w+", query.lower()))
        for p in papers:
            text = (p.title + " " + p.abstract).lower()
            overlap = sum(1 for t in terms if t in text)
            recency = (p.year or 2000) / 2100.0
            p.score = overlap + recency
        return sorted(papers, key=lambda p: p.score, reverse=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LARA — multilingual academic research search")
    parser.add_argument("query", help="Research topic/question, any language")
    parser.add_argument("--limit", type=int, default=8, help="Results per source before merge")
    parser.add_argument("--sources", nargs="*", default=None,
                         choices=["arxiv", "semantic_scholar", "crossref", "pubmed"])
    parser.add_argument("--translate-back", action="store_true",
                         help="Translate result titles/abstracts back to query language")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of pretty text")
    args = parser.parse_args()

    lara = LaraResearch()
    results = lara.search(args.query, limit=args.limit, sources=args.sources,
                           translate_results_back=args.translate_back)

    if args.json:
        print(json.dumps([p.to_dict() for p in results], indent=2, ensure_ascii=False))
        return

    print(f"\nLARA found {len(results)} unique papers for: \"{args.query}\"\n" + "-" * 60)
    for i, p in enumerate(results, 1):
        authors = ", ".join(p.authors[:3]) + (" et al." if len(p.authors) > 3 else "")
        print(f"{i}. {p.title}  [{p.source}, {p.year or 'n.d.'}]")
        if authors:
            print(f"   Authors: {authors}")
        if p.abstract:
            snippet = p.abstract[:220].replace("\n", " ")
            print(f"   Abstract: {snippet}{'...' if len(p.abstract) > 220 else ''}")
        print(f"   Link: {p.url}")
        print()


if __name__ == "__main__":
    main()
