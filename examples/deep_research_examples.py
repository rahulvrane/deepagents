"""
Deep Research System - Usage Examples

This file demonstrates various use cases for the deep research system,
showing how to leverage its specialized agents for different research scenarios.
"""

import json
import os
from pathlib import Path

from langchain_core.messages import HumanMessage

from examples.deep_research_system import create_deep_research_agent


def example_1_basic_research():
    """Example 1: Basic research on a technology topic."""
    print("\n" + "=" * 80)
    print("Example 1: Basic Research - AI in Healthcare")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-1-ai-healthcare"}}

    messages = [
        HumanMessage(
            content="Research the impact of AI on healthcare diagnostics in 2024-2025"
        )
    ]

    print("Starting research...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")
    print(f"Total messages exchanged: {len(result['messages'])}")
    print("\nFinal response:")
    print(result["messages"][-1].content[:500] + "...")

    # Show what files were created
    print("\nFiles created during research:")
    research_files = [
        "research_question.txt",
        "research_plan.md",
        "findings.md",
        "citations.json",
        "analysis.md",
        "quality_report.md",
        "synthesis.md",
        "final_report.md",
    ]

    for file in research_files:
        if Path(file).exists():
            print(f"  ✓ {file}")


def example_2_comparative_analysis():
    """Example 2: Comparative research with detailed analysis."""
    print("\n" + "=" * 80)
    print("Example 2: Comparative Analysis - Quantum vs Classical Computing")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-2-quantum-computing"}}

    messages = [
        HumanMessage(
            content="""
            Compare quantum computing and classical computing for drug discovery applications.

            Please include:
            1. Overview of each approach
            2. Strengths and limitations
            3. Current state of technology
            4. Timeline to practical deployment
            5. Cost considerations
            6. Key research institutions and companies

            Provide a comprehensive analysis with specific examples.
            """
        )
    ]

    print("Starting comparative research...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")

    # Access and display citation information
    if Path("citations.json").exists():
        with open("citations.json") as f:
            citations_data = json.load(f)
            print(f"\nTotal sources cited: {len(citations_data.get('citations', []))}")
            print("\nSample citations:")
            for citation in citations_data.get("citations", [])[:3]:
                print(f"\n  [{citation['id']}] {citation['title']}")
                print(f"      URL: {citation['url']}")
                print(f"      Why used: {citation.get('why_used', 'N/A')}")
                print(
                    f"      Reliability: {citation.get('reliability_score', 'N/A')}"
                )


def example_3_trend_analysis():
    """Example 3: Analyzing trends over time."""
    print("\n" + "=" * 80)
    print("Example 3: Trend Analysis - Climate Tech Developments")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-3-climate-tech"}}

    messages = [
        HumanMessage(
            content="""
            Analyze the major developments in climate technology from 2023-2025.

            Focus on:
            - Carbon capture and storage innovations
            - Renewable energy breakthroughs
            - Climate monitoring technology
            - Major funding and investment trends
            - Policy changes affecting climate tech

            Identify patterns, key players, and future trajectory.
            """
        )
    ]

    print("Starting trend analysis...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")

    # Display analysis insights
    if Path("analysis.md").exists():
        with open("analysis.md") as f:
            analysis = f.read()
            print("\nAnalysis file created (first 500 chars):")
            print(analysis[:500] + "...")


def example_4_market_research():
    """Example 4: Market research with multiple dimensions."""
    print("\n" + "=" * 80)
    print("Example 4: Market Research - Edge AI Chips")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-4-edge-ai"}}

    messages = [
        HumanMessage(
            content="""
            Research the edge AI chip market for 2024-2025.

            Cover these aspects:
            1. Market size and growth projections
            2. Key players and their products
            3. Technical specifications and capabilities
            4. Target applications and use cases
            5. Competitive landscape
            6. Barriers to adoption
            7. Future outlook

            Provide specific data points, company names, and product examples.
            """
        )
    ]

    print("Starting market research...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")


def example_5_academic_research():
    """Example 5: Academic-style research with heavy citation requirements."""
    print("\n" + "=" * 80)
    print("Example 5: Academic Research - Transformer Architecture Evolution")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-5-transformers"}}

    messages = [
        HumanMessage(
            content="""
            Research the evolution of transformer architectures from 2017-2025.

            Requirements:
            - Track the progression from original transformers to modern variants
            - Include key papers and their contributions
            - Identify breakthrough innovations and their impact
            - Analyze performance improvements over time
            - Cover different variants (BERT, GPT, T5, etc.)
            - Discuss current state-of-the-art

            This should be academic-level research with comprehensive citations.
            Please prioritize academic papers and include DOI where available.
            """
        )
    ]

    print("Starting academic research...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")

    # Show detailed citation tracking
    if Path("citations.json").exists():
        with open("citations.json") as f:
            citations_data = json.load(f)
            print(f"\nTotal sources: {len(citations_data.get('citations', []))}")

            # Count by type
            types = {}
            for citation in citations_data.get("citations", []):
                ctype = citation.get("content_type", "unknown")
                types[ctype] = types.get(ctype, 0) + 1

            print("\nSources by type:")
            for ctype, count in sorted(types.items()):
                print(f"  {ctype}: {count}")

            # Show academic papers
            print("\nAcademic papers cited:")
            for citation in citations_data.get("citations", []):
                if citation.get("content_type") == "journal article":
                    print(f"\n  {citation['title']}")
                    print(f"  Authors: {', '.join(citation.get('authors', []))}")
                    print(f"  DOI: {citation.get('doi', 'N/A')}")
                    print(f"  What extracted: {citation.get('what_extracted', 'N/A')[:100]}...")


