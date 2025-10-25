"""arXiv search integration using arXiv API."""

from typing import Any
from xml.etree import ElementTree

import requests
from langchain_core.tools import tool


@tool
def search_arxiv(
    query: str,
    max_results: int = 10,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Search arXiv database for preprints and scientific papers.

    This tool searches the arXiv repository for preprints across physics, mathematics,
    computer science, quantitative biology, quantitative finance, statistics, and more.

    Args:
        query: Search query string. Supports arXiv query syntax including:
            - Simple terms: "neural networks"
            - Field-specific: ti:"machine learning" (title), au:"John Doe" (author)
            - Boolean: AND, OR, ANDNOT
            Examples:
            - "quantum computing"
            - "ti:transformer AND cat:cs.AI"
            - "au:LeCun"
        max_results: Maximum number of results to return (default: 10, max: 100).
        category: Optional arXiv category filter. Common categories:
            - cs.AI: Artificial Intelligence
            - cs.LG: Machine Learning
            - cs.CL: Computation and Language
            - q-bio.GN: Genomics
            - q-bio.QM: Quantitative Methods
            - physics.bio-ph: Biological Physics
            - stat.ML: Machine Learning (Statistics)
            Full list: https://arxiv.org/category_taxonomy

    Returns:
        List of paper metadata dictionaries, each containing:
        - arxiv_id (str): arXiv identifier (e.g., "2301.12345")
        - title (str): Paper title
        - authors (list[str]): List of author names
        - abstract (str): Abstract text
        - categories (list[str]): List of arXiv categories
        - publication_date (str): Date published on arXiv
        - updated_date (str): Date last updated
        - url (str): Link to abstract page
        - pdf_url (str): Direct link to PDF

    Example:
        >>> results = search_arxiv("machine learning protein structure", max_results=5)
        >>> for paper in results:
        ...     print(f"{paper['title']}")
        ...     print(f"Authors: {', '.join(paper['authors'][:3])}")
        ...     print(f"Categories: {', '.join(paper['categories'])}")
        ...     print(f"PDF: {paper['pdf_url']}")

        >>> # Search specific category
        >>> results = search_arxiv("transformers", category="cs.LG", max_results=5)

    Note:
        - Free and open access, no API key required
        - Please be respectful: limit to 1 request per 3 seconds
        - Full-text PDFs are freely available
        - Papers are preprints (not peer-reviewed)
    """
    base_url = "http://export.arxiv.org/api/query"

    # Limit max_results to prevent excessive API calls
    max_results = min(max_results, 100)

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
        root = ElementTree.fromstring(response.content)

        # Define namespace
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        papers = []
        for entry in root.findall("atom:entry", ns):
            try:
                paper_data = _parse_arxiv_entry(entry, ns)
                papers.append(paper_data)
            except Exception as e:
                # Skip malformed entries but continue processing
                continue

        return papers

    except requests.RequestException as e:
        return [{"error": f"arXiv API request failed: {str(e)}"}]
    except ElementTree.ParseError as e:
        return [{"error": f"Failed to parse arXiv XML response: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Unexpected error during arXiv search: {str(e)}"}]


def _parse_arxiv_entry(entry: ElementTree.Element, ns: dict[str, str]) -> dict[str, Any]:
    """Parse an arXiv entry XML element into a structured dictionary.

    Args:
        entry: XML Element representing an arXiv entry.
        ns: Namespace dictionary for XML parsing.

    Returns:
        Dictionary with paper metadata.
    """
    # Extract arXiv ID from the full URL
    id_elem = entry.find("atom:id", ns)
    arxiv_url = id_elem.text if id_elem is not None else ""
    arxiv_id = arxiv_url.split("/")[-1] if arxiv_url else "Unknown"

    # Extract title (strip whitespace and newlines)
    title_elem = entry.find("atom:title", ns)
    title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else "No title"

    # Extract authors
    authors = []
    for author in entry.findall("atom:author", ns):
        name_elem = author.find("atom:name", ns)
        if name_elem is not None:
            authors.append(name_elem.text)

    # Extract abstract (strip whitespace and newlines)
    summary_elem = entry.find("atom:summary", ns)
    abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else "No abstract"

    # Extract categories
    categories = []
    for cat in entry.findall("atom:category", ns):
        term = cat.get("term")
        if term:
            categories.append(term)

    # Also get arXiv-specific primary category
    primary_cat = entry.find("arxiv:primary_category", ns)
    if primary_cat is not None:
        primary_term = primary_cat.get("term")
        if primary_term and primary_term not in categories:
            categories.insert(0, primary_term)

    # Extract dates
    published_elem = entry.find("atom:published", ns)
    publication_date = published_elem.text if published_elem is not None else "Unknown date"

    updated_elem = entry.find("atom:updated", ns)
    updated_date = updated_elem.text if updated_elem is not None else publication_date

    # Construct URLs
    url = arxiv_url
    pdf_url = arxiv_url.replace("/abs/", "/pdf/") + ".pdf" if arxiv_url else ""

    # Extract DOI if available
    doi = None
    doi_elem = entry.find("arxiv:doi", ns)
    if doi_elem is not None:
        doi = doi_elem.text

    # Extract journal reference if available
    journal_ref = None
    journal_elem = entry.find("arxiv:journal_ref", ns)
    if journal_elem is not None:
        journal_ref = journal_elem.text

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "categories": categories,
        "publication_date": publication_date,
        "updated_date": updated_date,
        "url": url,
        "pdf_url": pdf_url,
        "doi": doi,
        "journal_ref": journal_ref,
    }
