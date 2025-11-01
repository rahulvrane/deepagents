"""Hierarchical crew example with manager delegation.

This example demonstrates hierarchical process where a manager agent
dynamically delegates tasks to specialized worker agents.
"""

from deepagents.crew import Agent, Task, Crew, ProcessType


def main():
    """Run a hierarchical crew with manager delegation."""

    # Define specialized worker agents
    data_collector = Agent(
        role="Data Collection Specialist",
        goal="Gather comprehensive data from multiple sources",
        backstory="""You are an expert at finding and collecting quality data
        from diverse sources. You know where to look and how to verify
        information authenticity.""",
        allow_delegation=False,
        verbose=True,
    )

    analyst = Agent(
        role="Data Analyst",
        goal="Analyze data and identify meaningful patterns and insights",
        backstory="""You are a data scientist with expertise in statistical
        analysis and pattern recognition. You can extract actionable insights
        from complex datasets.""",
        allow_delegation=False,
        verbose=True,
    )

    writer = Agent(
        role="Report Writer",
        goal="Transform analysis into clear, compelling reports",
        backstory="""You are a professional report writer who excels at
        presenting complex findings in an accessible, well-structured format.""",
        allow_delegation=False,
        verbose=True,
    )

    # Define tasks (no explicit agent assignment for hierarchical)
    collect_task = Task(
        description="""Collect comprehensive data about {topic}.
        Gather information from multiple reliable sources including:
        - Academic papers and research
        - Industry reports
        - News articles
        - Expert opinions

        Ensure data quality and cite all sources.""",
        expected_output="A comprehensive dataset with verified sources",
    )

    analyze_task = Task(
        description="""Analyze the collected data about {topic}.
        Perform:
        - Trend analysis
        - Pattern identification
        - Comparative analysis
        - Statistical insights

        Identify the most significant findings.""",
        expected_output="Detailed analysis with key insights and statistics",
    )

    write_task = Task(
        description="""Create a professional report about {topic}.
        The report should include:
        - Executive summary
        - Methodology
        - Key findings
        - Detailed analysis
        - Conclusions and recommendations

        Format as a professional business report.""",
        expected_output="Complete professional report in markdown format",
        output_file="outputs/{topic}_report.md",
    )

    # Create hierarchical crew
    # Manager will dynamically assign tasks to appropriate agents
    crew = Crew(
        agents=[data_collector, analyst, writer],
        tasks=[collect_task, analyze_task, write_task],
        process=ProcessType.HIERARCHICAL,
        manager_llm="claude-sonnet-4.5",  # Manager uses Claude
        verbose=True,
        memory=True,
    )

    # Execute crew
    print("\n🚀 Starting Hierarchical Crew Example\n")
    result = crew.launch(inputs={"topic": "AI in Healthcare"})

    print("\n" + "="*60)
    print("📊 FINAL RESULT")
    print("="*60)
    print(result.raw[:500] + "..." if len(result.raw) > 500 else result.raw)
    print("\n" + "="*60)
    print(f"✅ Execution completed in {result.execution_time:.2f}s")
    print(f"📋 Tasks completed: {len(result.tasks_output)}")
    print("="*60)


if __name__ == "__main__":
    main()
