"""CrewAI-style Task class for DeepAgents."""

from dataclasses import dataclass, field
from typing import Optional, List, Callable, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .agent import Agent

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None


@dataclass
class TaskOutput:
    """Output from a completed task.

    Attributes:
        raw: Raw output string from the task.
        description: Original task description.
        expected_output: Expected output specification.
        agent: Agent that completed the task.
        output_file: File path if output was saved.
        created_at: Timestamp when output was created.
    """

    raw: str
    description: str
    expected_output: str
    agent: Optional["Agent"] = None
    output_file: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def summary(self) -> str:
        """Generate a summary of the output (first 200 chars)."""
        if len(self.raw) <= 200:
            return self.raw
        return self.raw[:197] + "..."

    def __repr__(self) -> str:
        """String representation."""
        return f"TaskOutput(description={self.description!r}, summary={self.summary!r})"


@dataclass
class Task:
    """CrewAI-style task definition.

    Tasks represent specific work units to be completed by agents.
    They can have dependencies on other tasks (context) and support
    various output formats.

    Example:
        >>> task = Task(
        ...     description="Research AI trends in 2025",
        ...     expected_output="A comprehensive report with 10 key findings",
        ...     agent=researcher_agent,
        ...     output_file="reports/ai_trends.md"
        ... )
    """

    # Core attributes (required)
    description: str
    expected_output: str

    # Optional configuration
    agent: Optional["Agent"] = None
    tools: Optional[List[Any]] = None
    context: Optional[List["Task"]] = None
    async_execution: bool = False
    human_input: bool = False
    output_file: Optional[str] = None
    output_pydantic: Optional[type] = None
    output_json: Optional[type] = None
    callback: Optional[Callable[[TaskOutput], None]] = None

    # Runtime state
    output: Optional[TaskOutput] = field(default=None, init=False, repr=False)
    _completed: bool = field(default=False, init=False, repr=False)
    _execution_time: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Validate configuration."""
        if self.context is None:
            self.context = []

        if self.output_pydantic and BaseModel is None:
            raise ImportError("pydantic is required for output_pydantic. Install with: pip install pydantic")

    @property
    def completed(self) -> bool:
        """Check if task is completed."""
        return self._completed

    @property
    def execution_time(self) -> Optional[float]:
        """Get task execution time in seconds."""
        return self._execution_time

    def get_full_description(self) -> str:
        """Get description including context from dependent tasks.

        Returns:
            str: Full task description with context.
        """
        desc = self.description

        if self.context:
            desc += "\n\n# Context from Previous Tasks:\n"
            for i, task in enumerate(self.context, 1):
                if task.output:
                    desc += f"\n## Task {i}: {task.description}\n"
                    desc += f"{task.output.raw}\n"

        return desc

    def get_prompt(self, inputs: dict = None) -> str:
        """Build complete prompt for task execution.

        Args:
            inputs: Variables for template substitution.

        Returns:
            str: Complete prompt ready for agent execution.
        """
        inputs = inputs or {}

        # Start with full description (includes context)
        prompt = self.get_full_description()

        # Variable substitution
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        # Add expected output
        prompt += f"\n\n# Expected Output\n{self.expected_output}"

        # Variable substitution in expected output
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        return prompt

    def mark_completed(self, output: str, agent: Optional["Agent"] = None, execution_time: Optional[float] = None):
        """Mark task as completed with output.

        Args:
            output: Task output string.
            agent: Agent that completed the task.
            execution_time: Time taken to complete task (seconds).
        """
        self.output = TaskOutput(
            raw=output,
            description=self.description,
            expected_output=self.expected_output,
            agent=agent,
            output_file=self.output_file,
        )
        self._completed = True
        self._execution_time = execution_time

        # Execute callback if provided
        if self.callback:
            try:
                self.callback(self.output)
            except Exception as e:
                print(f"Warning: Task callback failed: {e}")

    def reset(self):
        """Reset task state for re-execution."""
        self.output = None
        self._completed = False
        self._execution_time = None

    def __repr__(self) -> str:
        """String representation."""
        status = "completed" if self._completed else "pending"
        return f"Task(description={self.description[:50]!r}..., status={status})"
