# CrewAI-Like Agent Definition System for DeepAgents

## Executive Summary

This design document outlines the integration of CrewAI-style agent definitions into the DeepAgents framework. The goal is to enable declarative agent, task, and crew definitions while leveraging DeepAgents' existing middleware architecture.

## Key Design Goals

1. **Declarative Agent Definition**: Support CrewAI-style role, goal, backstory pattern
2. **Task Management**: Introduce explicit task definitions with dependencies
3. **Crew Orchestration**: Enable multi-agent collaboration with sequential and hierarchical processes
4. **Backward Compatibility**: Maintain compatibility with existing DeepAgents code
5. **YAML Support**: Enable configuration via YAML files
6. **Leverage Existing Infrastructure**: Use DeepAgents' middleware, backends, and tools

## Architecture Overview

```
libs/deepagents/
├── crew/
│   ├── __init__.py
│   ├── agent.py          # CrewAI-style Agent class
│   ├── task.py           # Task definition class
│   ├── crew.py           # Crew orchestrator
│   ├── process.py        # Process types (Sequential, Hierarchical)
│   ├── decorators.py     # @agent, @task, @crew decorators
│   └── config.py         # YAML configuration loader
```

## Component Specifications

### 1. Agent Class (`crew/agent.py`)

Maps CrewAI agent attributes to DeepAgents configuration:

```python
from dataclasses import dataclass
from typing import Optional, List, Callable, Any
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel

@dataclass
class Agent:
    """CrewAI-style agent definition for DeepAgents."""

    # Core attributes (required)
    role: str
    goal: str
    backstory: str

    # Optional configuration
    llm: Optional[str | BaseChatModel] = None
    tools: List[BaseTool | Callable] = None
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
    middleware: List[Any] = None
    backend: Optional[Any] = None

    def to_system_prompt(self) -> str:
        """Convert role, goal, backstory to system prompt."""
        return f"""# Role
{self.role}

# Goal
{self.goal}

# Backstory
{self.backstory}
"""

    def to_deepagents_config(self) -> dict:
        """Convert to create_deep_agent() parameters."""
        return {
            "model": self.llm,
            "tools": self.tools or [],
            "system_prompt": self.to_system_prompt(),
            "middleware": self.middleware or [],
            "backend": self.backend,
        }
```

### 2. Task Class (`crew/task.py`)

Defines work units with dependencies:

```python
from dataclasses import dataclass
from typing import Optional, List, Callable, Any
from pydantic import BaseModel

@dataclass
class Task:
    """CrewAI-style task definition."""

    # Core attributes (required)
    description: str
    expected_output: str

    # Optional configuration
    agent: Optional['Agent'] = None
    tools: Optional[List[Any]] = None
    context: Optional[List['Task']] = None
    async_execution: bool = False
    human_input: bool = False
    output_file: Optional[str] = None
    output_pydantic: Optional[type[BaseModel]] = None
    output_json: Optional[type[BaseModel]] = None
    callback: Optional[Callable] = None

    # Runtime state
    output: Optional[Any] = None
    _completed: bool = False

    def get_full_description(self) -> str:
        """Get description including context from dependent tasks."""
        desc = self.description

        if self.context:
            desc += "\n\n# Context from Previous Tasks:\n"
            for task in self.context:
                if task.output:
                    desc += f"\n## {task.description}\n{task.output}\n"

        return desc
```

### 3. Process Types (`crew/process.py`)

```python
from enum import Enum

class ProcessType(Enum):
    """Crew process types."""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
```

### 4. Crew Class (`crew/crew.py`)

Orchestrates agents and tasks:

