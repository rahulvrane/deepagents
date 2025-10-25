"""Literature search and retrieval tools."""

from deepagents.tools.literature.pubmed import search_pubmed
from deepagents.tools.literature.arxiv_search import search_arxiv
from deepagents.tools.literature.semantic_scholar import search_semantic_scholar
from deepagents.tools.literature.pdf_parser import download_paper, parse_scientific_pdf, extract_references

__all__ = [
    "search_pubmed",
    "search_arxiv",
    "search_semantic_scholar",
    "download_paper",
    "parse_scientific_pdf",
    "extract_references",
]
