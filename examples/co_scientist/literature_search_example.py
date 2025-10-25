"""Example: Using LiteratureSearchMiddleware to search scientific papers.

This example demonstrates how to use the Literature Search middleware to:
1. Search for papers across multiple databases
2. Download papers
3. Parse PDF content
4. Extract references

Run this example:
    python examples/co_scientist/literature_search_example.py

Requirements:
    - ANTHROPIC_API_KEY environment variable
    - Optional: NCBI_EMAIL for PubMed
    - Optional: pip install pymupdf (for PDF parsing)
"""

import os

from deepagents import create_deep_agent
from deepagents.middleware.scientific import LiteratureSearchMiddleware


def main():
    """Run literature search example."""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Get your key from: https://console.anthropic.com/")
        return

    print("="  * 70)
    print("Co-Scientist Literature Search Example")
    print("=" * 70)

    # Create agent with literature search middleware
    print("\n1. Creating agent with LiteratureSearchMiddleware...")
    agent = create_deep_agent(
        middleware=[LiteratureSearchMiddleware()],
        system_prompt="You are a scientific research assistant helping with literature review.",
    )
    print("✓ Agent created successfully\n")

    # Example 1: Search PubMed
    print("="  * 70)
    print("Example 1: Searching PubMed for CRISPR papers")
    print("=" * 70)

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": """Search PubMed for papers about CRISPR gene editing in cancer therapy.
            Find the 5 most relevant papers and summarize the key findings from their abstracts."""
        }]
    })

    print("\nAgent Response:")
    print("-" * 70)
    print(result["messages"][-1].content)

    # Example 2: Search arXiv
    print("\n" + "=" * 70)
    print("Example 2: Searching arXiv for machine learning papers")
    print("=" * 70)

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": """Search arXiv for recent papers on protein structure prediction using machine learning.
            Focus on papers from the last 2 years. Find 3 relevant papers."""
        }]
    })

    print("\nAgent Response:")
    print("-" * 70)
    print(result["messages"][-1].content)

    # Example 3: Multi-database search
    print("\n" + "=" * 70)
    print("Example 3: Searching multiple databases")
    print("=" * 70)

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": """I'm researching applications of transformers in genomics.
            Search PubMed, arXiv, and Semantic Scholar for relevant papers.
            Compare what you find in each database and identify the most cited papers."""
        }]
    })

    print("\nAgent Response:")
    print("-" * 70)
    print(result["messages"][-1].content)

    # Example 4: Download and parse (optional - requires PDF library)
    print("\n" + "=" * 70)
    print("Example 4: Download and parse paper (if PDF library available)")
    print("=" * 70)

    try:
        import pymupdf
        print("PyMuPDF is available - will attempt PDF download and parsing")

        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": """Find an interesting paper on arXiv about neural networks (any recent paper).
                Download the PDF and extract the abstract and introduction sections for me."""
            }]
        })

        print("\nAgent Response:")
        print("-" * 70)
        print(result["messages"][-1].content)

    except ImportError:
        print("PyMuPDF not installed - skipping PDF parsing example")
        print("To enable: pip install pymupdf")

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