```python
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from langchain_core.language_models import BaseChatModel

from deepagents import create_deep_agent
from .agent import Agent
from .task import Task
from .process import ProcessType

@dataclass
class Crew:
    """CrewAI-style crew orchestrator."""

    agents: List[Agent]
    tasks: List[Task]
    process: ProcessType = ProcessType.SEQUENTIAL
    verbose: bool = False
    memory: bool = False
    manager_llm: Optional[str | BaseChatModel] = None
    manager_agent: Optional[Agent] = None

    def __post_init__(self):
        """Validate configuration."""
        if self.process == ProcessType.HIERARCHICAL:
            if not self.manager_llm and not self.manager_agent:
                raise ValueError("Hierarchical process requires manager_llm or manager_agent")

    def launch(self, inputs: Optional[Dict[str, Any]] = None) -> Any:
        """Execute the crew."""
        if self.process == ProcessType.SEQUENTIAL:
            return self._execute_sequential(inputs or {})
        elif self.process == ProcessType.HIERARCHICAL:
            return self._execute_hierarchical(inputs or {})

    def _execute_sequential(self, inputs: Dict[str, Any]) -> Any:
        """Execute tasks sequentially."""
        for task in self.tasks:
            # Build prompt with context
            prompt = self._build_task_prompt(task, inputs)

            # Get agent for task
            agent = task.agent or self._get_default_agent()

            # Create deep agent
            deep_agent = self._create_agent_graph(agent)

            # Execute
            result = deep_agent.invoke({"messages": [{"role": "user", "content": prompt}]})

            # Store output
            task.output = result["messages"][-1].content
            task._completed = True

            # Callback
            if task.callback:
                task.callback(task.output)

            # Save to file
            if task.output_file:
                self._save_output(task.output_file, task.output, inputs)

        return self.tasks[-1].output

    def _execute_hierarchical(self, inputs: Dict[str, Any]) -> Any:
        """Execute with manager delegation."""
        # Create manager agent
        if self.manager_agent:
            manager = self.manager_agent
        else:
            manager = self._create_default_manager()

        # Convert worker agents to subagents
        subagents = self._convert_agents_to_subagents()

        # Create manager with subagents
        manager_config = manager.to_deepagents_config()
        manager_config["subagents"] = subagents

        manager_graph = create_deep_agent(**manager_config)

        # Build hierarchical prompt
        prompt = self._build_hierarchical_prompt(inputs)

        # Execute
        result = manager_graph.invoke({"messages": [{"role": "user", "content": prompt}]})

        return result["messages"][-1].content

    def _build_task_prompt(self, task: Task, inputs: Dict[str, Any]) -> str:
        """Build prompt for task execution."""
        prompt = task.get_full_description()

        # Variable substitution
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        prompt += f"\n\n# Expected Output\n{task.expected_output}"

        return prompt

    def _build_hierarchical_prompt(self, inputs: Dict[str, Any]) -> str:
        """Build prompt for hierarchical execution."""
        prompt = "# Tasks to Complete\n\n"

        for i, task in enumerate(self.tasks, 1):
            prompt += f"## Task {i}\n"
            prompt += f"**Description**: {task.description}\n"
            prompt += f"**Expected Output**: {task.expected_output}\n\n"

        # Variable substitution
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        prompt += "\nDelegate these tasks to the appropriate agents and coordinate their completion."

        return prompt

    def _convert_agents_to_subagents(self) -> List[Dict]:
        """Convert Crew agents to DeepAgents subagents."""
        subagents = []

        for agent in self.agents:
            subagent = {
                "name": agent.role.lower().replace(" ", "_"),
                "description": f"{agent.role}: {agent.goal}",
                "system_prompt": agent.to_system_prompt(),
                "tools": agent.tools or [],
            }

            if agent.llm:
                subagent["model"] = agent.llm

            if agent.middleware:
                subagent["middleware"] = agent.middleware

            subagents.append(subagent)

        return subagents

    def _create_agent_graph(self, agent: Agent):
        """Create DeepAgents graph from Agent."""
        config = agent.to_deepagents_config()
        return create_deep_agent(**config)

    def _create_default_manager(self) -> Agent:
        """Create default manager agent."""
        return Agent(
            role="Project Manager",
            goal="Efficiently coordinate team efforts and delegate tasks",
            backstory="Experienced project manager skilled at delegation and quality assurance.",
            llm=self.manager_llm,
            allow_delegation=True,
        )

    def _get_default_agent(self) -> Agent:
        """Get default agent if task has no assigned agent."""
        if not self.agents:
            raise ValueError("No agents available for task")
        return self.agents[0]

    def _save_output(self, file_path: str, content: str, inputs: Dict[str, Any]):
        """Save output to file with variable substitution."""
        # Variable substitution in file path
        for key, value in inputs.items():
            file_path = file_path.replace(f"{{{key}}}", str(value))

        with open(file_path, 'w') as f:
            f.write(content)
```

