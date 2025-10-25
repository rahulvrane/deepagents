"""Middleware for scientific literature search and management."""

from collections.abc import Callable, Awaitable
from typing import Any
from typing_extensions import NotRequired, TypedDict

from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain_core.tools import BaseTool

from deepagents.tools.literature import (
    search_pubmed,
    search_arxiv,
    search_semantic_scholar,
    download_paper,
    parse_scientific_pdf,
    extract_references,
)


LITERATURE_SYSTEM_PROMPT = """## Literature Search Tools

You have access to scientific literature databases to search, retrieve, and analyze research papers.

### Available Tools

**Search Tools:**
- `search_pubmed(query, max_results, sort)`: Search PubMed database for biomedical literature
  - Query examples: "CRISPR gene editing", "machine learning[Title] AND protein"
  - Returns: PMID, title, authors, abstract, journal, publication date, DOI
  - Best for: Biomedical, life sciences, clinical research

- `search_arxiv(query, max_results, category)`: Search arXiv for preprints
  - Query examples: "quantum computing", "ti:transformer AND cat:cs.AI"
  - Categories: cs.AI, cs.LG, q-bio.GN, physics.bio-ph, etc.
  - Returns: arXiv ID, title, authors, abstract, categories, PDF URL
  - Best for: Physics, mathematics, computer science, quantitative biology

- `search_semantic_scholar(query, max_results, fields, year_range)`: Search across all disciplines
  - Query examples: "neural networks protein folding", "climate change machine learning"
  - Returns: Citation counts, influential citations, open access PDFs
  - Best for: Cross-disciplinary search, finding highly cited papers

**PDF Tools:**
- `download_paper(paper_id, source)`: Download paper PDF to /papers/ directory
  - Sources: "arxiv", "pubmed", "doi", "url", "auto"
  - Examples: download_paper("2301.12345", "arxiv")

- `parse_scientific_pdf(file_path, extract_sections)`: Extract text and structure from PDF
  - Returns: Full text, metadata, sections (abstract, intro, methods, results, discussion)
  - Example: parse_scientific_pdf("/papers/2301.12345.pdf")

- `extract_references(file_path)`: Extract bibliography from paper
  - Returns: List of reference citations

### Best Practices

**When Searching:**
1. Use multiple databases for comprehensive coverage
   - PubMed for biomedical/clinical
   - arXiv for physics/CS/math preprints
   - Semantic Scholar for cross-disciplinary and citation metrics

2. Start broad, then refine
   - Initial search with general terms
   - Review results and refine query
   - Use field-specific tags for precision

3. Consider recency
   - Use year filters for recent research
   - Check publication dates in results
   - arXiv often has latest preprints

**When Organizing Papers:**
1. Download and store papers in `/papers/` directory
   - Use consistent naming: arxiv_2301.12345.pdf, PMID_12345678.pdf

2. Keep a summary file at `/literature_review_summary.md`
   - Document search queries used
   - Note key findings from each paper
   - Track papers by topic or theme

3. Maintain citation library at `/references/library.bib`
   - Add all papers you reference
   - Use consistent citation keys

**Literature Review Workflow:**
1. Define research question and search strategy
2. Search multiple databases (PubMed, arXiv, Semantic Scholar)
3. Download relevant papers to `/papers/`
4. Parse PDFs to extract text and sections
5. Read abstracts and methods to assess relevance
6. Extract key findings and add to summary
7. Extract references to find additional papers
8. Synthesize findings across papers

### Tips

- Use Boolean operators (AND, OR, NOT) for precise queries
- Combine databases: PubMed for clinical + arXiv for computational methods
- Check citation counts on Semantic Scholar to find influential papers
- Look for open access PDFs (arXiv, Semantic Scholar openAccessPdf field)
- Extract references from key papers to find related work
- Document all search queries for reproducibility

### Example Workflow

```
# 1. Search multiple databases
pubmed_results = search_pubmed("CRISPR cancer therapy", max_results=20)
arxiv_results = search_arxiv("CRISPR", category="q-bio.GN", max_results=10)
s2_results = search_semantic_scholar("CRISPR applications", max_results=15)

# 2. Download key papers
download_paper("2301.12345", "arxiv")
download_paper("PMC8234567", "pubmed")

# 3. Parse and analyze
paper = parse_scientific_pdf("/papers/2301.12345.pdf", extract_sections=True)
# Review abstract, methods, results

# 4. Extract references for more papers
refs = extract_references("/papers/2301.12345.pdf")

# 5. Update summary
# Add findings to /literature_review_summary.md
```

Remember: Always cite sources properly and respect copyright. Use open access sources when available.
"""


class LiteratureSearchState(AgentState):
    """Extended state for literature search functionality."""

    papers: NotRequired[dict[str, Any]]
    """Dictionary of downloaded papers and metadata."""


class LiteratureSearchMiddleware(AgentMiddleware):
    """Middleware for scientific literature search and retrieval.

    Provides tools for searching scientific databases (PubMed, arXiv,
    Semantic Scholar), downloading papers, and extracting information
    from scientific PDFs.

    Args:
        system_prompt: Optional custom system prompt override.
        enable_pubmed: Whether to enable PubMed search (default: True).
        enable_arxiv: Whether to enable arXiv search (default: True).
        enable_semantic_scholar: Whether to enable Semantic Scholar (default: True).
        enable_pdf_download: Whether to enable PDF download (default: True).
        enable_pdf_parsing: Whether to enable PDF parsing (default: True).

    Example:
        ```python
        from deepagents.middleware.scientific import LiteratureSearchMiddleware
        from deepagents import create_deep_agent

        # Basic usage
        agent = create_deep_agent(
            middleware=[LiteratureSearchMiddleware()]
        )

        # Custom configuration
        agent = create_deep_agent(
            middleware=[
                LiteratureSearchMiddleware(
                    enable_pubmed=True,
                    enable_arxiv=True,
                    enable_semantic_scholar=True,
                )
            ]
        )

        # Use the agent
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": "Search for recent papers on CRISPR gene editing in cancer therapy"
            }]
        })
        ```
    """

    state_schema = LiteratureSearchState

    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        enable_pubmed: bool = True,
        enable_arxiv: bool = True,
        enable_semantic_scholar: bool = True,
        enable_pdf_download: bool = True,
        enable_pdf_parsing: bool = True,
    ) -> None:
        """Initialize literature search middleware."""
        super().__init__()
        self.system_prompt = system_prompt or LITERATURE_SYSTEM_PROMPT

        # Build tool list based on enabled features
        self.tools: list[BaseTool] = []

        if enable_pubmed:
            self.tools.append(search_pubmed)

        if enable_arxiv:
            self.tools.append(search_arxiv)

        if enable_semantic_scholar:
            self.tools.append(search_semantic_scholar)

        if enable_pdf_download:
            self.tools.append(download_paper)

        if enable_pdf_parsing:
            self.tools.extend([
                parse_scientific_pdf,
                extract_references,
            ])

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Add literature search instructions to system prompt."""
        if self.system_prompt is not None:
            request.system_prompt = (
                request.system_prompt + "\n\n" + self.system_prompt
                if request.system_prompt
                else self.system_prompt
            )
        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """(async) Add literature search instructions to system prompt."""
        if self.system_prompt is not None:
            request.system_prompt = (
                request.system_prompt + "\n\n" + self.system_prompt
                if request.system_prompt
                else self.system_prompt
            )
        return await handler(request)
