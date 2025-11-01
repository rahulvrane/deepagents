"""YAML-based crew configuration example.

This example demonstrates how to define agents and tasks using YAML
configuration files, similar to CrewAI's recommended pattern.
"""

from deepagents.crew import Agent, Task, Crew, ProcessType
from deepagents.crew.decorators import CrewBase, agent, task, crew
from deepagents.crew.config import load_agents_config, load_tasks_config
from pathlib import Path


class ResearchCrew(CrewBase):
    """Research crew defined with YAML configuration."""

    def __init__(self):
        super().__init__()

        # Load configurations
        config_dir = Path(__file__).parent / "config"
        self.agents_config = load_agents_config(str(config_dir / "agents.yaml"))
        self.tasks_config = load_tasks_config(str(config_dir / "tasks.yaml"))

    @agent
    def researcher(self) -> Agent:
        """Create researcher agent from config."""
        return Agent(**self.agents_config['researcher'])

    @agent
    def analyst(self) -> Agent:
        """Create analyst agent from config."""
        return Agent(**self.agents_config['analyst'])

    @agent
    def writer(self) -> Agent:
        """Create writer agent from config."""
        return Agent(**self.agents_config['writer'])

    @task
    def research_task(self) -> Task:
        """Create research task from config."""
        return Task(
            **self.tasks_config['research_task'],
            agent=self.researcher()
        )

    @task
    def analysis_task(self) -> Task:
        """Create analysis task from config."""
        return Task(
            **self.tasks_config['analysis_task'],
            agent=self.analyst(),
            context=[self.research_task()]
        )

    @task
    def writing_task(self) -> Task:
        """Create writing task from config."""
        return Task(
            **self.tasks_config['writing_task'],
            agent=self.writer(),
            context=[self.research_task(), self.analysis_task()],
            output_file="outputs/{topic}_final_report.md"
        )

    @crew
    def crew(self) -> Crew:
        """Create crew with all agents and tasks."""
        return Crew(
            agents=self.agents,  # Auto-collected from @agent decorators
            tasks=self.tasks,    # Auto-collected from @task decorators
            process=ProcessType.SEQUENTIAL,
            verbose=True,
            memory=True,
        )


def main():
    """Run YAML-configured crew."""
    print("\n🚀 Starting YAML-Configured Crew Example\n")

    try:
        # Create crew instance
        research_crew = ResearchCrew()

        # Execute crew
        result = research_crew.crew().launch(inputs={
            "topic": "Quantum Computing",
            "year": "2025"
        })

        print("\n" + "="*60)
        print("📊 FINAL RESULT")
        print("="*60)
        print(result.raw[:500] + "..." if len(result.raw) > 500 else result.raw)
        print("\n" + "="*60)
        print(f"✅ Execution completed in {result.execution_time:.2f}s")
        print(f"📋 Tasks completed: {len(result.tasks_output)}")
        print("="*60)

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Make sure to create config/agents.yaml and config/tasks.yaml")
        print("    See the config examples in the crew examples directory.\n")


if __name__ == "__main__":
    main()