### 5. Decorators (`crew/decorators.py`)

```python
from typing import Callable, Dict, List
from functools import wraps

class CrewBase:
    """Base class for crew definitions."""

    def __init__(self):
        self._agents: Dict[str, Callable] = {}
        self._tasks: Dict[str, Callable] = {}
        self._crew_func: Optional[Callable] = None

        self.agents_config: Optional[str] = None
        self.tasks_config: Optional[str] = None

    @property
    def agents(self) -> List:
        """Get all agents."""
        return [func() for func in self._agents.values()]

    @property
    def tasks(self) -> List:
        """Get all tasks."""
        return [func() for func in self._tasks.values()]


def agent(func: Callable) -> Callable:
    """Decorator for agent definitions."""
    @wraps(func)
    def wrapper(self):
        return func(self)

    # Store in CrewBase instance
    if hasattr(func, '__self__'):
        self_obj = func.__self__
        if isinstance(self_obj, CrewBase):
            self_obj._agents[func.__name__] = wrapper

    return wrapper


def task(func: Callable) -> Callable:
    """Decorator for task definitions."""
    @wraps(func)
    def wrapper(self):
        return func(self)

    return wrapper


def crew(func: Callable) -> Callable:
    """Decorator for crew definitions."""
    @wraps(func)
    def wrapper(self):
        return func(self)

    return wrapper
```

### 6. YAML Configuration (`crew/config.py`)

```python
import yaml
from pathlib import Path
from typing import Dict, Any

def load_agents_config(config_path: str) -> Dict[str, Any]:
    """Load agents from YAML configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_tasks_config(config_path: str) -> Dict[str, Any]:
    """Load tasks from YAML configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def agent_from_config(config: Dict[str, Any]) -> 'Agent':
    """Create Agent from config dict."""
    from .agent import Agent
    return Agent(**config)


def task_from_config(config: Dict[str, Any]) -> 'Task':
    """Create Task from config dict."""
    from .task import Task
    return Task(**config)
```

## Usage Examples

### Example 1: Code-First Approach

```python
from deepagents.crew import Agent, Task, Crew, ProcessType

# Define agents
researcher = Agent(
    role="Senior Researcher",
    goal="Conduct comprehensive research on AI trends",
    backstory="Expert researcher with 10 years of experience",
    verbose=True,
    memory=True
)

writer = Agent(
    role="Technical Writer",
    goal="Create engaging technical content",
    backstory="Skilled writer who simplifies complex topics",
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research the latest developments in {topic}",
    expected_output="A comprehensive research report with 10 key findings",
    agent=researcher
)

writing_task = Task(
    description="Write a blog post about {topic} based on research",
    expected_output="A well-structured blog post",
    agent=writer,
    context=[research_task],
    output_file="blog_posts/{topic}_article.md"
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=ProcessType.SEQUENTIAL,
    verbose=True,
    memory=True
)

# Execute
result = crew.launch(inputs={"topic": "AI Agents"})
```

### Example 2: YAML-Based Approach

**config/agents.yaml:**
```yaml
researcher:
  role: "Senior Data Researcher"
  goal: "Uncover cutting-edge developments in {topic}"
  backstory: "You are a seasoned researcher with expertise in data analysis"
  verbose: true
  memory: true

analyst:
  role: "Data Analyst"
  goal: "Analyze research findings and identify trends"
  backstory: "You are an expert analyst with strong analytical skills"
  verbose: true
```

