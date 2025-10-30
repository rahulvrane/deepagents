"""
Deep Research System - Quick Start Guide

This file provides a simple, quick way to get started with the deep research system.
Copy and modify this template for your own research needs.
"""

import os
import json
from pathlib import Path
from examples.deep_research_system import create_deep_research_agent


def quick_research(question: str, thread_id: str = "quick-research"):
    """
    Run a quick research query and display results.

    Args:
        question: The research question to investigate
        thread_id: Unique identifier for this research session

    Returns:
        The agent result object
    """
    # Verify API keys are set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Please set it in your environment:\n"
            "export ANTHROPIC_API_KEY='your-key'"
        )

    if not os.environ.get("TAVILY_API_KEY"):
        raise ValueError(
            "TAVILY_API_KEY not set. Please set it in your environment:\n"
            "export TAVILY_API_KEY='your-key'"
        )

    # Create the agent
    print("Initializing deep research system...")
    agent = create_deep_research_agent()

    # Configure the session
    config = {"configurable": {"thread_id": thread_id}}

    # Run the research
    print(f"\nResearch question: {question}")
    print("\nStarting research (this may take several minutes)...")
    print("-" * 80)

    result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config=config)

    print("-" * 80)
    print("\n✓ Research complete!\n")

    return result


def display_research_summary():
    """Display a summary of the research outputs."""
    print("=" * 80)
    print("RESEARCH SUMMARY")
    print("=" * 80)

    # Check what files were created
    research_files = {
        "research_question.txt": "Research Question",
        "research_plan.md": "Research Plan",
        "findings.md": "Research Findings",
        "citations.json": "Citation Database",
        "analysis.md": "Deep Analysis",
        "quality_report.md": "Quality Assessment",
        "synthesis.md": "Synthesized Narrative",
        "final_report.md": "Final Report",
    }

    print("\nGenerated Files:")
    for filename, description in research_files.items():
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print(f"  ✓ {description:25} ({filename}) - {size:,} bytes")
        else:
            print(f"  ✗ {description:25} ({filename}) - not created")

    # Display citation statistics
    if Path("citations.json").exists():
        print("\nCitation Statistics:")
        with open("citations.json") as f:
            data = json.load(f)
            citations = data.get("citations", [])
            print(f"  Total sources cited: {len(citations)}")

            if citations:
                # Count by type
                types = {}
                for c in citations:
                    t = c.get("content_type", "unknown")
                    types[t] = types.get(t, 0) + 1

                print("  By type:")
                for t, count in sorted(types.items()):
                    print(f"    - {t}: {count}")

                # Count with DOI
                with_doi = sum(1 for c in citations if c.get("doi") and "N/A" not in c.get("doi", ""))
                print(f"  Sources with DOI: {with_doi}")

    # Display a preview of the final report
    if Path("final_report.md").exists():
        print("\nFinal Report Preview:")
        print("-" * 80)
        with open("final_report.md") as f:
            content = f.read()
            # Show first 1000 characters
            preview = content[:1000]
            print(preview)
            if len(content) > 1000:
                print(f"\n... (+ {len(content) - 1000} more characters)")
        print("-" * 80)

    print("\n✓ Research summary complete!")
    print("\nTo view full results, open the generated markdown files.")


def main():
    """Main function demonstrating quick start usage."""
    print("\n" + "=" * 80)
    print("DEEP RESEARCH SYSTEM - QUICK START")
    print("=" * 80 + "\n")

    # Example research question
    # Modify this to your research question
    question = """
    Research the state of autonomous vehicles in 2024-2025.
    Include: current capabilities, leading companies, safety records,
    regulatory status, and timeline to widespread adoption.
    """

    try:
        # Run the research
        result = quick_research(question, thread_id="quickstart-demo")

        # Display summary
        display_research_summary()

        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("\n1. Review the final_report.md for the complete research output")
        print("2. Check citations.json for detailed source information")
        print("3. Examine analysis.md for deep insights")
        print("4. Review quality_report.md to see quality assessment")
        print("\nTo run your own research:")
        print("  1. Modify the 'question' variable in this script")
        print("  2. Run: python examples/deep_research_quickstart.py")
        print("\nOr use in your code:")
        print("  from examples.deep_research_quickstart import quick_research")
        print("  result = quick_research('Your question here')")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure ANTHROPIC_API_KEY is set")
        print("  2. Ensure TAVILY_API_KEY is set")
        print("  3. Check your internet connection")
        print("  4. Verify deepagents is installed: pip install deepagents")
        print()


# Template for custom research scripts
def custom_research_template():
    """
    Template function showing how to customize research parameters.
    Copy and modify this for your specific needs.
    """
    # Step 1: Define your research question
    research_question = """
    Your detailed research question here.

    Include:
    - Specific aspects to cover
    - Desired depth of analysis
    - Any particular perspectives needed
    - Timeline or scope
    """

    # Step 2: Set up the agent
    agent = create_deep_research_agent()

    # Step 3: Configure the session
    # Use a unique thread_id for each research project
    config = {"configurable": {"thread_id": "my-research-project-001"}}

    # Step 4: Run the research
    result = agent.invoke(
        {"messages": [{"role": "user", "content": research_question}]}, config=config
    )

    # Step 5: Access results
    # The final report is in final_report.md
    # Citations are in citations.json
    # Analysis is in analysis.md

    # Step 6: (Optional) Follow-up research
    # You can continue the conversation with follow-up questions:
    # follow_up = "Please expand on the section about X"
    # result = agent.invoke(
    #     {"messages": result["messages"] + [{"role": "user", "content": follow_up}]},
    #     config=config
    # )

    return result


def batch_research_template():
    """
    Template showing how to run multiple research queries in batch.
    """
    research_questions = [
        "Question 1: ...",
        "Question 2: ...",
        "Question 3: ...",
    ]

    agent = create_deep_research_agent()

    results = []
    for i, question in enumerate(research_questions, 1):
        print(f"\nResearching question {i}/{len(research_questions)}...")

        # Use unique thread_id for each question
        config = {"configurable": {"thread_id": f"batch-research-{i}"}}

        result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config=config)

        results.append(result)

        # Rename output files to avoid overwriting
        if Path("final_report.md").exists():
            Path("final_report.md").rename(f"final_report_{i}.md")
        if Path("citations.json").exists():
            Path("citations.json").rename(f"citations_{i}.json")

        print(f"✓ Question {i} complete. Files saved with suffix _{i}")

    return results


if __name__ == "__main__":
    # Run the quick start demonstration
    main()

    # Uncomment to see template examples:
    # print("\n" + "="*80)
    # print("CUSTOM RESEARCH TEMPLATE")
    # print("="*80)
    # print(inspect.getsource(custom_research_template))

    # print("\n" + "="*80)
    # print("BATCH RESEARCH TEMPLATE")
    # print("="*80)
    # print(inspect.getsource(batch_research_template))
