"""
MCP-Tools für akademische Recherche:
- Paper-Suche (Crossref + OpenAlex)
- DOI-Lookup mit Detail-Metadaten
- Zitationsanalyse
- Autoren-Profile
- Trending Topics
"""

from mcp.server.fastmcp import FastMCP
from src.clients.crossref import (
    crossref_search,
    crossref_get_work,
    semantic_scholar_citations,
    semantic_scholar_paper,
    openalex_search,
    openalex_author_search,
    openalex_topic_works,
)


def _format_crossref_item(item: dict) -> dict:
    """Crossref-Work-Item in einheitliches Format bringen."""
    authors = []
    for a in item.get("author", []):
        name_parts = []
        if a.get("given"):
            name_parts.append(a["given"])
        if a.get("family"):
            name_parts.append(a["family"])
        if name_parts:
            authors.append(" ".join(name_parts))

    # Datum extrahieren
    date_parts = item.get("published", {}).get("date-parts", [[]])
    year = date_parts[0][0] if date_parts and date_parts[0] else None

    return {
        "title": (item.get("title") or ["Unbekannt"])[0],
        "authors": authors,
        "year": year,
        "doi": item.get("DOI"),
        "type": item.get("type"),
        "journal": (item.get("container-title") or [None])[0],
        "citation_count": item.get("is-referenced-by-count", 0),
        "url": item.get("URL"),
    }


def _format_openalex_item(item: dict) -> dict:
    """OpenAlex-Work-Item in einheitliches Format bringen."""
    authors = []
    for authorship in item.get("authorships", []):
        author = authorship.get("author", {})
        if author.get("display_name"):
            authors.append(author["display_name"])

    return {
        "title": item.get("title", "Unbekannt"),
        "authors": authors,
        "year": item.get("publication_year"),
        "doi": (item.get("doi") or "").replace("https://doi.org/", ""),
        "type": item.get("type"),
        "journal": (item.get("primary_location") or {}).get("source", {}).get("display_name") if item.get("primary_location") else None,
        "citation_count": item.get("cited_by_count", 0),
        "open_access": item.get("open_access", {}).get("is_oa", False),
        "url": item.get("doi"),
    }


