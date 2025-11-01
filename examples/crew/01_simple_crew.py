"""Simple crew example with code-first approach.

This example demonstrates the basic usage of the CrewAI-like interface
with a researcher and writer working together sequentially.
"""

from deepagents.crew import Agent, Task, Crew, ProcessType


def main():
    """Run a simple research and writing crew."""

    # Define agents
    researcher = Agent(
        role="Senior Researcher",
        goal="Conduct comprehensive research on AI trends",
        backstory="""You are an experienced researcher with 10 years of experience
        in technology analysis. You excel at finding relevant information and
        synthesizing insights from multiple sources.""",
        verbose=True,
        memory=True,
    )

    writer = Agent(
        role="Technical Writer",
        goal="Create engaging and informative technical content",
        backstory="""You are a skilled writer who specializes in making complex
        technical topics accessible to a broad audience. You have a talent for
        clear explanations and compelling narratives.""",
        verbose=True,
        memory=True,
    )

    # Define tasks
    research_task = Task(
        description="""Research the latest developments in {topic} for 2025.
        Focus on:
        - Key innovations and breakthroughs
        - Major players and companies
        - Future trends and predictions
        - Potential challenges and concerns

        Provide comprehensive findings with sources.""",
        expected_output="A detailed research report with 10 key findings",
        agent=researcher,
    )

    writing_task = Task(
        description="""Based on the research findings, write a comprehensive
        blog post about {topic}. The post should:
        - Have an engaging introduction
        - Cover the main findings from the research
        - Include insights and analysis
        - Conclude with future outlook

        Make it accessible to a general technical audience.""",
        expected_output="A well-structured blog post (800-1000 words)",
        agent=writer,
        context=[research_task],  # Depends on research task
        output_file="outputs/{topic}_blog_post.md",
    )

    # Create crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=ProcessType.SEQUENTIAL,
        verbose=True,
        memory=True,
    )

    # Execute crew
    print("\n🚀 Starting Simple Crew Example\n")
    result = crew.launch(inputs={"topic": "AI Agents"})

    print("\n" + "="*60)
    print("📊 FINAL RESULT")
    print("="*60)
    print(result.raw)
    print("\n" + "="*60)
    print(f"✅ Execution completed in {result.execution_time:.2f}s")
    print(f"📋 Tasks completed: {len(result.tasks_output)}")
    print("="*60)


if __name__ == "__main__":
    main()
