# EVA Academic Research Agent Specification

## 1. Objective & Zero Hallucination Invariant
The Academic Research Agent discovers, parses, ranks, and synthesizes peer-reviewed scientific literature across multiple verified academic repositories.

> [!IMPORTANT]
> **Zero Hallucination Invariant**: The Research Agent NEVER fabricates papers, authors, publication years, abstracts, or DOI identifiers. Every citation returned must be traceable to a real publication.

---

## 2. Supported Academic Integrations

```
                               ┌────────────────────────────────┐
                               │     Research Agent Gateway     │
                               └───────────────┬────────────────┘
                                               │
       ┌───────────────────────┬───────────────┴───────┬───────────────────────┐
       ▼                       ▼                       ▼                       ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  arXiv API   │        │ OpenAlex API │        │Semantic Schol│        │ Crossref API │
│(Open Access) │        │(Acad. Graph) │        │ (Citations)  │        │ (DOI Engine) │
└──────────────┘        └──────────────┘        └──────────────┘        └──────────────┘
```

### 1. arXiv API (`export.arxiv.org/api/query`)
* **Access**: Open Access (No API key required).
* **Data Extracted**: Title, authors, abstract, arXiv ID, PDF direct link, publication date.

### 2. OpenAlex API (`api.openalex.org/works`)
* **Access**: Open Access with optional polite email header.
* **Data Extracted**: Global academic graph, primary publication location, citation count, DOI.

### 3. Semantic Scholar API (`api.semanticscholar.org/graph/v1`)
* **Access**: Public rate limit tier or authenticated with `SEMANTIC_SCHOLAR_API_KEY`.
* **Data Extracted**: Paper summary, field of study, citation impact, external identifiers.

### 4. Crossref Metadata API (`api.crossref.org/works`)
* **Access**: Public / Polite pool with `CROSSREF_EMAIL`.
* **Data Extracted**: Publisher DOIs, author family/given names, journal title, publication date.

---

## 3. Paper Deduplication & Relevance Ranking

1. **Title Normalization**: Lowercases and strips punctuation from titles to eliminate duplicate entries across repositories.
2. **Relevance Scoring**: Evaluates keyword overlap and query term frequency in title and abstract.
3. **Synthesis Generation**: Constructs structured, speech-friendly summaries highlighting the lead author, year of publication, and key contribution.

Example Output:
```json
{
  "status": "SUCCESS",
  "query": "Ergonomic Smart Wearables",
  "total_papers": 3,
  "summary": "Found 3 peer-reviewed papers on 'Ergonomic Smart Wearables'. Key paper: 'A Survey on Smart Glasses: Current Status, Challenges, and Opportunities' by Syed Fahad et al. (2023) [DOI: 10.1109/ACCESS.2023.3289012].",
  "papers": [
    {
      "title": "A Survey on Smart Glasses: Current Status, Challenges, and Opportunities",
      "authors": ["Syed Fahad", "Hui Chen", "David Zhang"],
      "published_date": "2023-08-15",
      "publication_year": "2023",
      "source": "IEEE Access / Verified",
      "doi": "10.1109/ACCESS.2023.3289012",
      "url": "https://doi.org/10.1109/ACCESS.2023.3289012",
      "pdf_url": "https://arxiv.org/pdf/2308.09123"
    }
  ]
}
```
