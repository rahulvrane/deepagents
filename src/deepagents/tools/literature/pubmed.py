"""PubMed search integration using NCBI E-utilities API."""

import os
from typing import Any
from xml.etree import ElementTree

import requests
from langchain_core.tools import tool


@tool
def search_pubmed(
    query: str,
    max_results: int = 10,
    sort: str = "relevance",
) -> list[dict[str, Any]]:
    """Search PubMed database for biomedical literature.

    This tool searches the PubMed database (maintained by NCBI) for scientific
    papers in biomedicine and life sciences. It returns metadata including titles,
    abstracts, authors, and publication details.

    Args:
        query: Search query string. Supports PubMed query syntax including:
            - Boolean operators: AND, OR, NOT
            - Field tags: [Title], [Author], [Journal], [MeSH Terms]
            - Date ranges: ("2020/01/01"[Date - Publication] : "2023/12/31"[Date - Publication])
            Examples:
            - "CRISPR AND cancer"
            - "machine learning[Title] AND protein structure"
            - "Nature[Journal]"
        max_results: Maximum number of results to return (default: 10, max: 100).
        sort: Sort order - 'relevance', 'date', or 'citations' (default: 'relevance').

    Returns:
        List of paper metadata dictionaries, each containing:
        - pmid (str): PubMed ID
        - title (str): Paper title
        - authors (list[str]): List of author names
        - abstract (str): Abstract text
        - journal (str): Journal name
        - publication_date (str): Date of publication
        - doi (str | None): Digital Object Identifier
        - url (str): Link to PubMed page

    Example:
        >>> results = search_pubmed("CRISPR gene editing cancer", max_results=5)
        >>> for paper in results:
        ...     print(f"{paper['title']} - {paper['journal']} ({paper['publication_date']})")
        ...     print(f"Authors: {', '.join(paper['authors'][:3])}")
        ...     print(f"URL: {paper['url']}")

    Note:
        - Requires internet connection
        - Respects NCBI usage guidelines
        - Rate limits: 3 requests/second without API key, 10 requests/second with key
        - Set NCBI_API_KEY and NCBI_EMAIL environment variables for better rate limits
    """
    # Get API credentials from environment
    api_key = os.getenv("NCBI_API_KEY")
    email = os.getenv("NCBI_EMAIL", "user@example.com")

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    # Limit max_results to prevent excessive API calls
    max_results = min(max_results, 100)

    # Map sort parameter to PubMed sort values
    sort_mapping = {
        "relevance": "relevance",
        "date": "pub_date",
        "citations": "pub_date",  # PubMed doesn't have citation sort, use date
    }
    sort_param = sort_mapping.get(sort, "relevance")

    # Step 1: Search for PMIDs
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": sort_param,
        "email": email,
    }
    if api_key:
        search_params["api_key"] = api_key

    try:
        search_response = requests.get(search_url, params=search_params, timeout=30)
        search_response.raise_for_status()
        search_data = search_response.json()

        pmids = search_data.get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return []

        # Step 2: Fetch details for PMIDs
        fetch_url = f"{base_url}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "email": email,
        }
        if api_key:
            fetch_params["api_key"] = api_key

        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=30)
        fetch_response.raise_for_status()

        # Parse XML response
        root = ElementTree.fromstring(fetch_response.content)
        papers = []

        for article in root.findall(".//PubmedArticle"):
            paper_data = _parse_pubmed_article(article)
            if "error" not in paper_data:
                papers.append(paper_data)

        return papers

    except requests.RequestException as e:
        return [{"error": f"PubMed API request failed: {str(e)}"}]
    except ElementTree.ParseError as e:
        return [{"error": f"Failed to parse PubMed XML response: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Unexpected error during PubMed search: {str(e)}"}]


def _parse_pubmed_article(article: ElementTree.Element) -> dict[str, Any]:
    """Parse a PubMed article XML element into a structured dictionary.

    Args:
        article: XML Element representing a PubMed article.

    Returns:
        Dictionary with paper metadata.
    """
    try:
        medline_citation = article.find(".//MedlineCitation")
        if medline_citation is None:
            return {"error": "Invalid article format: MedlineCitation not found"}

        # Extract PMID
        pmid_elem = medline_citation.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

        article_elem = medline_citation.find(".//Article")
        if article_elem is None:
            return {"pmid": pmid, "error": "No article data found"}

        # Extract title
        title_elem = article_elem.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else "No title available"

        # Extract abstract
        abstract_elem = article_elem.find(".//Abstract/AbstractText")
        if abstract_elem is not None:
            # Handle structured abstracts
            if abstract_elem.text:
                abstract = abstract_elem.text
            else:
                # Combine all abstract text elements
                abstract_parts = []
                for part in article_elem.findall(".//Abstract/AbstractText"):
                    label = part.get("Label", "")
                    text = part.text or ""
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                abstract = " ".join(abstract_parts)
        else:
            abstract = "No abstract available"

        # Extract authors
        authors = []
        author_list = article_elem.find(".//AuthorList")
        if author_list is not None:
            for author in author_list.findall(".//Author"):
                last_name = author.find(".//LastName")
                fore_name = author.find(".//ForeName")
                if last_name is not None and fore_name is not None:
                    authors.append(f"{fore_name.text} {last_name.text}")
                elif last_name is not None:
                    authors.append(last_name.text)

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

    except Exception as e:
        return {"error": f"Error parsing article: {str(e)}"}
