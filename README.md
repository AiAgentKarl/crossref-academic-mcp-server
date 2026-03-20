# Crossref Academic MCP Server

MCP Server that gives AI agents access to scientific papers, citations, and academic research data. Queries **Crossref**, **OpenAlex**, and **Semantic Scholar** — three major open academic APIs covering 150M+ research works.

No API keys required. All data sources are free and open.

## Tools

| Tool | Description |
|------|-------------|
| `search_papers` | Search for scientific papers across Crossref + OpenAlex simultaneously |
| `get_paper_details` | Get full metadata for a paper via DOI (bibliographic data + abstract + impact metrics) |
| `get_citations` | Find papers that cite a given paper (via Semantic Scholar) |
| `get_author_profile` | Look up an author's profile — publications, h-index, affiliations, research topics |
| `search_topics` | Find the most-cited recent papers in a topic area (trending research since 2023) |

## Installation

### With pip (recommended)

```bash
pip install crossref-academic-mcp-server
```

### From source

```bash
git clone https://github.com/AiAgentKarl/crossref-academic-mcp-server.git
cd crossref-academic-mcp-server
pip install -e .
```

## Configuration

Add to your MCP client config (e.g. Claude Desktop `claude_desktop_config.json`):

### Using pip install

```json
{
  "mcpServers": {
    "crossref-academic": {
      "command": "crossref-server"
    }
  }
}
```

### Using uvx (no install needed)

```json
{
  "mcpServers": {
    "crossref-academic": {
      "command": "uvx",
      "args": ["crossref-academic-mcp-server"]
    }
  }
}
```

## Example Usage

**Search for papers:**
> "Find recent papers about transformer architectures in NLP"

**Look up a specific paper:**
> "Get details for DOI 10.1038/s41586-021-03819-2"

**Explore citations:**
> "What papers cite the original attention paper?"

**Author lookup:**
> "Show me Yoshua Bengio's publication profile"

**Trending research:**
> "What are the most-cited papers about quantum computing from the last two years?"

## Data Sources

- **Crossref** — 150M+ metadata records, DOI resolution, bibliographic data
- **OpenAlex** — Open catalog of scholarly works, authors, institutions, topics
- **Semantic Scholar** — AI-powered citation analysis, abstracts, impact metrics

## License

MIT
