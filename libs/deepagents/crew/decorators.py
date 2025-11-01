"""Decorators for CrewAI-style crew definitions."""

from typing import Callable, Dict, List, Optional
from functools import wraps


class CrewBase:
    """Base class for crew definitions using decorators.

    This class provides a convenient way to define agents, tasks, and crews
    using Python decorators, similar to CrewAI's pattern.

    Example:
        >>> from deepagents.crew import CrewBase, agent, task, crew
        >>>
        >>> class MyCrewBase):
        ...     @agent
        ...     def researcher(self):
        ...         return Agent(role="Researcher", ...)
        ...
        ...     @task
        ...     def research_task(self):
        ...         return Task(description="...", agent=self.researcher())
        ...
        ...     @crew
        ...     def crew(self):
        ...         return Crew(agents=self.agents, tasks=self.tasks)
        >>>
        >>> my_crew = MyCrew()
        >>> result = my_crew.crew().kickoff()
    """

    def __init__(self):
        """Initialize crew base."""
        self._agents: Dict[str, Callable] = {}
        self._tasks: Dict[str, Callable] = {}
        self._crew_func: Optional[Callable] = None

        # Configuration paths (can be overridden in subclasses)
        self.agents_config: Optional[str] = None
        self.tasks_config: Optional[str] = None

    @property
    def agents(self) -> List:
        """Get all agents defined with @agent decorator.

        Returns:
            List: List of Agent instances.
        """
        return [func(self) for func in self._agents.values()]

    @property
    def tasks(self) -> List:
        """Get all tasks defined with @task decorator.

        Returns:
            List: List of Task instances.
        """
        return [func(self) for func in self._tasks.values()]

    def _register_agent(self, name: str, func: Callable):
        """Register an agent function.

        Args:
            name: Agent name.
            func: Agent factory function.
        """
        self._agents[name] = func

    def _register_task(self, name: str, func: Callable):
        """Register a task function.

        Args:
            name: Task name.
            func: Task factory function.
        """
        self._tasks[name] = func

    def _register_crew(self, func: Callable):
        """Register crew function.

        Args:
            func: Crew factory function.
        """
        self._crew_func = func


def agent(func: Callable) -> Callable:
    """Decorator for agent definitions.

    Marks a method as an agent factory. The method should return an Agent instance.

    Example:
        >>> @agent
        ... def researcher(self) -> Agent:
        ...     return Agent(role="Researcher", goal="...", backstory="...")

    Args:
        func: Method that returns an Agent instance.

    Returns:
        Callable: Decorated method.
    """
    @wraps(func)
    def wrapper(self):
        return func(self)

    # Mark as agent method
    wrapper._is_agent = True
    wrapper._agent_name = func.__name__

    return wrapper


def task(func: Callable) -> Callable:
    """Decorator for task definitions.

    Marks a method as a task factory. The method should return a Task instance.

    Example:
        >>> @task
        ... def research_task(self) -> Task:
        ...     return Task(
        ...         description="Research the topic",
        ...         expected_output="Comprehensive report",
        ...         agent=self.researcher()
        ...     )

    Args:
        func: Method that returns a Task instance.

    Returns:
        Callable: Decorated method.
    """
    @wraps(func)
    def wrapper(self):
        return func(self)

    # Mark as task method
    wrapper._is_task = True
    wrapper._task_name = func.__name__

    return wrapper


def crew(func: Callable) -> Callable:
    """Decorator for crew definitions.

    Marks a method as a crew factory. The method should return a Crew instance.

    Example:
        >>> @crew
        ... def crew(self) -> Crew:
        ...     return Crew(
        ...         agents=self.agents,
        ...         tasks=self.tasks,
        ...         process=ProcessType.SEQUENTIAL
        ...     )

    Args:
        func: Method that returns a Crew instance.

    Returns:
        Callable: Decorated method.
    """
    @wraps(func)
    def wrapper(self):
        return func(self)

    # Mark as crew method
    wrapper._is_crew = True

    return wrapper


def __init_subclass__(cls, **kwargs):
    """Auto-register decorated methods when subclass is created."""
    super().__init_subclass__(**kwargs)

    # Find and register decorated methods
    for name, method in cls.__dict__.items():
        if hasattr(method, '_is_agent'):
            # Will be registered when instance is created
            pass
        elif hasattr(method, '_is_task'):
            pass
        elif hasattr(method, '_is_crew'):
            pass


# Monkey-patch CrewBase to support auto-registration
original_init = CrewBase.__init__


def enhanced_init(self):
    """Enhanced init that auto-registers decorated methods."""
    original_init(self)

    # Auto-register decorated methods
    for name in dir(self):
        if name.startswith('_'):
            continue

        attr = getattr(self, name)

        if hasattr(attr, '_is_agent'):
            self._register_agent(name, attr)
        elif hasattr(attr, '_is_task'):
            self._register_task(name, attr)
        elif hasattr(attr, '_is_crew'):
            self._register_crew(attr)


CrewBase.__init__ = enhanced_init
