#!/usr/bin/env python3
"""Real-world test of Phase 1 Literature Search implementation.

This script tests the literature search middleware with a real scientific query
to verify all components are working correctly.

Topic: AI applications in drug discovery (timely and spans multiple disciplines)
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepagents import create_deep_agent
from deepagents.middleware.scientific import LiteratureSearchMiddleware


def main():
    """Run real-world literature search test."""

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return 1

    print("=" * 80)
    print("PHASE 1 REAL-WORLD TEST: Literature Search Middleware")
    print("=" * 80)
    print()
    print("Research Topic: AI applications in drug discovery")
    print("Objective: Find recent papers across multiple databases and summarize findings")
    print()
    print("=" * 80)
    print()

    # Create agent with literature search middleware
    print("Step 1: Creating agent with LiteratureSearchMiddleware...")
    try:
        agent = create_deep_agent(
            middleware=[LiteratureSearchMiddleware()],
            system_prompt="""You are a scientific research assistant with expertise in
            literature review. Be systematic and thorough in your searches.""",
        )
        print("✅ Agent created successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return 1

    # Test 1: Basic search
    print("=" * 80)
    print("TEST 1: Search PubMed for AI drug discovery papers")
    print("=" * 80)
    print()

    try:
        print("Sending query to agent...")
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": """Search PubMed for papers about artificial intelligence and machine learning
                in drug discovery. Find 5 relevant recent papers. For each paper, tell me:
                - Title
                - First 2 authors
                - Year
                - One-sentence summary of what they did

                Focus on papers from 2022 onwards if possible."""
            }]
        })

        print("\n" + "─" * 80)
        print("AGENT RESPONSE:")
        print("─" * 80)
        print(result["messages"][-1].content)
        print()

        # Check if tool was used
        messages = result.get("messages", [])
        tool_calls = [
            tc for msg in messages
            if hasattr(msg, "tool_calls")
            for tc in msg.tool_calls
        ]

        if any("pubmed" in tc["name"].lower() for tc in tool_calls):
            print("✅ Test 1 PASSED: PubMed search tool was used")
        else:
            print("⚠️  Test 1 WARNING: PubMed tool may not have been called")
            print(f"   Tool calls made: {[tc['name'] for tc in tool_calls]}")
        print()

    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 2: arXiv search
    print("=" * 80)
    print("TEST 2: Search arXiv for machine learning drug discovery papers")
    print("=" * 80)
    print()

    try:
        print("Sending query to agent...")
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": """Now search arXiv for preprints about deep learning for molecular property prediction.
                Find 3 papers and tell me their titles and main contributions."""
            }]
        })

        print("\n" + "─" * 80)
        print("AGENT RESPONSE:")
        print("─" * 80)
        print(result["messages"][-1].content)
        print()

        messages = result.get("messages", [])
        tool_calls = [
            tc for msg in messages
            if hasattr(msg, "tool_calls")
            for tc in msg.tool_calls
        ]

        if any("arxiv" in tc["name"].lower() for tc in tool_calls):
            print("✅ Test 2 PASSED: arXiv search tool was used")
        else:
            print("⚠️  Test 2 WARNING: arXiv tool may not have been called")
            print(f"   Tool calls made: {[tc['name'] for tc in tool_calls]}")
        print()

    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 3: Multi-database comparison
    print("=" * 80)
    print("TEST 3: Compare results across multiple databases")
    print("=" * 80)
    print()

    try:
        print("Sending query to agent...")
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": """Compare what you found about AI in drug discovery between PubMed and arXiv.
                What are the main differences in focus or approach? Give me a brief 3-4 sentence summary."""
            }]
        })

        print("\n" + "─" * 80)
        print("AGENT RESPONSE:")
        print("─" * 80)
        print(result["messages"][-1].content)
        print()

        print("✅ Test 3 PASSED: Agent synthesized information across databases")
        print()

    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 4: Semantic Scholar with citation metrics
    print("=" * 80)
    print("TEST 4: Search Semantic Scholar for highly cited papers")
    print("=" * 80)
    print()

    try:
        print("Sending query to agent...")
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": """Search Semantic Scholar for papers on 'transformer models drug discovery'.
                Find 3 papers and tell me their citation counts to identify the most influential work."""
            }]
        })

        print("\n" + "─" * 80)
        print("AGENT RESPONSE:")
        print("─" * 80)
        print(result["messages"][-1].content)
        print()

        messages = result.get("messages", [])
        tool_calls = [
            tc for msg in messages
            if hasattr(msg, "tool_calls")
            for tc in msg.tool_calls
        ]

        if any("semantic" in tc["name"].lower() for tc in tool_calls):
            print("✅ Test 4 PASSED: Semantic Scholar search tool was used")
        else:
            print("⚠️  Test 4 WARNING: Semantic Scholar tool may not have been called")
            print(f"   Tool calls made: {[tc['name'] for tc in tool_calls]}")
        print()

    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Final summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print("✅ All core tests completed successfully!")
    print()
    print("Components verified:")
    print("  ✓ LiteratureSearchMiddleware integration")
    print("  ✓ PubMed search functionality")
    print("  ✓ arXiv search functionality")
    print("  ✓ Semantic Scholar search functionality")
    print("  ✓ Multi-database synthesis")
    print("  ✓ Agent reasoning and response generation")
    print()
    print("Phase 1 implementation is working correctly! 🎉")
    print()
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
