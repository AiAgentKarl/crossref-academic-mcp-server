"""
Async HTTP-Clients für akademische APIs:
- Crossref (Metadaten, DOI-Lookup)
- OpenAlex (Autoren, Trending Topics)
- Semantic Scholar (Zitationen)
"""

import httpx
from typing import Any


# Gemeinsame Timeout-Einstellungen
TIMEOUT = httpx.Timeout(30.0, connect=10.0)

# Polite-Pool Header für Crossref (bessere Rate-Limits)
CROSSREF_HEADERS = {
    "User-Agent": "CrossrefAcademicMCP/0.1.0 (mailto:coach1916@gmail.com)",
    "Accept": "application/json",
}

SEMANTIC_SCHOLAR_HEADERS = {
    "Accept": "application/json",
}

OPENALEX_HEADERS = {
    "User-Agent": "CrossrefAcademicMCP/0.1.0 (mailto:coach1916@gmail.com)",
    "Accept": "application/json",
}


# --- Crossref API ---

async def crossref_search(query: str, limit: int = 10) -> dict[str, Any]:
    """Suche nach Papers über Crossref."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            "https://api.crossref.org/works",
            params={
                "query": query,
                "rows": min(limit, 50),
                "sort": "relevance",
                "order": "desc",
            },
            headers=CROSSREF_HEADERS,
        )
        response.raise_for_status()
        return response.json()


async def crossref_get_work(doi: str) -> dict[str, Any]:
    """Hole Detail-Metadaten eines Papers via DOI."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"https://api.crossref.org/works/{doi}",
            headers=CROSSREF_HEADERS,
        )
        response.raise_for_status()
        return response.json()


# --- Semantic Scholar API ---

async def semantic_scholar_citations(doi: str, limit: int = 10) -> dict[str, Any]:
    """Hole Zitationen eines Papers über Semantic Scholar."""
    paper_id = f"DOI:{doi}"
    fields = "title,authors,year,citationCount,externalIds,url"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations",
            params={
                "fields": fields,
                "limit": min(limit, 100),
            },
            headers=SEMANTIC_SCHOLAR_HEADERS,
        )
        response.raise_for_status()
        return response.json()


async def semantic_scholar_paper(doi: str) -> dict[str, Any]:
    """Hole Paper-Details über Semantic Scholar."""
    paper_id = f"DOI:{doi}"
    fields = (
        "title,authors,year,abstract,citationCount,"
        "referenceCount,influentialCitationCount,"
        "fieldsOfStudy,externalIds,url,venue,openAccessPdf"
    )
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}",
            params={"fields": fields},
            headers=SEMANTIC_SCHOLAR_HEADERS,
        )
        response.raise_for_status()
        return response.json()


# --- OpenAlex API ---

async def openalex_search(query: str, limit: int = 10) -> dict[str, Any]:
    """Suche nach Papers über OpenAlex."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            "https://api.openalex.org/works",
            params={
                "search": query,
                "per_page": min(limit, 50),
                "sort": "relevance_score:desc",
                "mailto": "coach1916@gmail.com",
            },
            headers=OPENALEX_HEADERS,
        )
        response.raise_for_status()
        return response.json()


async def openalex_author_search(name: str) -> dict[str, Any]:
    """Suche nach einem Autor über OpenAlex."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            "https://api.openalex.org/authors",
            params={
                "search": name,
                "per_page": 5,
                "mailto": "coach1916@gmail.com",
            },
            headers=OPENALEX_HEADERS,
        )
        response.raise_for_status()
        return response.json()


async def openalex_topic_works(topic: str, limit: int = 10) -> dict[str, Any]:
    """Suche nach trending Papers zu einem Thema über OpenAlex."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            "https://api.openalex.org/works",
            params={
                "search": topic,
                "per_page": min(limit, 50),
                "sort": "cited_by_count:desc",
                "filter": "from_publication_date:2023-01-01",
                "mailto": "coach1916@gmail.com",
            },
            headers=OPENALEX_HEADERS,
        )
        response.raise_for_status()
        return response.json()