def example_6_multilingual_research():
    """Example 6: Research in a non-English language."""
    print("\n" + "=" * 80)
    print("Example 6: Multilingual Research - Spanish Language")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-6-spanish"}}

    messages = [
        HumanMessage(
            content="""
            Investiga el impacto de la inteligencia artificial en la educación
            en América Latina durante 2024-2025.

            Incluye:
            - Aplicaciones principales
            - Países líderes en adopción
            - Desafíos y barreras
            - Casos de éxito
            - Perspectivas futuras
            """
        )
    ]

    print("Starting research in Spanish...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")
    print("\nNote: The final report will be in Spanish to match the question language.")


def example_7_iterative_refinement():
    """Example 7: Demonstrate iterative refinement with follow-up questions."""
    print("\n" + "=" * 80)
    print("Example 7: Iterative Refinement - Following Up on Research")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-7-iterative"}}

    # Initial research
    messages = [
        HumanMessage(
            content="Research the basics of neuromorphic computing and its applications."
        )
    ]

    print("Step 1: Initial research on neuromorphic computing...")
    result = agent.invoke({"messages": messages}, config=config)

    # Follow-up to deepen specific aspect
    messages = result["messages"] + [
        HumanMessage(
            content="""
            Great! Now please expand the research specifically on neuromorphic
            computing applications in robotics. Provide more detailed technical
            information and recent developments.
            """
        )
    ]

    print("\nStep 2: Deepening research on robotics applications...")
    result = agent.invoke({"messages": messages}, config=config)

    # Another follow-up
    messages = result["messages"] + [
        HumanMessage(
            content="""
            Please add a section comparing neuromorphic chips from different
            manufacturers (Intel, IBM, etc.) with specific technical specs
            and benchmarks.
            """
        )
    ]

    print("\nStep 3: Adding competitive analysis...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nIterative research complete!")
    print(
        "This demonstrates how you can progressively deepen research on specific aspects."
    )


def example_8_quality_focused():
    """Example 8: Research emphasizing quality and verification."""
    print("\n" + "=" * 80)
    print("Example 8: Quality-Focused Research - Fact Verification")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-8-quality"}}

    messages = [
        HumanMessage(
            content="""
            Research the claimed benefits and actual evidence for quantum supremacy
            achievements announced by Google and IBM.

            CRITICAL: This research must prioritize accuracy and fact-checking.
            - Verify all claims with multiple sources
            - Distinguish between company announcements and peer-reviewed validation
            - Note any controversies or disputes
            - Assess the reliability of sources
            - Be clear about what is proven vs. what is claimed

            Quality and accuracy are more important than speed.
            """
        )
    ]

    print("Starting quality-focused research...")
    print("(This may take longer due to emphasis on verification)\n")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")

    # Show quality assessment
    if Path("quality_report.md").exists():
        with open("quality_report.md") as f:
            quality_report = f.read()
            print("\nQuality report excerpt:")
            print(quality_report[:600] + "...")


def example_9_structured_output():
    """Example 9: Research producing a specific structured format."""
    print("\n" + "=" * 80)
    print("Example 9: Structured Output - Technology Comparison Table")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-9-structured"}}

    messages = [
        HumanMessage(
            content="""
            Create a comprehensive comparison of the top 5 large language models
            as of 2024-2025.

            Format as a detailed table with these columns:
            - Model Name
            - Developer
            - Release Date
            - Parameters
            - Context Window
            - Key Capabilities
            - Benchmark Scores (specific tests)
            - Pricing
            - Notable Features

            Include detailed citations for all data points.
            """
        )
    ]

    print("Starting structured research...")
    result = agent.invoke({"messages": messages}, config=config)

    print("\nResearch complete!")
    print("The final report should contain a detailed comparison table.")


