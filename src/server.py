"""
Crossref Academic MCP Server

Gibt AI-Agents Zugriff auf wissenschaftliche Paper-Datenbanken:
Crossref, OpenAlex und Semantic Scholar.
"""

from mcp.server.fastmcp import FastMCP
from src.tools.academic import register_tools

mcp = FastMCP(
    "Crossref Academic",
    instructions=(
        "MCP-Server für wissenschaftliche Recherche. "
        "Durchsuche Millionen akademischer Papers über Crossref und OpenAlex. "
        "Finde Paper-Details via DOI, analysiere Zitationsnetzwerke über Semantic Scholar, "
        "erkunde Autoren-Profile und entdecke Trend-Themen in der Forschung. "
        "Alle APIs sind kostenlos und benötigen keine API-Keys."
    ),
)

# Tools registrieren
register_tools(mcp)


def main():
    """Startet den MCP-Server über stdio-Transport."""
    mcp.run()


if __name__ == "__main__":
    main()
