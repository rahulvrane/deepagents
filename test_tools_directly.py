#!/usr/bin/env python3
"""Test Phase 1 tools directly without requiring full agent setup.

This tests the literature search tools in isolation to verify they work correctly.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepagents.tools.literature import (
    search_pubmed,
    search_arxiv,
    search_semantic_scholar,
)


def test_pubmed():
    """Test PubMed search directly."""
    print("=" * 80)
    print("TEST 1: PubMed Search")
    print("=" * 80)
    print()
    print("Searching PubMed for 'CRISPR cancer therapy'...")
    print()

    try:
        results = search_pubmed.invoke({
            "query": "CRISPR cancer therapy",
            "max_results": 3,
            "sort": "relevance"
        })

        if isinstance(results, list) and len(results) > 0:
            if "error" in results[0]:
                print(f"❌ Error: {results[0]['error']}")
                return False

            print(f"✅ Found {len(results)} papers:")
            print()

            for i, paper in enumerate(results, 1):
                print(f"{i}. {paper.get('title', 'No title')}")
                print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}")
                print(f"   Journal: {paper.get('journal', 'Unknown')}")
                print(f"   Date: {paper.get('publication_date', 'Unknown')}")
                print(f"   PMID: {paper.get('pmid', 'Unknown')}")
                print(f"   Abstract: {paper.get('abstract', 'No abstract')[:150]}...")
                print()

            return True
        else:
            print(f"⚠️  No results returned: {results}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arxiv():
    """Test arXiv search directly."""
    print("=" * 80)
    print("TEST 2: arXiv Search")
    print("=" * 80)
    print()
    print("Searching arXiv for 'machine learning protein structure'...")
    print()

    try:
        results = search_arxiv.invoke({
            "query": "machine learning protein structure",
            "max_results": 3,
        })

        if isinstance(results, list) and len(results) > 0:
            if "error" in results[0]:
                print(f"❌ Error: {results[0]['error']}")
                return False

            print(f"✅ Found {len(results)} papers:")
            print()

            for i, paper in enumerate(results, 1):
                print(f"{i}. {paper.get('title', 'No title')}")
                print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}")
                print(f"   arXiv ID: {paper.get('arxiv_id', 'Unknown')}")
                print(f"   Categories: {', '.join(paper.get('categories', []))}")
                print(f"   Published: {paper.get('publication_date', 'Unknown')[:10]}")
                print(f"   PDF: {paper.get('pdf_url', 'No URL')}")
                print(f"   Abstract: {paper.get('abstract', 'No abstract')[:150]}...")
                print()

            return True
        else:
            print(f"⚠️  No results returned: {results}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_scholar():
    """Test Semantic Scholar search directly."""
    print("=" * 80)
    print("TEST 3: Semantic Scholar Search")
    print("=" * 80)
    print()
    print("Searching Semantic Scholar for 'deep learning drug discovery'...")
    print()

    try:
        results = search_semantic_scholar.invoke({
            "query": "deep learning drug discovery",
            "max_results": 3,
        })

        if isinstance(results, list) and len(results) > 0:
            if "error" in results[0]:
                print(f"❌ Error: {results[0]['error']}")
                return False

            print(f"✅ Found {len(results)} papers:")
            print()

            for i, paper in enumerate(results, 1):
                print(f"{i}. {paper.get('title', 'No title')}")
                print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}")
                print(f"   Year: {paper.get('year', 'Unknown')}")
                print(f"   Citations: {paper.get('citation_count', 0)}")
                print(f"   Venue: {paper.get('venue', 'Unknown')}")
                if paper.get('doi'):
                    print(f"   DOI: {paper.get('doi')}")
                if paper.get('pdf_url'):
                    print(f"   PDF: {paper.get('pdf_url')}")
                print(f"   Abstract: {paper.get('abstract', 'No abstract')[:150]}...")
                print()

            return True
        else:
            print(f"⚠️  No results returned: {results}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print()
    print("=" * 80)
    print("PHASE 1 DIRECT TOOL TESTS")
    print("Testing literature search tools without full agent")
    print("=" * 80)
    print()

    results = []

    # Test PubMed
    results.append(("PubMed", test_pubmed()))
    print()

    # Test arXiv
    results.append(("arXiv", test_arxiv()))
    print()

    # Test Semantic Scholar
    results.append(("Semantic Scholar", test_semantic_scholar()))
    print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")

    print()

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("🎉 All tests PASSED!")
        print()
        print("Phase 1 Literature Search tools are working correctly!")
        print("The tools successfully:")
        print("  ✓ Connect to PubMed API")
        print("  ✓ Connect to arXiv API")
        print("  ✓ Connect to Semantic Scholar API")
        print("  ✓ Parse and return structured data")
        print("  ✓ Handle errors gracefully")
        return 0
    else:
        print("⚠️  Some tests failed. Check output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