def example_10_comprehensive_case_study():
    """Example 10: Full case study demonstrating all system capabilities."""
    print("\n" + "=" * 80)
    print("Example 10: Comprehensive Case Study - AI Safety Landscape")
    print("=" * 80 + "\n")

    agent = create_deep_research_agent()

    config = {"configurable": {"thread_id": "example-10-comprehensive"}}

    messages = [
        HumanMessage(
            content="""
            Conduct a comprehensive research study on the AI safety landscape in 2024-2025.

            This should be a DEEP, thorough research project covering:

            1. TECHNICAL APPROACHES
               - Alignment techniques
               - Interpretability methods
               - Safety evaluation frameworks
               - Red teaming practices

            2. ORGANIZATIONS AND INITIATIVES
               - Leading research institutions
               - Major companies and their approaches
               - Government initiatives
               - International coordination efforts

            3. KEY CHALLENGES
               - Technical obstacles
               - Coordination problems
               - Resource allocation
               - Timeline pressures

            4. RECENT DEVELOPMENTS
               - Breakthrough research (2024-2025)
               - Policy changes
               - Industry standards
               - Safety incidents and lessons

            5. EXPERT PERSPECTIVES
               - Leading researchers' views
               - Industry perspectives
               - Academic consensus and debates
               - Civil society concerns

            6. FUTURE OUTLOOK
               - Predicted developments
               - Potential risks
               - Opportunities
               - Recommendations

            Requirements:
            - Comprehensive coverage of all aspects
            - Heavy citation with DOI where available
            - Multiple perspectives represented
            - Critical analysis of claims
            - Clear distinction between facts and opinions
            - Academic rigor throughout

            This is a flagship demonstration of the deep research system's capabilities.
            Take your time and produce the highest quality output.
            """
        )
    ]

    print("Starting comprehensive case study...")
    print("(This is a complex research project and will take time)\n")

    result = agent.invoke({"messages": messages}, config=config)

    print("\nCase study complete!")

    # Detailed analysis of outputs
    print("\n" + "=" * 80)
    print("Research Artifacts Summary")
    print("=" * 80)

    files = {
        "research_question.txt": "Research Question",
        "research_plan.md": "Research Plan",
        "findings.md": "Search Findings",
        "citations.json": "Citation Database",
        "analysis.md": "Deep Analysis",
        "quality_report.md": "Quality Assessment",
        "synthesis.md": "Synthesized Narrative",
        "final_report.md": "Final Report",
    }

    for filename, description in files.items():
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print(f"\n{description} ({filename}):")
            print(f"  Size: {size:,} bytes")

            if filename == "citations.json":
                with open(filename) as f:
                    data = json.load(f)
                    print(f"  Citations: {len(data.get('citations', []))}")

    if Path("citations.json").exists():
        with open("citations.json") as f:
            citations_data = json.load(f)
            print("\n" + "=" * 80)
            print("Citation Analysis")
            print("=" * 80)

            citations = citations_data.get("citations", [])
            print(f"Total sources: {len(citations)}")

            # Type distribution
            types = {}
            for c in citations:
                t = c.get("content_type", "unknown")
                types[t] = types.get(t, 0) + 1

            print("\nBy content type:")
            for t, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {t}: {count}")

            # Reliability distribution
            reliability = {}
            for c in citations:
                r = c.get("reliability_score", "unknown")
                reliability[r] = reliability.get(r, 0) + 1

            print("\nBy reliability:")
            for r, count in sorted(
                reliability.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  {r}: {count}")

            # DOI coverage
            with_doi = sum(1 for c in citations if c.get("doi") and c["doi"] != "N/A")
            print(f"\nSources with DOI: {with_doi}/{len(citations)}")

    print("\n" + "=" * 80)
    print("Case study artifacts generated successfully!")
    print("=" * 80)


def run_all_examples():
    """Run all examples in sequence."""
    examples = [
        ("Basic Research", example_1_basic_research),
        ("Comparative Analysis", example_2_comparative_analysis),
        ("Trend Analysis", example_3_trend_analysis),
        ("Market Research", example_4_market_research),
        ("Academic Research", example_5_academic_research),
        ("Multilingual Research", example_6_multilingual_research),
        ("Iterative Refinement", example_7_iterative_refinement),
        ("Quality-Focused Research", example_8_quality_focused),
        ("Structured Output", example_9_structured_output),
        ("Comprehensive Case Study", example_10_comprehensive_case_study),
    ]

    print("\n" + "=" * 80)
    print("DEEP RESEARCH SYSTEM - EXAMPLES SUITE")
    print("=" * 80)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nTo run a specific example:")
    print("  from examples.deep_research_examples import example_1_basic_research")
    print("  example_1_basic_research()")

    print("\nTo run all examples:")
    print("  from examples.deep_research_examples import run_all_examples")
    print("  run_all_examples()")

    print("\nNote: Running all examples will take significant time.")
    print("Consider running examples individually for testing.\n")


if __name__ == "__main__":
    print("Deep Research System - Examples")
    print("\nThis file contains 10 comprehensive examples demonstrating")
    print("the deep research system's capabilities.\n")

    print("Examples:")
    print("  1. Basic Research - AI in Healthcare")
    print("  2. Comparative Analysis - Quantum vs Classical Computing")
    print("  3. Trend Analysis - Climate Tech Developments")
    print("  4. Market Research - Edge AI Chips")
    print("  5. Academic Research - Transformer Architecture Evolution")
    print("  6. Multilingual Research - Spanish Language")
    print("  7. Iterative Refinement - Following Up on Research")
    print("  8. Quality-Focused Research - Fact Verification")
    print("  9. Structured Output - Technology Comparison Table")
    print(" 10. Comprehensive Case Study - AI Safety Landscape\n")

    print("To run an example, import and call the function:")
    print("  from examples.deep_research_examples import example_1_basic_research")
    print("  example_1_basic_research()\n")

    # Optionally run one example as demonstration
    # Uncomment to run:
    # example_1_basic_research()
