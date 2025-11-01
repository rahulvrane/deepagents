"""CrewAI-style Agent class for DeepAgents."""

from dataclasses import dataclass, field
from typing import Optional, List, Callable, Any, Union
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel


@dataclass
class Agent:
    """CrewAI-style agent definition for DeepAgents.

    This class provides a CrewAI-compatible interface for defining agents
    with role, goal, and backstory, which are mapped to DeepAgents'
    system prompt configuration.

    Example:
        >>> agent = Agent(
        ...     role="Senior Researcher",
        ...     goal="Conduct comprehensive research",
        ...     backstory="Expert researcher with 10 years experience",
        ...     tools=[search_tool],
        ...     verbose=True
        ... )
    """

    # Core attributes (required)
    role: str
    goal: str
    backstory: str

    # Optional configuration
    llm: Optional[Union[str, BaseChatModel]] = None
    tools: Optional[List[Union[BaseTool, Callable]]] = None
    max_iter: int = 20
    max_execution_time: Optional[int] = None
    max_rpm: Optional[int] = None
    max_retry_limit: int = 2
    allow_delegation: bool = False
    allow_code_execution: bool = False
    verbose: bool = False
    memory: bool = False
    cache: bool = True

    # DeepAgents-specific
    middleware: Optional[List[Any]] = None
    backend: Optional[Any] = None

    # Internal
    _name: Optional[str] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialize computed fields."""
        if self._name is None:
            self._name = self.role.lower().replace(" ", "_")

    @property
    def name(self) -> str:
        """Get the agent's name (derived from role)."""
        return self._name

    def to_system_prompt(self) -> str:
        """Convert role, goal, backstory to system prompt.

        Returns:
            str: Formatted system prompt for the agent.
        """
        prompt = f"""# Role
{self.role}

# Goal
{self.goal}

# Backstory
{self.backstory}
"""

        if self.allow_delegation:
            prompt += """
# Delegation
You can delegate tasks to other agents when needed. Use the `task` tool to delegate work to specialized agents.
"""

        if self.allow_code_execution:
            prompt += """
# Code Execution
You can execute code when needed. Use the shell execution tools responsibly.
"""

        return prompt

    def to_deepagents_config(self) -> dict:
        """Convert to create_deep_agent() parameters.

        Returns:
            dict: Configuration dictionary for create_deep_agent().
        """
        config = {
            "model": self.llm,
            "tools": self.tools or [],
            "system_prompt": self.to_system_prompt(),
            "middleware": self.middleware or [],
        }

        if self.backend is not None:
            config["backend"] = self.backend

        if self.name:
            config["name"] = self.name

        return config

    def to_subagent_dict(self) -> dict:
        """Convert to DeepAgents subagent dictionary.

        Returns:
            dict: Subagent configuration for use in create_deep_agent(subagents=[...]).
        """
        subagent = {
            "name": self.name,
            "description": f"{self.role}: {self.goal}",
            "system_prompt": self.to_system_prompt(),
            "tools": self.tools or [],
        }

        if self.llm:
            subagent["model"] = self.llm

        if self.middleware:
            subagent["middleware"] = self.middleware

        return subagent

    def __repr__(self) -> str:
        """String representation."""
        return f"Agent(role={self.role!r}, goal={self.goal!r})"
