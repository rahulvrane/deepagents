"""PDF download and parsing tools for scientific papers."""

import os
import re
from pathlib import Path
from typing import Any

import requests
from langchain_core.tools import tool
from langchain.tools import ToolRuntime

# Try to import PDF libraries (graceful degradation)
try:
    import pymupdf  # PyMuPDF (fitz)
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


@tool
def download_paper(
    paper_id: str,
    source: str = "auto",
    runtime: ToolRuntime | None = None,
) -> str:
    """Download a scientific paper PDF and save to filesystem.

    This tool downloads scientific papers from various sources and stores them
    in the /papers/ directory for later reading and analysis.

    Args:
        paper_id: Identifier for the paper:
            - For PubMed: PMID (e.g., "12345678") or PMC ID (e.g., "PMC1234567")
            - For arXiv: arXiv ID (e.g., "2301.12345" or "1706.03762")
            - For DOI: Full DOI (e.g., "10.1038/nature12345")
            - For direct URL: Full PDF URL
        source: Source of the paper. Options:
            - "auto": Auto-detect from paper_id format
            - "pubmed": PubMed Central
            - "arxiv": arXiv
            - "doi": DOI resolver
            - "url": Direct URL
        runtime: Tool runtime for filesystem access (optional).

    Returns:
        String message indicating success with file path, or error message.

    Example:
        >>> # Download from arXiv
        >>> result = download_paper("2301.12345", source="arxiv")
        >>> # Returns: "Downloaded paper to /papers/2301.12345.pdf"

        >>> # Download from PubMed Central
        >>> result = download_paper("PMC8234567", source="pubmed")

        >>> # Auto-detect source
        >>> result = download_paper("10.1038/nature12345", source="auto")

        >>> # Direct URL
        >>> result = download_paper("https://example.com/paper.pdf", source="url")

    Note:
        - Requires write access to /papers/ directory
        - PubMed Central: Not all papers have free PDFs
        - arXiv: All papers have free PDFs
        - Respects copyright and usage policies
        - File names are sanitized for filesystem compatibility
    """
    # Auto-detect source if not specified
    if source == "auto":
        source = _detect_paper_source(paper_id)

    try:
        # Get PDF URL based on source
        if source == "arxiv":
            pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
            filename = f"{paper_id.replace('/', '-')}.pdf"
        elif source == "pubmed":
            # Try to get PDF from PubMed Central
            if paper_id.startswith("PMC"):
                pmc_id = paper_id.replace("PMC", "")
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/"
                filename = f"PMC{pmc_id}.pdf"
            else:
                # PMID - try to convert to PMC ID first
                return f"Error: PMID {paper_id} cannot be directly downloaded. Please provide PMC ID or use DOI."
        elif source == "doi":
            # Use Unpaywall or Sci-Hub (if available)
            return _download_via_doi(paper_id)
        elif source == "url":
            pdf_url = paper_id  # paper_id is actually the URL
            # Extract filename from URL
            filename = paper_id.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename = f"{_sanitize_filename(filename)}.pdf"
        else:
            return f"Error: Unsupported source '{source}'"

        # Download the PDF
        response = requests.get(pdf_url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        # Check if response is actually a PDF
        content_type = response.headers.get("Content-Type", "")
        if "application/pdf" not in content_type and not response.content.startswith(b"%PDF"):
            return f"Error: Retrieved content is not a PDF (Content-Type: {content_type})"

        # Save to /papers/ directory
        papers_dir = Path("/papers")
        # In filesystem middleware, this would be virtual
        # For now, create relative path for testing
        if not papers_dir.exists():
            papers_dir = Path("papers")
            papers_dir.mkdir(exist_ok=True)

        file_path = papers_dir / filename
        with open(file_path, "wb") as f:
            f.write(response.content)

        return f"Downloaded paper to /{papers_dir.name}/{filename} ({len(response.content)} bytes)"

    except requests.RequestException as e:
        return f"Error downloading paper: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@tool
def parse_scientific_pdf(
    file_path: str,
    extract_sections: bool = True,
) -> dict[str, Any]:
    """Parse a scientific PDF and extract structured information.

    This tool extracts text, metadata, and optionally identifies sections
    from a scientific paper PDF.

    Args:
        file_path: Path to PDF file (e.g., "/papers/paper.pdf").
        extract_sections: Whether to attempt to identify paper sections
            (Abstract, Introduction, Methods, Results, Discussion, etc.).

    Returns:
        Dictionary containing:
        - text (str): Full extracted text
        - num_pages (int): Number of pages
        - metadata (dict): PDF metadata (title, author, etc.)
        - sections (dict): Extracted sections if extract_sections=True
        - references (list): Extracted references if found

    Example:
        >>> result = parse_scientific_pdf("/papers/2301.12345.pdf")
        >>> print(f"Title: {result['metadata'].get('title', 'Unknown')}")
        >>> print(f"Pages: {result['num_pages']}")
        >>> print(f"Abstract: {result['sections'].get('abstract', 'Not found')[:200]}...")

    Note:
        - Requires pymupdf (PyMuPDF) or pdfplumber
        - Quality varies with PDF structure
        - Scanned PDFs require OCR (not included)
        - Section extraction is heuristic-based
    """
    if not PYMUPDF_AVAILABLE and not PDFPLUMBER_AVAILABLE:
        return {
            "error": "PDF parsing libraries not available. Install pymupdf or pdfplumber: pip install pymupdf"
        }

    try:
        if PYMUPDF_AVAILABLE:
            return _parse_with_pymupdf(file_path, extract_sections)
        else:
            return _parse_with_pdfplumber(file_path, extract_sections)

    except FileNotFoundError:
        return {"error": f"File not found: {file_path}"}
    except Exception as e:
        return {"error": f"Error parsing PDF: {str(e)}"}


@tool
def extract_references(file_path: str) -> list[str]:
    """Extract bibliography/references from a scientific paper PDF.

    This tool attempts to extract the references section from a PDF
    and parse individual citations.

    Args:
        file_path: Path to PDF file.

    Returns:
        List of reference strings, or error message.

    Example:
        >>> refs = extract_references("/papers/paper.pdf")
        >>> for i, ref in enumerate(refs[:5], 1):
        ...     print(f"{i}. {ref[:100]}...")

    Note:
        - Accuracy depends on PDF structure
        - May include some false positives
        - Citations may not be perfectly formatted
    """
    try:
        # First extract full text
        parsed = parse_scientific_pdf(file_path, extract_sections=True)
        if "error" in parsed:
            return [f"Error: {parsed['error']}"]

        text = parsed.get("text", "")

        # Try to find references section
        references = _extract_references_from_text(text)

        if not references:
            return ["No references found in document"]

        return references

    except Exception as e:
        return [f"Error extracting references: {str(e)}"]


# Helper functions

def _detect_paper_source(paper_id: str) -> str:
    """Auto-detect the source of a paper based on its ID format."""
    if paper_id.startswith("http://") or paper_id.startswith("https://"):
        return "url"
    elif re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", paper_id):  # arXiv format
        return "arxiv"
    elif paper_id.startswith("PMC") or paper_id.isdigit():
        return "pubmed"
    elif "/" in paper_id or paper_id.startswith("10."):  # DOI format
        return "doi"
    else:
        return "url"  # Assume URL as fallback


def _sanitize_filename(filename: str) -> str:
    """Sanitize a string to be a valid filename."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def _download_via_doi(doi: str) -> str:
    """Attempt to download PDF via DOI using Unpaywall."""
    # Try Unpaywall first
    email = os.getenv("UNPAYWALL_EMAIL", "user@example.com")
    unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email={email}"

    try:
        response = requests.get(unpaywall_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check for open access PDF
        best_oa = data.get("best_oa_location")
        if best_oa and best_oa.get("url_for_pdf"):
            pdf_url = best_oa["url_for_pdf"]
            # Download using the PDF URL
            return download_paper(pdf_url, source="url")
        else:
            return f"Error: No open access PDF found for DOI {doi}"

    except Exception as e:
        return f"Error retrieving DOI {doi}: {str(e)}"


def _parse_with_pymupdf(file_path: str, extract_sections: bool) -> dict[str, Any]:
    """Parse PDF using PyMuPDF."""
    import pymupdf

    doc = pymupdf.open(file_path)

    # Extract metadata
    metadata = doc.metadata

    # Extract text from all pages
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    result = {
        "text": full_text,
        "num_pages": len(doc),
        "metadata": metadata,
    }

    # Extract sections if requested
    if extract_sections:
        sections = _extract_sections_from_text(full_text)
        result["sections"] = sections

    doc.close()
    return result


def _parse_with_pdfplumber(file_path: str, extract_sections: bool) -> dict[str, Any]:
    """Parse PDF using pdfplumber."""
    import pdfplumber

    with pdfplumber.open(file_path) as pdf:
        # Extract metadata
        metadata = pdf.metadata or {}

        # Extract text from all pages
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() or ""

        result = {
            "text": full_text,
            "num_pages": len(pdf.pages),
            "metadata": metadata,
        }

        # Extract sections if requested
        if extract_sections:
            sections = _extract_sections_from_text(full_text)
            result["sections"] = sections

    return result


def _extract_sections_from_text(text: str) -> dict[str, str]:
    """Extract common paper sections from text using heuristics."""
    sections = {}

    # Common section headers
    section_patterns = {
        "abstract": r"(?i)(^|\n)\s*abstract\s*\n",
        "introduction": r"(?i)(^|\n)\s*(1\.?\s+)?introduction\s*\n",
        "methods": r"(?i)(^|\n)\s*(\d+\.?\s+)?(methods?|materials?\s+and\s+methods?)\s*\n",
        "results": r"(?i)(^|\n)\s*(\d+\.?\s+)?results?\s*\n",
        "discussion": r"(?i)(^|\n)\s*(\d+\.?\s+)?discussion\s*\n",
        "conclusion": r"(?i)(^|\n)\s*(\d+\.?\s+)?conclus(ion|ions)\s*\n",
        "references": r"(?i)(^|\n)\s*(references?|bibliography)\s*\n",
    }

    # Find section boundaries
    section_starts = {}
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, text)
        if match:
            section_starts[section_name] = match.end()

    # Extract text between sections
    sorted_sections = sorted(section_starts.items(), key=lambda x: x[1])
    for i, (section_name, start) in enumerate(sorted_sections):
        # Find end (start of next section or end of document)
        if i + 1 < len(sorted_sections):
            end = sorted_sections[i + 1][1]
        else:
            end = len(text)

        section_text = text[start:end].strip()
        # Limit section length for practicality
        if len(section_text) > 5000:
            section_text = section_text[:5000] + "... (truncated)"

        sections[section_name] = section_text

    return sections


def _extract_references_from_text(text: str) -> list[str]:
    """Extract individual references from text."""
    # Find references section
    ref_match = re.search(r"(?i)(^|\n)\s*(references?|bibliography)\s*\n", text)
    if not ref_match:
        return []

    ref_section = text[ref_match.end():]

    # Split by common reference patterns
    # Pattern: [1], 1., (1), or just new numbered items
    references = []
    current_ref = ""

    lines = ref_section.split("\n")
    for line in lines:
        # Check if line starts a new reference (numbered)
        if re.match(r"^\s*[\[\(]?\d+[\]\)\.]\s+", line):
            if current_ref:
                references.append(current_ref.strip())
            current_ref = re.sub(r"^\s*[\[\(]?\d+[\]\)\.]\s+", "", line)
        else:
            current_ref += " " + line

    # Add last reference
    if current_ref:
        references.append(current_ref.strip())

    # Filter out very short or invalid references
    references = [ref for ref in references if len(ref) > 20]

    # Limit number of references
    return references[:100]
