"""Semantic Scholar API integration."""

import os
from typing import Any

import requests
from langchain_core.tools import tool


@tool
def search_semantic_scholar(
    query: str,
    max_results: int = 10,
    fields: list[str] | None = None,
    year_range: tuple[int, int] | None = None,
) -> list[dict[str, Any]]:
    """Search Semantic Scholar for academic papers across all disciplines.

    Semantic Scholar is an AI-powered research tool that indexes papers from
    computer science, neuroscience, and biomedical sciences. It provides
    rich metadata including citation counts and influential citations.

    Args:
        query: Search query string. Supports natural language queries.
            Examples:
            - "neural networks for protein folding"
            - "CRISPR applications"
            - "climate change machine learning"
        max_results: Maximum number of results to return (default: 10, max: 100).
        fields: Optional list of fields to retrieve. If None, returns default fields.
            Available fields:
            - Basic: title, abstract, authors, year
            - Metrics: citationCount, influentialCitationCount, referenceCount
            - Links: url, openAccessPdf
            - Publication: venue, publicationVenue, publicationDate
            - Identifiers: externalIds (includes DOI, PubMed ID, arXiv ID, etc.)
        year_range: Optional tuple of (min_year, max_year) to filter by publication year.
            Example: (2020, 2023) for papers from 2020-2023

    Returns:
        List of paper metadata dictionaries, each containing:
        - s2_id (str): Semantic Scholar paper ID
        - title (str): Paper title
        - abstract (str): Abstract text
        - authors (list[str]): List of author names
        - year (int | None): Publication year
        - citation_count (int): Number of citations
        - influential_citation_count (int): Number of influential citations
        - venue (str): Publication venue
        - url (str): Semantic Scholar URL
        - pdf_url (str | None): Link to open access PDF if available
        - external_ids (dict): External identifiers (DOI, PubMed, arXiv, etc.)

    Example:
        >>> # Basic search
        >>> results = search_semantic_scholar("transformers attention mechanism", max_results=5)
        >>> for paper in results:
        ...     print(f"{paper['title']} ({paper['year']})")
        ...     print(f"Citations: {paper['citation_count']}")
        ...     print(f"PDF: {paper['pdf_url']}")

        >>> # Search with year filter
        >>> results = search_semantic_scholar(
        ...     "machine learning",
        ...     max_results=10,
        ...     year_range=(2022, 2024)
        ... )

        >>> # Custom fields
        >>> results = search_semantic_scholar(
        ...     "protein structure prediction",
        ...     fields=["title", "abstract", "authors", "citationCount", "openAccessPdf"]
        ... )

    Note:
        - Free API with generous rate limits
        - Optional API key increases rate limits
        - Set SEMANTIC_SCHOLAR_API_KEY environment variable for higher limits
        - Provides citation metrics and open access PDF links
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    # Get API key if available
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    # Limit max_results
    max_results = min(max_results, 100)

    # Set default fields if not provided
    if fields is None:
        fields = [
            "paperId",
            "title",
            "abstract",
            "authors",
            "year",
            "citationCount",
            "influentialCitationCount",
            "venue",
            "url",
            "openAccessPdf",
            "externalIds",
            "publicationDate",
        ]

    params = {
        "query": query,
        "limit": max_results,
        "fields": ",".join(fields),
    }

    # Add year filter if specified
    if year_range:
        min_year, max_year = year_range
        params["year"] = f"{min_year}-{max_year}"

    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        papers = []
        for paper in data.get("data", []):
            paper_data = _parse_semantic_scholar_paper(paper)
            papers.append(paper_data)

        return papers

    except requests.RequestException as e:
        return [{"error": f"Semantic Scholar API request failed: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Unexpected error during Semantic Scholar search: {str(e)}"}]


def _parse_semantic_scholar_paper(paper: dict[str, Any]) -> dict[str, Any]:
    """Parse Semantic Scholar API response into a structured dictionary.

    Args:
        paper: Paper dictionary from Semantic Scholar API.

    Returns:
        Standardized paper metadata dictionary.
    """
    # Extract basic information
    s2_id = paper.get("paperId", "Unknown")
    title = paper.get("title", "No title")
    abstract = paper.get("abstract", "No abstract available")
    year = paper.get("year")
    venue = paper.get("venue", "Unknown venue")
    url = paper.get("url", f"https://www.semanticscholar.org/paper/{s2_id}")
    publication_date = paper.get("publicationDate", "Unknown date")

    # Extract authors
    authors = []
    for author in paper.get("authors", []):
        author_name = author.get("name", "Unknown")
        authors.append(author_name)

    # Extract citation metrics
    citation_count = paper.get("citationCount", 0)
    influential_citation_count = paper.get("influentialCitationCount", 0)

    # Extract PDF URL if available
    pdf_url = None
    open_access = paper.get("openAccessPdf")
    if open_access and isinstance(open_access, dict):
        pdf_url = open_access.get("url")

    # Extract external IDs (DOI, PubMed, arXiv, etc.)
    external_ids = paper.get("externalIds", {})

    # Extract specific external IDs for convenience
    doi = external_ids.get("DOI") if external_ids else None
    pmid = external_ids.get("PubMed") if external_ids else None
    arxiv_id = external_ids.get("ArXiv") if external_ids else None

    return {
        "s2_id": s2_id,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "year": year,
        "citation_count": citation_count,
        "influential_citation_count": influential_citation_count,
        "venue": venue,
        "publication_date": publication_date,
        "url": url,
        "pdf_url": pdf_url,
        "external_ids": external_ids,
        "doi": doi,
        "pmid": pmid,
        "arxiv_id": arxiv_id,
    }