**config/tasks.yaml:**
```yaml
research_task:
  description: "Research the latest developments in {topic}"
  expected_output: "Comprehensive research report"

analysis_task:
  description: "Analyze the research findings"
  expected_output: "Analysis report with insights"
  output_file: "reports/{topic}_analysis.md"
```

**crew.py:**
```python
from deepagents.crew import Agent, Task, Crew, ProcessType
from deepagents.crew.decorators import CrewBase, agent, task, crew
from deepagents.crew.config import load_agents_config, load_tasks_config

class ResearchCrew(CrewBase):
    agents_config_path = 'config/agents.yaml'
    tasks_config_path = 'config/tasks.yaml'

    def __init__(self):
        super().__init__()
        self.agents_config = load_agents_config(self.agents_config_path)
        self.tasks_config = load_tasks_config(self.tasks_config_path)

    @agent
    def researcher(self) -> Agent:
        return Agent(**self.agents_config['researcher'])

    @agent
    def analyst(self) -> Agent:
        return Agent(**self.agents_config['analyst'])

    @task
    def research_task(self) -> Task:
        return Task(
            **self.tasks_config['research_task'],
            agent=self.researcher()
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            **self.tasks_config['analysis_task'],
            agent=self.analyst(),
            context=[self.research_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=ProcessType.SEQUENTIAL,
            verbose=True
        )

# Execute
research_crew = ResearchCrew()
result = research_crew.crew().launch(inputs={"topic": "AI Agents"})
```

### Example 3: Hierarchical Process

```python
from deepagents.crew import Agent, Task, Crew, ProcessType

# Define specialized agents
data_collector = Agent(
    role="Data Collection Specialist",
    goal="Gather data from multiple sources",
    backstory="Expert at finding quality data",
    allow_delegation=False
)

analyst = Agent(
    role="Data Analyst",
    goal="Analyze and interpret data",
    backstory="PhD in Statistics",
    allow_delegation=False
)

visualizer = Agent(
    role="Data Visualization Expert",
    goal="Create compelling visualizations",
    backstory="Expert in data storytelling",
    allow_delegation=False
)

# Define tasks (no pre-assignment for hierarchical)
collect_task = Task(
    description="Collect market data for {industry}",
    expected_output="Comprehensive dataset"
)

analyze_task = Task(
    description="Analyze the collected data",
    expected_output="Statistical analysis"
)

visualize_task = Task(
    description="Create visualizations",
    expected_output="Charts and graphs"
)

# Hierarchical crew
crew = Crew(
    agents=[data_collector, analyst, visualizer],
    tasks=[collect_task, analyze_task, visualize_task],
    process=ProcessType.HIERARCHICAL,
    manager_llm="claude-sonnet-4.5",
    verbose=True
)

result = crew.launch(inputs={"industry": "AI"})
```

## Memory Integration

Map CrewAI memory types to DeepAgents backends:

```python
from deepagents.backends import StateBackend, StoreBackend, CompositeBackend, FilesystemBackend
from pathlib import Path

def create_memory_backend(crew_name: str, memory: bool = False):
    """Create memory backend for crew."""
    if not memory:
        return StateBackend

    # Mimic CrewAI's memory structure
    storage_dir = Path.home() / ".deepagents" / "crews" / crew_name
    storage_dir.mkdir(parents=True, exist_ok=True)

    return CompositeBackend(
        default=StateBackend,  # Short-term memory
        routes={
            "/long_term/": FilesystemBackend(root_dir=storage_dir / "long_term"),
            "/entities/": FilesystemBackend(root_dir=storage_dir / "entities"),
        }
    )
```

## Migration Path

1. **Phase 1**: Implement core classes (Agent, Task, Crew, Process)
2. **Phase 2**: Add decorator support and YAML configuration
3. **Phase 3**: Implement memory integration
4. **Phase 4**: Add advanced features (async execution, callbacks, guardrails)
5. **Phase 5**: Create comprehensive examples and documentation

## Conclusion

This design enables CrewAI-style agent definitions in DeepAgents while maintaining backward compatibility and leveraging existing infrastructure. The system is extensible and follows established patterns from both frameworks.
