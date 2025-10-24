# Co-Scientist Agent System: Implementation Plan

## Overview

This document provides a detailed, actionable implementation plan for transforming DeepAgents into a Co-Scientist Agent System. It includes specific code examples, file structure, and step-by-step instructions.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Phase 1: Foundation - Scientific Middleware](#phase-1-foundation---scientific-middleware)
3. [Phase 2: Specialized Subagents](#phase-2-specialized-subagents)
4. [Phase 3: Domain-Specific Tools](#phase-3-domain-specific-tools)
5. [Testing Strategy](#testing-strategy)
6. [Deployment](#deployment)

---

## Project Structure

```
deepagents/
├── src/deepagents/
│   ├── __init__.py
│   ├── graph.py                              # Existing
│   ├── co_scientist.py                       # NEW: Co-scientist factory
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── filesystem.py                     # Existing
│   │   ├── subagents.py                      # Existing
│   │   ├── patch_tool_calls.py               # Existing
│   │   ├── scientific/                       # NEW: Scientific middleware
│   │   │   ├── __init__.py
│   │   │   ├── literature.py                 # Literature search middleware
│   │   │   ├── data_analysis.py              # Data analysis middleware
│   │   │   ├── visualization.py              # Visualization middleware
│   │   │   ├── citation.py                   # Citation management middleware
│   │   │   ├── experimental_design.py        # Experimental design middleware
│   │   │   ├── writing.py                    # Scientific writing middleware
│   │   │   └── domains/                      # Domain-specific middleware
│   │   │       ├── __init__.py
│   │   │       ├── bioinformatics.py
│   │   │       ├── chemistry.py
│   │   │       └── physics.py
│   ├── tools/                                # NEW: Scientific tools
│   │   ├── __init__.py
│   │   ├── literature/
│   │   │   ├── __init__.py
│   │   │   ├── pubmed.py
│   │   │   ├── arxiv.py
│   │   │   ├── semantic_scholar.py
│   │   │   └── pdf_parser.py
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── python_executor.py
│   │   │   ├── statistics.py
│   │   │   └── ml_models.py
│   │   ├── visualization/
│   │   │   ├── __init__.py
│   │   │   ├── plotting.py
│   │   │   └── scientific_figures.py
│   │   ├── citation/
│   │   │   ├── __init__.py
│   │   │   ├── bibtex_manager.py
│   │   │   └── citation_formatter.py
│   │   ├── experimental/
│   │   │   ├── __init__.py
│   │   │   ├── power_analysis.py
│   │   │   ├── sample_size.py
│   │   │   └── protocol_generator.py
│   │   └── domains/
│   │       ├── __init__.py
│   │       ├── bio_tools.py
│   │       ├── chem_tools.py
│   │       └── physics_tools.py
│   └── subagents/                            # NEW: Predefined subagents
│       ├── __init__.py
│       ├── literature_reviewer.py
│       ├── data_analyst.py
│       ├── experimental_designer.py
│       ├── scientific_writer.py
│       ├── hypothesis_generator.py
│       └── domain_experts.py
├── examples/
│   ├── research/                             # Existing
│   │   └── research_agent.py
│   ├── co_scientist/                         # NEW: Co-scientist examples
│   │   ├── literature_review_example.py
│   │   ├── data_analysis_example.py
│   │   ├── experimental_design_example.py
│   │   ├── paper_writing_example.py
│   │   └── full_research_workflow.py
├── tests/
│   ├── integration_tests/
│   │   ├── test_literature_middleware.py     # NEW
│   │   ├── test_data_analysis_middleware.py  # NEW
│   │   ├── test_co_scientist.py              # NEW
│   └── utils.py
├── docs/
│   ├── co_scientist_guide.md                 # NEW
│   ├── middleware_reference.md               # NEW
│   └── subagents_reference.md                # NEW
├── requirements.txt
├── pyproject.toml
├── CO_SCIENTIST_DESIGN.md
└── IMPLEMENTATION_PLAN.md
```

---

## Phase 1: Foundation - Scientific Middleware

### 1.1 Literature Search Middleware

**File:** `src/deepagents/middleware/scientific/literature.py`

```python
"""Middleware for scientific literature search and management."""

from collections.abc import Callable, Awaitable
from typing import Any, Literal
from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain_core.tools import BaseTool, tool
from typing_extensions import TypedDict, NotRequired

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

Available tools:
- `search_pubmed(query, max_results)`: Search PubMed database for biomedical literature
- `search_arxiv(query, max_results, category)`: Search arXiv for preprints
- `search_semantic_scholar(query, max_results, fields)`: Search Semantic Scholar for papers across disciplines
- `download_paper(paper_id, source)`: Download full-text PDF of a paper
- `parse_scientific_pdf(file_path)`: Extract structured data from a scientific PDF
- `extract_references(file_path)`: Extract bibliography from a paper

Best practices:
- Store downloaded papers in `/papers/` directory
- Keep a summary of key findings in `/literature_summary.md`
- Track all citations in `/references/library.bib`
- Use specific, well-formed search queries
- Consider multiple databases for comprehensive coverage
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
        max_results_default: Default maximum results for searches (default: 10).

    Example:
        ```python
        from deepagents.middleware.scientific import LiteratureSearchMiddleware
        from deepagents import create_deep_agent

        agent = create_deep_agent(
            middleware=[LiteratureSearchMiddleware()]
        )

        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": "Search for recent papers on CRISPR gene editing"
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
        max_results_default: int = 10,
    ) -> None:
        """Initialize literature search middleware."""
        super().__init__()
        self.system_prompt = system_prompt or LITERATURE_SYSTEM_PROMPT
        self.max_results_default = max_results_default

        # Build tool list based on enabled sources
        self.tools: list[BaseTool] = []
        if enable_pubmed:
            self.tools.append(search_pubmed)
        if enable_arxiv:
            self.tools.append(search_arxiv)
        if enable_semantic_scholar:
            self.tools.append(search_semantic_scholar)

        # Always include download and parsing tools
        self.tools.extend([
            download_paper,
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
```

**File:** `src/deepagents/tools/literature/pubmed.py`

```python
"""PubMed search integration."""

from typing import Any
from langchain_core.tools import tool
import requests
from xml.etree import ElementTree


@tool
def search_pubmed(
    query: str,
    max_results: int = 10,
    sort: str = "relevance",
) -> list[dict[str, Any]]:
    """Search PubMed database for biomedical literature.

    Args:
        query: Search query string. Supports PubMed query syntax.
        max_results: Maximum number of results to return (default: 10).
        sort: Sort order - 'relevance', 'date', or 'citations' (default: 'relevance').

    Returns:
        List of paper metadata dictionaries with fields:
        - pmid: PubMed ID
        - title: Paper title
        - authors: List of author names
        - abstract: Abstract text
        - journal: Journal name
        - publication_date: Date of publication
        - doi: Digital Object Identifier
        - url: Link to paper

    Example:
        ```python
        results = search_pubmed("CRISPR gene editing cancer", max_results=5)
        for paper in results:
            print(f"{paper['title']} ({paper['publication_date']})")
        ```
    """
    # Implementation using NCBI E-utilities API
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    # Step 1: Search for IDs
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": sort,
    }

    try:
        search_response = requests.get(search_url, params=search_params, timeout=30)
        search_response.raise_for_status()
        search_data = search_response.json()

        pmids = search_data.get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return []

        # Step 2: Fetch details for IDs
        fetch_url = f"{base_url}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }

        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=30)
        fetch_response.raise_for_status()

        # Parse XML response
        root = ElementTree.fromstring(fetch_response.content)
        papers = []

        for article in root.findall(".//PubmedArticle"):
            paper_data = _parse_pubmed_article(article)
            papers.append(paper_data)

        return papers

    except requests.RequestException as e:
        return [{"error": f"PubMed API error: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Error processing PubMed results: {str(e)}"}]


def _parse_pubmed_article(article: ElementTree.Element) -> dict[str, Any]:
    """Parse a PubMed article XML element into a structured dictionary."""
    medline_citation = article.find(".//MedlineCitation")
    if medline_citation is None:
        return {"error": "Invalid article format"}

    pmid_elem = medline_citation.find(".//PMID")
    pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

    article_elem = medline_citation.find(".//Article")
    if article_elem is None:
        return {"pmid": pmid, "error": "No article data"}

    # Extract title
    title_elem = article_elem.find(".//ArticleTitle")
    title = title_elem.text if title_elem is not None else "No title"

    # Extract abstract
    abstract_elem = article_elem.find(".//Abstract/AbstractText")
    abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"

    # Extract authors
    authors = []
    author_list = article_elem.find(".//AuthorList")
    if author_list is not None:
        for author in author_list.findall(".//Author"):
            last_name = author.find(".//LastName")
            fore_name = author.find(".//ForeName")
            if last_name is not None and fore_name is not None:
                authors.append(f"{fore_name.text} {last_name.text}")

    # Extract journal
    journal_elem = article_elem.find(".//Journal/Title")
    journal = journal_elem.text if journal_elem is not None else "Unknown journal"

    # Extract publication date
    pub_date = article_elem.find(".//Journal/JournalIssue/PubDate")
    pub_date_str = "Unknown date"
    if pub_date is not None:
        year = pub_date.find(".//Year")
        month = pub_date.find(".//Month")
        day = pub_date.find(".//Day")
        date_parts = []
        if year is not None:
            date_parts.append(year.text)
        if month is not None:
            date_parts.append(month.text)
        if day is not None:
            date_parts.append(day.text)
        if date_parts:
            pub_date_str = " ".join(date_parts)

    # Extract DOI
    doi = None
    article_id_list = article.find(".//PubmedData/ArticleIdList")
    if article_id_list is not None:
        for article_id in article_id_list.findall(".//ArticleId"):
            if article_id.get("IdType") == "doi":
                doi = article_id.text
                break

    return {
        "pmid": pmid,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "journal": journal,
        "publication_date": pub_date_str,
        "doi": doi,
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
    }
```

**File:** `src/deepagents/tools/literature/arxiv.py`

```python
"""arXiv search integration."""

from typing import Any
from langchain_core.tools import tool
import requests


@tool
def search_arxiv(
    query: str,
    max_results: int = 10,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Search arXiv database for preprints.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return (default: 10).
        category: Optional arXiv category filter (e.g., 'cs.AI', 'q-bio.GN').

    Returns:
        List of paper metadata dictionaries with fields:
        - arxiv_id: arXiv identifier
        - title: Paper title
        - authors: List of author names
        - abstract: Abstract text
        - categories: List of arXiv categories
        - publication_date: Date of publication
        - url: Link to paper
        - pdf_url: Link to PDF

    Example:
        ```python
        results = search_arxiv("machine learning protein structure", max_results=5)
        for paper in results:
            print(f"{paper['title']} - {paper['pdf_url']}")
        ```
    """
    base_url = "http://export.arxiv.org/api/query"

    # Build search query
    search_query = f"all:{query}"
    if category:
        search_query = f"cat:{category}+AND+{search_query}"

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        # Parse Atom XML response
        from xml.etree import ElementTree
        root = ElementTree.fromstring(response.content)

        # Define namespace
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("atom:entry", ns):
            paper_data = {
                "arxiv_id": entry.find("atom:id", ns).text.split("/")[-1],
                "title": entry.find("atom:title", ns).text.strip(),
                "authors": [
                    author.find("atom:name", ns).text
                    for author in entry.findall("atom:author", ns)
                ],
                "abstract": entry.find("atom:summary", ns).text.strip(),
                "categories": [
                    cat.get("term")
                    for cat in entry.findall("atom:category", ns)
                ],
                "publication_date": entry.find("atom:published", ns).text,
                "url": entry.find("atom:id", ns).text,
                "pdf_url": entry.find("atom:id", ns).text.replace("/abs/", "/pdf/") + ".pdf",
            }
            papers.append(paper_data)

        return papers

    except requests.RequestException as e:
        return [{"error": f"arXiv API error: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Error processing arXiv results: {str(e)}"}]
```

**File:** `src/deepagents/tools/literature/semantic_scholar.py`

```python
"""Semantic Scholar API integration."""

from typing import Any
from langchain_core.tools import tool
import requests


@tool
def search_semantic_scholar(
    query: str,
    max_results: int = 10,
    fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Search Semantic Scholar for academic papers across disciplines.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return (default: 10).
        fields: Optional list of fields to retrieve. Available fields:
            'title', 'abstract', 'authors', 'year', 'citationCount',
            'referenceCount', 'venue', 'externalIds', 'url', 'openAccessPdf'

    Returns:
        List of paper metadata dictionaries.

    Example:
        ```python
        results = search_semantic_scholar(
            "neural networks",
            max_results=5,
            fields=['title', 'abstract', 'authors', 'citationCount']
        )
        ```
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    if fields is None:
        fields = [
            "title",
            "abstract",
            "authors",
            "year",
            "citationCount",
            "venue",
            "url",
            "openAccessPdf",
        ]

    params = {
        "query": query,
        "limit": max_results,
        "fields": ",".join(fields),
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        papers = []
        for paper in data.get("data", []):
            paper_data = {
                "s2_id": paper.get("paperId", "Unknown"),
                "title": paper.get("title", "No title"),
                "abstract": paper.get("abstract", "No abstract available"),
                "authors": [
                    author.get("name", "Unknown")
                    for author in paper.get("authors", [])
                ],
                "year": paper.get("year", "Unknown"),
                "citation_count": paper.get("citationCount", 0),
                "venue": paper.get("venue", "Unknown venue"),
                "url": paper.get("url", ""),
                "pdf_url": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None,
            }
            papers.append(paper_data)

        return papers

    except requests.RequestException as e:
        return [{"error": f"Semantic Scholar API error: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Error processing Semantic Scholar results: {str(e)}"}]
```

### 1.2 Data Analysis Middleware

**File:** `src/deepagents/middleware/scientific/data_analysis.py`

```python
"""Middleware for data analysis with sandboxed Python execution."""

from collections.abc import Callable, Awaitable
from typing import Any
from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain_core.tools import BaseTool
from typing_extensions import TypedDict, NotRequired

from deepagents.tools.analysis import (
    execute_python_code,
    statistical_test,
    fit_model,
    summarize_data,
)


DATA_ANALYSIS_SYSTEM_PROMPT = """## Data Analysis Tools

You have access to data analysis tools including sandboxed Python execution.

Available tools:
- `execute_python_code(code, timeout)`: Execute Python code in a secure sandbox
- `statistical_test(test_type, data_path, parameters)`: Perform statistical hypothesis tests
- `fit_model(model_type, data_path, parameters)`: Fit regression or ML models
- `summarize_data(data_path)`: Get descriptive statistics for a dataset

Python Sandbox Environment:
- Available libraries: numpy, pandas, scipy, sklearn, statsmodels, matplotlib, seaborn
- Execution timeout: 60 seconds (configurable)
- Memory limit: 2GB
- No network access
- File system access limited to /data/ and /figures/ directories

Best practices:
- Store datasets in `/data/` directory
- Save figures to `/figures/` directory
- Document all analysis steps in `/analysis/analysis_log.md`
- Save important results to `/results/` directory
- Include comments in Python code for reproducibility

Security:
- Code execution is sandboxed and isolated
- External network requests are blocked
- File system access is restricted
- All operations are logged
"""


class DataAnalysisState(AgentState):
    """Extended state for data analysis functionality."""

    analysis_results: NotRequired[dict[str, Any]]
    """Dictionary of analysis results and outputs."""


class DataAnalysisMiddleware(AgentMiddleware):
    """Middleware for statistical analysis and Python code execution.

    Provides secure, sandboxed Python execution environment with
    pre-installed scientific libraries for data analysis.

    Args:
        system_prompt: Optional custom system prompt override.
        timeout: Default timeout for code execution in seconds (default: 60).
        memory_limit_mb: Memory limit in MB (default: 2048).
        enable_plotting: Whether to enable matplotlib/seaborn (default: True).

    Example:
        ```python
        from deepagents.middleware.scientific import DataAnalysisMiddleware
        from deepagents import create_deep_agent

        agent = create_deep_agent(
            middleware=[DataAnalysisMiddleware(timeout=120)]
        )

        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": "Analyze the data in /data/experiment.csv and create a plot"
            }]
        })
        ```
    """

    state_schema = DataAnalysisState

    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        timeout: int = 60,
        memory_limit_mb: int = 2048,
        enable_plotting: bool = True,
    ) -> None:
        """Initialize data analysis middleware."""
        super().__init__()
        self.system_prompt = system_prompt or DATA_ANALYSIS_SYSTEM_PROMPT
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.enable_plotting = enable_plotting

        self.tools: list[BaseTool] = [
            execute_python_code,
            statistical_test,
            fit_model,
            summarize_data,
        ]

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Add data analysis instructions to system prompt."""
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
        """(async) Add data analysis instructions to system prompt."""
        if self.system_prompt is not None:
            request.system_prompt = (
                request.system_prompt + "\n\n" + self.system_prompt
                if request.system_prompt
                else self.system_prompt
            )
        return await handler(request)
```

**File:** `src/deepagents/tools/analysis/python_executor.py`

```python
"""Secure Python code execution sandbox."""

from typing import Any
from langchain_core.tools import tool
import subprocess
import tempfile
import os
import json


@tool
def execute_python_code(
    code: str,
    timeout: int = 60,
) -> str:
    """Execute Python code in a secure sandboxed environment.

    Args:
        code: Python code to execute.
        timeout: Maximum execution time in seconds (default: 60).

    Returns:
        String containing stdout, stderr, and any generated output.
        If figures are created, they are saved to /figures/ and paths are returned.

    Available libraries:
    - numpy, pandas, scipy, sklearn, statsmodels
    - matplotlib, seaborn (if plotting enabled)

    Example:
        ```python
        code = '''
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('/data/experiment.csv')

# Create plot
plt.figure(figsize=(10, 6))
plt.scatter(df['x'], df['y'])
plt.xlabel('X variable')
plt.ylabel('Y variable')
plt.title('Experiment Results')
plt.savefig('/figures/scatter_plot.png', dpi=300, bbox_inches='tight')

# Summary statistics
print(df.describe())
        '''
        result = execute_python_code(code)
        print(result)
        ```

    Security:
    - No network access
    - Limited file system access (/data/ and /figures/ only)
    - Memory and CPU limits enforced
    - Execution timeout
    """
    # Create a temporary directory for execution
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write code to temporary file
        code_file = os.path.join(tmpdir, "script.py")
        with open(code_file, "w") as f:
            f.write(code)

        # Prepare execution environment
        # In production, this should use Docker or a proper sandbox
        # For now, we'll use subprocess with some restrictions
        try:
            # Run with restricted environment
            result = subprocess.run(
                ["python3", code_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                # Add environment restrictions
                env={
                    "PYTHONPATH": "",
                    "HOME": tmpdir,
                },
            )

            output = []
            if result.stdout:
                output.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output.append(f"STDERR:\n{result.stderr}")
            if result.returncode != 0:
                output.append(f"Exit code: {result.returncode}")

            return "\n\n".join(output) if output else "Code executed successfully with no output."

        except subprocess.TimeoutExpired:
            return f"Error: Code execution exceeded timeout of {timeout} seconds."
        except Exception as e:
            return f"Error executing code: {str(e)}"


# NOTE: In production, replace the above implementation with a proper
# sandboxing solution like Docker, RestrictedPython, or a dedicated
# code execution service. The current implementation is simplified
# for demonstration purposes.
```

### 1.3 Visualization Middleware

**File:** `src/deepagents/middleware/scientific/visualization.py`

```python
"""Middleware for scientific data visualization."""

from collections.abc import Callable, Awaitable
from langchain.agents.middleware.types import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)
from langchain_core.tools import BaseTool

from deepagents.tools.visualization import (
    create_plot,
    create_heatmap,
    create_publication_figure,
)


VISUALIZATION_SYSTEM_PROMPT = """## Data Visualization Tools

You have access to scientific visualization tools for creating publication-quality figures.

Available tools:
- `create_plot(plot_type, data_path, parameters)`: Create various plot types
- `create_heatmap(data_path, parameters)`: Create heatmaps for matrix data
- `create_publication_figure(plot_config)`: Create publication-ready multi-panel figures

Supported plot types:
- scatter, line, bar, box, violin, histogram
- scatter_3d, surface_3d
- volcano (for omics data)
- manhattan (for GWAS data)
- network_graph

Best practices:
- Save all figures to `/figures/` directory
- Use high DPI (300+) for publication quality
- Include clear axis labels and titles
- Save in multiple formats (PNG for preview, PDF/SVG for publication)
- Document figure generation in `/figures/figure_log.md`
"""


class VisualizationMiddleware(AgentMiddleware):
    """Middleware for creating scientific visualizations.

    Provides tools for generating publication-quality plots and figures.

    Args:
        system_prompt: Optional custom system prompt override.
        default_dpi: Default DPI for saved figures (default: 300).
        default_format: Default figure format (default: 'png').

    Example:
        ```python
        from deepagents.middleware.scientific import VisualizationMiddleware
        from deepagents import create_deep_agent

        agent = create_deep_agent(
            middleware=[VisualizationMiddleware(default_dpi=600)]
        )
        ```
    """

    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        default_dpi: int = 300,
        default_format: str = "png",
    ) -> None:
        """Initialize visualization middleware."""
        super().__init__()
        self.system_prompt = system_prompt or VISUALIZATION_SYSTEM_PROMPT
        self.default_dpi = default_dpi
        self.default_format = default_format

        self.tools: list[BaseTool] = [
            create_plot,
            create_heatmap,
            create_publication_figure,
        ]

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Add visualization instructions to system prompt."""
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
        """(async) Add visualization instructions to system prompt."""
        if self.system_prompt is not None:
            request.system_prompt = (
                request.system_prompt + "\n\n" + self.system_prompt
                if request.system_prompt
                else self.system_prompt
            )
        return await handler(request)
```

### 1.4 Citation Management Middleware

**File:** `src/deepagents/middleware/scientific/citation.py`

```python
"""Middleware for citation and reference management."""

from collections.abc import Callable, Awaitable
from typing import Any
from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain_core.tools import BaseTool
from typing_extensions import TypedDict, NotRequired

from deepagents.tools.citation import (
    add_reference,
    cite_paper,
    format_bibliography,
    export_bibtex,
    import_bibtex,
)


CITATION_SYSTEM_PROMPT = """## Citation Management Tools

You have access to citation and reference management tools.

Available tools:
- `add_reference(paper_metadata)`: Add a paper to the reference library
- `cite_paper(paper_id, citation_style)`: Generate an in-text citation
- `format_bibliography(citation_style)`: Create a formatted bibliography
- `export_bibtex(output_path)`: Export references in BibTeX format
- `import_bibtex(file_path)`: Import references from BibTeX file

Citation styles supported:
- apa: APA 7th edition
- mla: MLA 9th edition
- chicago: Chicago Manual of Style
- vancouver: Vancouver style (common in medical journals)
- nature: Nature journal style
- science: Science journal style

Best practices:
- Store references in `/references/library.bib`
- Maintain consistent citation style throughout document
- Include all cited papers in bibliography
- Use unique citation keys for each paper
"""


class CitationState(AgentState):
    """Extended state for citation management."""

    references: NotRequired[dict[str, Any]]
    """Dictionary of references in the library."""


class CitationManagementMiddleware(AgentMiddleware):
    """Middleware for managing citations and references.

    Provides tools for adding references, generating citations,
    and formatting bibliographies in various styles.

    Args:
        system_prompt: Optional custom system prompt override.
        default_style: Default citation style (default: 'apa').
        library_path: Path to reference library file (default: '/references/library.bib').

    Example:
        ```python
        from deepagents.middleware.scientific import CitationManagementMiddleware
        from deepagents import create_deep_agent

        agent = create_deep_agent(
            middleware=[
                CitationManagementMiddleware(default_style='nature')
            ]
        )
        ```
    """

    state_schema = CitationState

    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        default_style: str = "apa",
        library_path: str = "/references/library.bib",
    ) -> None:
        """Initialize citation management middleware."""
        super().__init__()
        self.system_prompt = system_prompt or CITATION_SYSTEM_PROMPT
        self.default_style = default_style
        self.library_path = library_path

        self.tools: list[BaseTool] = [
            add_reference,
            cite_paper,
            format_bibliography,
            export_bibtex,
            import_bibtex,
        ]

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Add citation management instructions to system prompt."""
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
        """(async) Add citation management instructions to system prompt."""
        if self.system_prompt is not None:
            request.system_prompt = (
                request.system_prompt + "\n\n" + self.system_prompt
                if request.system_prompt
                else self.system_prompt
            )
        return await handler(request)
```

---

## Phase 2: Specialized Subagents

### 2.1 Literature Reviewer Subagent

**File:** `src/deepagents/subagents/literature_reviewer.py`

```python
"""Literature reviewer subagent configuration."""

from typing import Any
from deepagents.middleware.scientific.literature import LiteratureSearchMiddleware
from deepagents.middleware.scientific.citation import CitationManagementMiddleware


LITERATURE_REVIEWER_PROMPT = """You are a scientific literature review expert. Your role is to conduct comprehensive, systematic reviews of scientific literature.

## Your Responsibilities

1. **Search Strategy**
   - Formulate effective search queries
   - Search multiple databases (PubMed, arXiv, Semantic Scholar)
   - Apply appropriate filters and inclusion/exclusion criteria

2. **Paper Analysis**
   - Read and analyze papers systematically
   - Extract key information: research questions, methods, results, conclusions
   - Identify strengths and limitations
   - Note statistical rigor and reproducibility

3. **Synthesis**
   - Identify common themes and patterns across studies
   - Compare and contrast findings
   - Identify contradictions and controversies
   - Map the research landscape

4. **Gap Analysis**
   - Identify what is known vs unknown
   - Spot methodological limitations
   - Find opportunities for future research
   - Suggest novel directions

5. **Documentation**
   - Store all papers in `/papers/` with consistent naming
   - Maintain comprehensive notes in `/literature_review_summary.md`
   - Track all citations in `/references/library.bib`
   - Create evidence tables when appropriate

## Output Format

Your final report should include:
- **Overview**: Brief summary of the review scope and search strategy
- **Key Findings**: Main themes and important discoveries
- **Detailed Analysis**: In-depth discussion of major papers and findings
- **Research Gaps**: What's missing or needs more investigation
- **Recommendations**: Suggested future directions
- **References**: Complete bibliography

## Best Practices

- Be systematic and thorough
- Document search strategies and inclusion criteria
- Assess quality and reliability of sources
- Consider both recent advances and foundational work
- Look for meta-analyses and systematic reviews
- Check for publication bias
- Note sample sizes and statistical power
- Consider clinical/practical significance vs statistical significance

Remember: Your final message is the ONLY output the user will see. Make it comprehensive and well-organized.
"""


def create_literature_reviewer_subagent() -> dict[str, Any]:
    """Create literature reviewer subagent configuration.

    Returns:
        SubAgent configuration dictionary.
    """
    from deepagents.tools.literature import (
        search_pubmed,
        search_arxiv,
        search_semantic_scholar,
        download_paper,
        parse_scientific_pdf,
        extract_references,
    )

    return {
        "name": "literature-reviewer",
        "description": """Expert at conducting comprehensive literature reviews. Use this agent when you need to:
- Systematically review scientific literature on a topic
- Identify research trends and gaps
- Analyze multiple papers and synthesize findings
- Create evidence-based summaries
- Find relevant papers across multiple databases

This agent has deep expertise in literature search, paper analysis, and synthesis.""",
        "system_prompt": LITERATURE_REVIEWER_PROMPT,
        "tools": [
            search_pubmed,
            search_arxiv,
            search_semantic_scholar,
            download_paper,
            parse_scientific_pdf,
            extract_references,
        ],
        "middleware": [
            LiteratureSearchMiddleware(),
            CitationManagementMiddleware(),
        ],
    }
```

### 2.2 Data Analyst Subagent

**File:** `src/deepagents/subagents/data_analyst.py`

```python
"""Data analyst subagent configuration."""

from typing import Any
from deepagents.middleware.scientific.data_analysis import DataAnalysisMiddleware
from deepagents.middleware.scientific.visualization import VisualizationMiddleware


DATA_ANALYST_PROMPT = """You are a data analysis expert with expertise in statistics, data science, and scientific computing.

## Your Responsibilities

1. **Data Exploration**
   - Load and inspect datasets
   - Check for missing values, outliers, data types
   - Generate summary statistics
   - Create exploratory visualizations

2. **Statistical Analysis**
   - Choose appropriate statistical tests
   - Check assumptions (normality, homogeneity of variance, etc.)
   - Perform hypothesis testing
   - Calculate effect sizes and confidence intervals
   - Apply multiple testing corrections when needed

3. **Modeling**
   - Select appropriate models (regression, classification, etc.)
   - Split data into training/validation/test sets
   - Train and evaluate models
   - Assess model performance and diagnostics
   - Interpret model results

4. **Visualization**
   - Create publication-quality figures
   - Use appropriate plot types for data
   - Include clear labels, legends, and captions
   - Save figures in multiple formats
   - Maintain consistent style

5. **Interpretation**
   - Explain statistical results in plain language
   - Distinguish between statistical and practical significance
   - Identify limitations and caveats
   - Suggest appropriate conclusions

## File Organization

- Store datasets in `/data/`
- Save figures to `/figures/`
- Document analysis steps in `/analysis/analysis_log.md`
- Save important results to `/results/`
- Keep code reproducible and well-commented

## Python Code Guidelines

When writing analysis code:
- Import necessary libraries at the top
- Add comments explaining each step
- Include error handling
- Save intermediate results
- Generate summary statistics
- Create diagnostic plots
- Document assumptions and decisions

Example structure:
```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('/data/experiment.csv')

# Explore data
print("Dataset shape:", df.shape)
print("Summary statistics:")
print(df.describe())

# Check for missing values
print("Missing values:")
print(df.isnull().sum())

# Perform analysis
# ... (your analysis code)

# Create visualization
plt.figure(figsize=(10, 6))
# ... (your plot code)
plt.savefig('/figures/result_plot.png', dpi=300, bbox_inches='tight')

# Print results
print("Analysis results:")
# ... (your results)
```

## Statistical Best Practices

- Always check assumptions before applying tests
- Use non-parametric tests when assumptions are violated
- Report complete statistics (test statistic, p-value, effect size, CI)
- Apply Bonferroni or FDR correction for multiple comparisons
- Consider sample size and power
- Look for biological/practical significance, not just statistical
- Be cautious with small sample sizes
- Report both positive and negative results

Remember: Your final message is the ONLY output the user will see. Include:
- Summary of findings
- Key statistics and visualizations
- Interpretation and implications
- Any limitations or caveats
"""


def create_data_analyst_subagent() -> dict[str, Any]:
    """Create data analyst subagent configuration.

    Returns:
        SubAgent configuration dictionary.
    """
    from deepagents.tools.analysis import (
        execute_python_code,
        statistical_test,
        fit_model,
        summarize_data,
    )
    from deepagents.tools.visualization import (
        create_plot,
        create_heatmap,
        create_publication_figure,
    )

    return {
        "name": "data-analyst",
        "description": """Expert in statistical analysis, data visualization, and interpreting experimental results. Use this agent when you need to:
- Analyze datasets with statistical methods
- Create publication-quality plots and figures
- Perform regression or machine learning modeling
- Interpret statistical results
- Check assumptions and diagnostics
- Generate comprehensive analysis reports

This agent can execute Python code for complex analyses.""",
        "system_prompt": DATA_ANALYST_PROMPT,
        "tools": [
            execute_python_code,
            statistical_test,
            fit_model,
            summarize_data,
            create_plot,
            create_heatmap,
            create_publication_figure,
        ],
        "middleware": [
            DataAnalysisMiddleware(timeout=120),
            VisualizationMiddleware(),
        ],
    }
```

### 2.3 Creating Co-Scientist Agent

**File:** `src/deepagents/co_scientist.py`

```python
"""Factory function for creating co-scientist agents."""

from typing import Any, Sequence
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.types import Checkpointer

from deepagents.graph import create_deep_agent
from deepagents.middleware.scientific.literature import LiteratureSearchMiddleware
from deepagents.middleware.scientific.data_analysis import DataAnalysisMiddleware
from deepagents.middleware.scientific.visualization import VisualizationMiddleware
from deepagents.middleware.scientific.citation import CitationManagementMiddleware
from deepagents.subagents.literature_reviewer import create_literature_reviewer_subagent
from deepagents.subagents.data_analyst import create_data_analyst_subagent


CO_SCIENTIST_SYSTEM_PROMPT = """You are a Co-Scientist AI Assistant, designed to work alongside scientists throughout the entire research lifecycle.

## Your Role

You are not here to replace scientists, but to amplify their capabilities by handling:
- Time-consuming literature reviews
- Complex data analyses
- Figure generation and formatting
- Citation management
- Experimental design considerations
- Scientific writing assistance

## Your Capabilities

### 1. Literature Review & Research
- Search scientific databases (PubMed, arXiv, Semantic Scholar)
- Retrieve and analyze papers
- Identify research gaps and trends
- Manage citations and references

### 2. Data Analysis
- Execute Python code for statistical analysis
- Create publication-quality visualizations
- Perform hypothesis testing
- Build and evaluate models
- Interpret results

### 3. Experimental Design
- Help design rigorous experiments
- Perform power analysis
- Suggest appropriate controls
- Generate detailed protocols

### 4. Scientific Writing
- Draft papers, grants, and reports
- Format citations and references
- Generate figure captions
- Maintain consistent scientific writing style

## File Organization

Use a systematic file organization:
- `/papers/` - Downloaded scientific papers
- `/literature_review_summary.md` - Synthesis of literature findings
- `/references/library.bib` - Citation library
- `/data/` - Experimental datasets
- `/figures/` - Generated plots and visualizations
- `/analysis/` - Analysis logs and code
- `/results/` - Analysis results and tables
- `/protocols/` - Experimental protocols
- `/manuscript/` - Manuscript drafts
- `/hypotheses.md` - Research hypotheses and rationale
- `/research_journal.md` - Ongoing research notes and decisions

## Using Specialized Subagents

You have access to expert subagents for focused work:

- **literature-reviewer**: Comprehensive, systematic literature reviews
- **data-analyst**: Statistical analysis and visualization

Delegate complex, multi-step tasks to subagents to keep your context clean and focused.

## Long-term Research Projects

For ongoing projects:
1. Create a project plan at `/project_plan.md`
2. Use todos to track progress and next steps
3. Document all decisions and rationale in `/research_journal.md`
4. Maintain reproducibility by saving code, parameters, and random seeds
5. Version control protocols and manuscripts
6. Keep comprehensive notes for continuity

## Best Practices

1. **Be Systematic**: Break down complex questions into manageable tasks
2. **Document Everything**: Store all information for future reference
3. **Ensure Reproducibility**: Save code, parameters, and analysis steps
4. **Think Critically**: Question assumptions, consider alternatives, identify limitations
5. **Cite Properly**: Always attribute ideas and maintain reference library
6. **Seek Clarity**: Ask for clarification when research questions are ambiguous
7. **Human Collaboration**: This is a collaboration - get human input for critical decisions

## Communication Style

- Be clear and concise
- Use scientific language appropriately
- Explain statistical concepts when needed
- Acknowledge uncertainty and limitations
- Present both supporting and contradicting evidence
- Focus on scientific rigor and reproducibility

You are a research assistant that makes scientists more productive while maintaining the highest standards of scientific integrity.
"""


def create_co_scientist(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool] | None = None,
    *,
    additional_subagents: list[dict[str, Any]] | None = None,
    enable_literature_search: bool = True,
    enable_data_analysis: bool = True,
    enable_visualization: bool = True,
    enable_citation_management: bool = True,
    use_longterm_memory: bool = True,
    store: BaseStore | None = None,
    checkpointer: Checkpointer | None = None,
    **kwargs: Any,
) -> Any:
    """Create a Co-Scientist agent with scientific capabilities.

    This is a specialized factory function that creates a deep agent
    configured for scientific research tasks. It includes middleware
    for literature search, data analysis, visualization, and citation
    management, along with specialized subagents.

    Args:
        model: Language model to use (default: Claude Sonnet 4.5).
        tools: Additional tools to provide to the agent.
        additional_subagents: Additional custom subagents beyond the defaults.
        enable_literature_search: Enable literature search capabilities (default: True).
        enable_data_analysis: Enable data analysis capabilities (default: True).
        enable_visualization: Enable visualization capabilities (default: True).
        enable_citation_management: Enable citation management (default: True).
        use_longterm_memory: Enable persistent memory across sessions (default: True).
        store: Store for long-term memory (default: InMemoryStore).
        checkpointer: Checkpointer for agent state persistence.
        **kwargs: Additional arguments to pass to create_deep_agent.

    Returns:
        Configured co-scientist agent (CompiledStateGraph).

    Example:
        ```python
        from deepagents import create_co_scientist

        # Create co-scientist agent
        agent = create_co_scientist()

        # Use for literature review
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": "Conduct a literature review on CRISPR applications in cancer therapy"
            }]
        })

        # Use for data analysis
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": "Analyze the experimental data in /data/results.csv"
            }]
        })
        ```
    """
    # Build middleware list
    middleware_list = []

    if enable_literature_search:
        middleware_list.append(LiteratureSearchMiddleware())

    if enable_data_analysis:
        middleware_list.append(DataAnalysisMiddleware())

    if enable_visualization:
        middleware_list.append(VisualizationMiddleware())

    if enable_citation_management:
        middleware_list.append(CitationManagementMiddleware())

    # Build subagents list
    subagents_list = []

    if enable_literature_search:
        subagents_list.append(create_literature_reviewer_subagent())

    if enable_data_analysis:
        subagents_list.append(create_data_analyst_subagent())

    if additional_subagents:
        subagents_list.extend(additional_subagents)

    # Set up store for long-term memory
    if use_longterm_memory and store is None:
        store = InMemoryStore()

    # Create the agent
    return create_deep_agent(
        model=model,
        tools=tools or [],
        system_prompt=CO_SCIENTIST_SYSTEM_PROMPT,
        middleware=middleware_list,
        subagents=subagents_list,
        use_longterm_memory=use_longterm_memory,
        store=store,
        checkpointer=checkpointer,
        **kwargs,
    )
```

---

## Phase 3: Domain-Specific Tools

### 3.1 Bioinformatics Middleware

**File:** `src/deepagents/middleware/scientific/domains/bioinformatics.py`

```python
"""Middleware for bioinformatics tools."""

from langchain.agents.middleware.types import AgentMiddleware


BIOINFORMATICS_SYSTEM_PROMPT = """## Bioinformatics Tools

You have access to bioinformatics analysis tools:

- `blast_search(sequence, database, program)`: Search for sequence homologs
- `align_sequences(sequences, method)`: Multiple sequence alignment
- `predict_protein_structure(sequence)`: Predict 3D protein structure
- `annotate_genes(sequence_file)`: Gene annotation and prediction
- `pathway_analysis(gene_list, organism)`: Biological pathway enrichment

Use these tools for genomic, proteomic, and biological sequence analysis.
"""


class BioinformaticsMiddleware(AgentMiddleware):
    """Middleware providing bioinformatics analysis tools.

    Example:
        ```python
        from deepagents.middleware.scientific.domains import BioinformaticsMiddleware
        from deepagents import create_co_scientist

        agent = create_co_scientist(
            additional_middleware=[BioinformaticsMiddleware()]
        )
        ```
    """

    def __init__(self, *, system_prompt: str | None = None) -> None:
        """Initialize bioinformatics middleware."""
        super().__init__()
        self.system_prompt = system_prompt or BIOINFORMATICS_SYSTEM_PROMPT

        # Import and configure tools
        from deepagents.tools.domains.bio_tools import (
            blast_search,
            align_sequences,
            predict_protein_structure,
        )

        self.tools = [
            blast_search,
            align_sequences,
            predict_protein_structure,
        ]
```

---

## Testing Strategy

### Integration Test Example

**File:** `tests/integration_tests/test_co_scientist.py`

```python
"""Integration tests for co-scientist agent."""

import pytest
from langchain_core.messages import HumanMessage

from deepagents.co_scientist import create_co_scientist


class TestCoScientist:
    def test_create_co_scientist(self):
        """Test basic co-scientist creation."""
        agent = create_co_scientist()
        assert agent is not None

        # Check that scientific middleware tools are present
        tool_names = set(agent.nodes["tools"].bound._tools_by_name.keys())
        assert "search_pubmed" in tool_names
        assert "execute_python_code" in tool_names

    def test_literature_search_integration(self):
        """Test literature search functionality."""
        agent = create_co_scientist()

        result = agent.invoke({
            "messages": [HumanMessage(content="Search PubMed for papers on CRISPR")]
        })

        # Verify task tool was used to delegate to literature-reviewer
        messages = result.get("messages", [])
        tool_calls = [
            tool_call
            for msg in messages
            if hasattr(msg, "tool_calls")
            for tool_call in msg.tool_calls
        ]

        # Check if literature search or subagent was used
        assert any(
            "pubmed" in tc["name"].lower() or tc["name"] == "task"
            for tc in tool_calls
        )

    def test_data_analysis_integration(self):
        """Test data analysis functionality."""
        agent = create_co_scientist()

        # Create a simple dataset in /data/
        # (In real tests, this would be set up in fixtures)

        result = agent.invoke({
            "messages": [
                HumanMessage(
                    content="Execute Python code to create a simple plot: import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.savefig('/figures/test.png')"
                )
            ]
        })

        messages = result.get("messages", [])
        # Verify code execution was attempted
        assert any("execute_python" in str(msg) for msg in messages)

    @pytest.mark.parametrize("subagent_type", [
        "literature-reviewer",
        "data-analyst",
    ])
    def test_subagent_invocation(self, subagent_type):
        """Test that subagents can be invoked."""
        agent = create_co_scientist()

        result = agent.invoke({
            "messages": [
                HumanMessage(
                    content=f"Use the {subagent_type} subagent to help with this task"
                )
            ]
        })

        messages = result.get("messages", [])
        tool_calls = [
            tc
            for msg in messages
            if hasattr(msg, "tool_calls")
            for tc in msg.tool_calls
        ]

        # Verify task tool was called with correct subagent
        assert any(
            tc["name"] == "task"
            and tc.get("args", {}).get("subagent_type") == subagent_type
            for tc in tool_calls
        )
```

---

## Deployment

### Example Deployment Script

**File:** `examples/co_scientist/deploy_co_scientist.py`

```python
"""Example deployment script for co-scientist agent."""

import os
from deepagents.co_scientist import create_co_scientist
from langgraph.checkpoint.postgres import PostgresSaver


def deploy_co_scientist():
    """Deploy co-scientist agent with production configuration."""

    # Configure production store (e.g., PostgreSQL)
    # This requires: pip install psycopg2-binary
    DATABASE_URI = os.environ.get("DATABASE_URI", "postgresql://localhost/coscientist")

    # Create checkpointer for state persistence
    checkpointer = PostgresSaver.from_conn_string(DATABASE_URI)
    checkpointer.setup()

    # Create agent with production settings
    agent = create_co_scientist(
        model="claude-sonnet-4-5-20250929",
        use_longterm_memory=True,
        # store will be created from checkpointer
        checkpointer=checkpointer,
        # Enable human-in-the-loop for sensitive operations
        interrupt_on={
            "execute_python_code": True,  # Require approval for code execution
        },
    )

    return agent


if __name__ == "__main__":
    agent = deploy_co_scientist()
    print("Co-scientist agent deployed successfully!")

    # Example usage
    result = agent.invoke(
        {
            "messages": [{
                "role": "user",
                "content": "Help me start a research project on neurodegenerative diseases"
            }]
        },
        config={"configurable": {"thread_id": "project_001"}}
    )

    print("\nAgent response:")
    print(result["messages"][-1].content)
```

---

## Summary

This implementation plan provides:

1. **Concrete code structure** for all new components
2. **Detailed middleware implementations** with proper interfaces
3. **Tool definitions** with clear documentation
4. **Subagent configurations** with specialized prompts
5. **Integration tests** to verify functionality
6. **Deployment examples** for production use

The modular architecture ensures that components can be:
- Developed independently
- Tested in isolation
- Combined flexibly
- Extended with new capabilities

**Next Steps:**
1. Begin implementing Phase 1 middleware
2. Develop tool implementations
3. Test each component thoroughly
4. Integrate into full co-scientist agent
5. Create comprehensive examples and documentation
