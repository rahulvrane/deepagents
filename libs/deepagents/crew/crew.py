"""CrewAI-style Crew orchestrator for DeepAgents."""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path
import time
from langchain_core.language_models import BaseChatModel

from .agent import Agent
from .task import Task, TaskOutput
from .process import ProcessType


@dataclass
class CrewOutput:
    """Output from crew execution.

    Attributes:
        raw: Raw output from final task.
        tasks_output: List of all task outputs.
        execution_time: Total execution time in seconds.
    """

    raw: str
    tasks_output: List[TaskOutput]
    execution_time: float

    def __repr__(self) -> str:
        """String representation."""
        return f"CrewOutput(tasks={len(self.tasks_output)}, time={self.execution_time:.2f}s)"


class Crew:
    """CrewAI-style crew orchestrator.

    Coordinates multiple agents working on multiple tasks using either
    sequential or hierarchical execution processes.

    Example:
        >>> crew = Crew(
        ...     agents=[researcher, writer],
        ...     tasks=[research_task, writing_task],
        ...     process=ProcessType.SEQUENTIAL,
        ...     verbose=True
        ... )
        >>> result = crew.launch(inputs={"topic": "AI"})
    """

    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        process: ProcessType = ProcessType.SEQUENTIAL,
        verbose: bool = False,
        memory: bool = False,
        manager_llm: Optional[Union[str, BaseChatModel]] = None,
        manager_agent: Optional[Agent] = None,
    ):
        """Initialize crew.

        Args:
            agents: List of agents in the crew.
            tasks: List of tasks to execute.
            process: Execution process type (sequential or hierarchical).
            verbose: Enable detailed logging.
            memory: Enable memory for agents.
            manager_llm: LLM for hierarchical manager (required if hierarchical).
            manager_agent: Custom manager agent (alternative to manager_llm).

        Raises:
            ValueError: If configuration is invalid.
        """
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.verbose = verbose
        self.memory = memory
        self.manager_llm = manager_llm
        self.manager_agent = manager_agent

        self._validate_config()

    def _validate_config(self):
        """Validate crew configuration."""
        if not self.agents:
            raise ValueError("Crew must have at least one agent")

        if not self.tasks:
            raise ValueError("Crew must have at least one task")

        if self.process == ProcessType.HIERARCHICAL:
            if not self.manager_llm and not self.manager_agent:
                raise ValueError(
                    "Hierarchical process requires either manager_llm or manager_agent"
                )

        # Validate task context dependencies
        for task in self.tasks:
            if task.context:
                for context_task in task.context:
                    if context_task not in self.tasks:
                        raise ValueError(
                            f"Task context references task not in crew: {context_task.description}"
                        )

    def launch(self, inputs: Optional[Dict[str, Any]] = None) -> CrewOutput:
        """Execute the crew.

        Args:
            inputs: Variables for template substitution in task descriptions.

        Returns:
            CrewOutput: Results from crew execution.
        """
        start_time = time.time()
        inputs = inputs or {}

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🚀 Starting Crew Execution")
            print(f"Process: {self.process.value}")
            print(f"Agents: {len(self.agents)}")
            print(f"Tasks: {len(self.tasks)}")
            print(f"{'='*60}\n")

        if self.process == ProcessType.SEQUENTIAL:
            result = self._execute_sequential(inputs)
        elif self.process == ProcessType.HIERARCHICAL:
            result = self._execute_hierarchical(inputs)
        else:
            raise ValueError(f"Unknown process type: {self.process}")

        execution_time = time.time() - start_time

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"✅ Crew Execution Complete")
            print(f"Execution Time: {execution_time:.2f}s")
            print(f"{'='*60}\n")

        return CrewOutput(
            raw=result,
            tasks_output=[task.output for task in self.tasks if task.output],
            execution_time=execution_time,
        )

    def _execute_sequential(self, inputs: Dict[str, Any]) -> str:
        """Execute tasks sequentially.

        Args:
            inputs: Variables for template substitution.

        Returns:
            str: Output from final task.
        """
        from deepagents import create_deep_agent

        for i, task in enumerate(self.tasks, 1):
            task_start = time.time()

            if self.verbose:
                print(f"\n{'─'*60}")
                print(f"📋 Task {i}/{len(self.tasks)}: {task.description[:50]}...")
                print(f"{'─'*60}\n")

            # Build prompt with context
            prompt = task.get_prompt(inputs)

            # Get agent for task
            agent = task.agent or self._get_default_agent()

            if self.verbose:
                print(f"👤 Agent: {agent.role}\n")

            # Create deep agent
            agent_config = agent.to_deepagents_config()

            # Add memory backend if enabled
            if self.memory:
                agent_config["backend"] = self._create_memory_backend(agent.name)

            deep_agent = create_deep_agent(**agent_config)

            # Execute
            result = deep_agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            # Extract output
            output = result["messages"][-1].content

            # Calculate execution time
            task_time = time.time() - task_start

            # Store output
            task.mark_completed(output, agent, task_time)

            if self.verbose:
                print(f"\n✅ Task completed in {task_time:.2f}s")
                print(f"📄 Output summary: {task.output.summary}\n")

            # Save to file if specified
            if task.output_file:
                self._save_output(task.output_file, output, inputs)

                if self.verbose:
                    print(f"💾 Saved output to: {task.output_file}\n")

        # Return output from final task
        return self.tasks[-1].output.raw

    def _execute_hierarchical(self, inputs: Dict[str, Any]) -> str:
        """Execute with manager delegation.

        Args:
            inputs: Variables for template substitution.

        Returns:
            str: Output from manager.
        """
        from deepagents import create_deep_agent

        if self.verbose:
            print(f"\n{'─'*60}")
            print(f"👔 Initializing Manager Agent")
            print(f"{'─'*60}\n")

        # Create manager agent
        if self.manager_agent:
            manager = self.manager_agent
        else:
            manager = self._create_default_manager()

        # Convert worker agents to subagents
        subagents = self._convert_agents_to_subagents()

        if self.verbose:
            print(f"Worker Agents: {len(subagents)}")
            for subagent in subagents:
                print(f"  - {subagent['name']}: {subagent['description']}")
            print()

        # Create manager with subagents
        manager_config = manager.to_deepagents_config()
        manager_config["subagents"] = subagents

        # Add memory backend if enabled
        if self.memory:
            manager_config["backend"] = self._create_memory_backend("manager")

        manager_graph = create_deep_agent(**manager_config)

        # Build hierarchical prompt
        prompt = self._build_hierarchical_prompt(inputs)

        if self.verbose:
            print(f"{'─'*60}")
            print(f"🎯 Delegating Tasks to Workers")
            print(f"{'─'*60}\n")

        # Execute
        start_time = time.time()
        result = manager_graph.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })

        output = result["messages"][-1].content
        execution_time = time.time() - start_time

        # Mark all tasks as completed (manager handled them)
        for task in self.tasks:
            task.mark_completed(output, manager, execution_time / len(self.tasks))

        return output

    def _build_hierarchical_prompt(self, inputs: Dict[str, Any]) -> str:
        """Build prompt for hierarchical execution.

        Args:
            inputs: Variables for template substitution.

        Returns:
            str: Complete prompt for manager.
        """
        prompt = "# Tasks to Complete\n\n"
        prompt += "You are managing a team of specialized agents. Delegate the following tasks to the appropriate agents and coordinate their completion.\n\n"

        for i, task in enumerate(self.tasks, 1):
            prompt += f"## Task {i}\n"
            prompt += f"**Description**: {task.description}\n"
            prompt += f"**Expected Output**: {task.expected_output}\n"

            if task.context:
                prompt += f"**Depends On**: "
                depends = [f"Task {self.tasks.index(t) + 1}" for t in task.context if t in self.tasks]
                prompt += ", ".join(depends)
                prompt += "\n"

            prompt += "\n"

        # Variable substitution
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        prompt += "\n# Instructions\n\n"
        prompt += "1. Analyze each task and determine which agent is best suited\n"
        prompt += "2. Delegate tasks to agents using the `task` tool\n"
        prompt += "3. Ensure task dependencies are respected\n"
        prompt += "4. Synthesize the results into a cohesive final output\n"

        return prompt

    def _convert_agents_to_subagents(self) -> List[Dict]:
        """Convert Crew agents to DeepAgents subagents.

        Returns:
            List[Dict]: Subagent configurations.
        """
        return [agent.to_subagent_dict() for agent in self.agents]

    def _create_default_manager(self) -> Agent:
        """Create default manager agent.

        Returns:
            Agent: Manager agent configuration.
        """
        return Agent(
            role="Project Manager",
            goal="Efficiently coordinate team efforts and delegate tasks to achieve high-quality results",
            backstory="You are an experienced project manager with a proven track record of successful team coordination. You excel at understanding team member capabilities and strategically delegating work to maximize efficiency and quality.",
            llm=self.manager_llm,
            allow_delegation=True,
            verbose=self.verbose,
        )

    def _get_default_agent(self) -> Agent:
        """Get default agent if task has no assigned agent.

        Returns:
            Agent: First agent in crew.

        Raises:
            ValueError: If no agents available.
        """
        if not self.agents:
            raise ValueError("No agents available for task")
        return self.agents[0]

    def _save_output(self, file_path: str, content: str, inputs: Dict[str, Any]):
        """Save output to file with variable substitution.

        Args:
            file_path: Path to output file (supports {variable} substitution).
            content: Content to save.
            inputs: Variables for template substitution.
        """
        # Variable substitution in file path
        for key, value in inputs.items():
            file_path = file_path.replace(f"{{{key}}}", str(value))

        # Create parent directories
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_memory_backend(self, agent_name: str):
        """Create memory backend for agent.

        Args:
            agent_name: Name of the agent.

        Returns:
            Backend factory function.
        """
        from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend
        from pathlib import Path

        # Create storage directory
        storage_dir = Path.home() / ".deepagents" / "crews" / agent_name
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Return backend factory
        return lambda runtime: CompositeBackend(
            default=StateBackend(runtime),
            routes={
                "/memory/": FilesystemBackend(root_dir=storage_dir, virtual_mode=True),
            }
        )

    def reset_tasks(self):
        """Reset all tasks to allow re-execution."""
        for task in self.tasks:
            task.reset()

    def __repr__(self) -> str:
        """String representation."""
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)}, process={self.process.value})"