def register_tools(mcp: FastMCP):
    """Registriert alle akademischen Tools beim MCP-Server."""

    @mcp.tool()
    async def search_papers(query: str, limit: int = 10) -> dict:
        """
        Suche nach wissenschaftlichen Papers über Crossref und OpenAlex.

        Durchsucht zwei große akademische Datenbanken gleichzeitig und
        kombiniert die Ergebnisse. Ideal für Literaturrecherche.

        Args:
            query: Suchbegriff(e), z.B. "machine learning healthcare"
            limit: Maximale Anzahl Ergebnisse pro Quelle (Standard: 10, Max: 50)
        """
        limit = max(1, min(limit, 50))
        errors = []

        # Crossref-Ergebnisse
        crossref_results = []
        try:
            cr_data = await crossref_search(query, limit)
            items = cr_data.get("message", {}).get("items", [])
            crossref_results = [_format_crossref_item(item) for item in items]
        except Exception as e:
            errors.append(f"Crossref-Fehler: {str(e)}")

        # OpenAlex-Ergebnisse
        openalex_results = []
        try:
            oa_data = await openalex_search(query, limit)
            items = oa_data.get("results", [])
            openalex_results = [_format_openalex_item(item) for item in items]
        except Exception as e:
            errors.append(f"OpenAlex-Fehler: {str(e)}")

        return {
            "query": query,
            "crossref": {
                "count": len(crossref_results),
                "results": crossref_results,
            },
            "openalex": {
                "count": len(openalex_results),
                "results": openalex_results,
            },
            "total_results": len(crossref_results) + len(openalex_results),
            "errors": errors if errors else None,
        }

    @mcp.tool()
    async def get_paper_details(doi: str) -> dict:
        """
        Hole vollständige Metadaten eines Papers via DOI.

        Kombiniert Daten aus Crossref (bibliographisch) und
        Semantic Scholar (Abstract, Einfluss-Metriken).

        Args:
            doi: Digital Object Identifier, z.B. "10.1038/s41586-021-03819-2"
        """
        # DOI bereinigen
        doi = doi.strip()
        if doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")
        if doi.startswith("http://doi.org/"):
            doi = doi.replace("http://doi.org/", "")

        result = {"doi": doi}
        errors = []

        # Crossref-Details
        try:
            cr_data = await crossref_get_work(doi)
            item = cr_data.get("message", {})
            result["crossref"] = _format_crossref_item(item)

            # Zusätzliche Details aus Crossref
            result["crossref"]["abstract"] = item.get("abstract")
            result["crossref"]["publisher"] = item.get("publisher")
            result["crossref"]["issn"] = item.get("ISSN")
            result["crossref"]["subject"] = item.get("subject")
            result["crossref"]["license"] = [
                lic.get("URL") for lic in item.get("license", [])
            ] or None
            result["crossref"]["reference_count"] = item.get("references-count", 0)
            result["crossref"]["funder"] = [
                {"name": f.get("name"), "doi": f.get("DOI")}
                for f in item.get("funder", [])
            ] or None
        except Exception as e:
            errors.append(f"Crossref-Fehler: {str(e)}")

        # Semantic Scholar Ergänzung
        try:
            ss_data = await semantic_scholar_paper(doi)
            result["semantic_scholar"] = {
                "title": ss_data.get("title"),
                "abstract": ss_data.get("abstract"),
                "year": ss_data.get("year"),
                "citation_count": ss_data.get("citationCount", 0),
                "reference_count": ss_data.get("referenceCount", 0),
                "influential_citations": ss_data.get("influentialCitationCount", 0),
                "fields_of_study": ss_data.get("fieldsOfStudy"),
                "venue": ss_data.get("venue"),
                "open_access_pdf": (ss_data.get("openAccessPdf") or {}).get("url"),
                "url": ss_data.get("url"),
            }
        except Exception as e:
            errors.append(f"Semantic Scholar-Fehler: {str(e)}")

        if errors:
            result["errors"] = errors

        return result

    @mcp.tool()
    async def get_citations(doi: str, limit: int = 10) -> dict:
        """
        Finde Papers, die ein bestimmtes Paper zitieren.

        Nutzt Semantic Scholar für Zitationsanalyse. Zeigt welche
        neueren Arbeiten auf einem Paper aufbauen.

        Args:
            doi: DOI des Quell-Papers, z.B. "10.1038/s41586-021-03819-2"
            limit: Maximale Anzahl Zitationen (Standard: 10, Max: 100)
        """
        doi = doi.strip()
        if doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")
        if doi.startswith("http://doi.org/"):
            doi = doi.replace("http://doi.org/", "")

        limit = max(1, min(limit, 100))

        try:
            data = await semantic_scholar_citations(doi, limit)

            citations = []
            for entry in data.get("data", []):
                citing = entry.get("citingPaper", {})
                authors = [
                    a.get("name", "Unbekannt")
                    for a in citing.get("authors", [])
                ]
                ext_ids = citing.get("externalIds", {})

                citations.append({
                    "title": citing.get("title"),
                    "authors": authors,
                    "year": citing.get("year"),
                    "citation_count": citing.get("citationCount", 0),
                    "doi": ext_ids.get("DOI"),
                    "url": citing.get("url"),
                })

            return {
                "doi": doi,
                "citations_found": len(citations),
                "citations": citations,
            }
        except Exception as e:
            return {
                "doi": doi,
                "error": str(e),
                "citations": [],
            }

    @mcp.tool()
    async def get_author_profile(name: str) -> dict:
        """
        Suche nach einem Autor und zeige Profil-Informationen.

        Nutzt OpenAlex für Autoren-Daten inkl. Publikationszahlen,
        Zitationsmetriken und Forschungsgebiete.

        Args:
            name: Name des Autors, z.B. "Yoshua Bengio"
        """
        try:
            data = await openalex_author_search(name)
            results = data.get("results", [])

            if not results:
                return {
                    "query": name,
                    "found": False,
                    "message": f"Kein Autor gefunden für '{name}'",
                }

            authors = []
            for author in results:
                # Top-Konzepte extrahieren
                topics = []
                for topic in (author.get("topics") or [])[:5]:
                    topics.append({
                        "name": topic.get("display_name"),
                        "count": topic.get("count", 0),
                    })

                # Letzte bekannte Affiliation
                affiliations = []
                for aff in (author.get("affiliations") or [])[:3]:
                    inst = aff.get("institution", {})
                    if inst.get("display_name"):
                        affiliations.append({
                            "institution": inst["display_name"],
                            "country": inst.get("country_code"),
                            "type": inst.get("type"),
                        })

                authors.append({
                    "name": author.get("display_name"),
                    "openalex_id": author.get("id"),
                    "orcid": author.get("orcid"),
                    "works_count": author.get("works_count", 0),
                    "citation_count": author.get("cited_by_count", 0),
                    "h_index": (author.get("summary_stats") or {}).get("h_index", 0),
                    "i10_index": (author.get("summary_stats") or {}).get("i10_index", 0),
                    "topics": topics,
                    "affiliations": affiliations,
                })

            return {
                "query": name,
                "found": True,
                "count": len(authors),
                "authors": authors,
            }
        except Exception as e:
            return {
                "query": name,
                "error": str(e),
            }

    @mcp.tool()
    async def search_topics(topic: str, limit: int = 10) -> dict:
        """
        Finde die meistzitierten neueren Papers zu einem Thema.

        Sucht über OpenAlex nach Papers seit 2023, sortiert nach
        Zitationszahl. Ideal um Trend-Themen zu erkunden.

        Args:
            topic: Themengebiet, z.B. "large language models", "CRISPR"
            limit: Maximale Anzahl Ergebnisse (Standard: 10, Max: 50)
        """
        limit = max(1, min(limit, 50))

        try:
            data = await openalex_topic_works(topic, limit)
            results = data.get("results", [])

            papers = []
            for item in results:
                papers.append(_format_openalex_item(item))

            return {
                "topic": topic,
                "count": len(papers),
                "note": "Sortiert nach Zitationszahl, Papers seit 2023",
                "papers": papers,
            }
        except Exception as e:
            return {
                "topic": topic,
                "error": str(e),
                "papers": [],
            }
