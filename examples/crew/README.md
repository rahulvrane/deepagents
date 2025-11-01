# CrewAI-Style Agent Definitions for DeepAgents

This directory contains examples demonstrating the CrewAI-like interface for defining multi-agent systems in DeepAgents.

## Overview

The `deepagents.crew` module provides a CrewAI-compatible API for defining agents, tasks, and crews while leveraging DeepAgents' powerful middleware architecture and backend systems.

### Key Features

- **Declarative Agent Definition**: Define agents with role, goal, and backstory
- **Task Management**: Create explicit tasks with dependencies and outputs
- **Process Types**: Sequential and hierarchical execution modes
- **YAML Configuration**: Support for configuration via YAML files
- **Memory Integration**: Built-in memory systems for agent learning
- **Backward Compatible**: Works seamlessly with existing DeepAgents code

## Examples

### 1. Simple Sequential Crew (`01_simple_crew.py`)

A basic example with a researcher and writer working sequentially:

```python
from deepagents.crew import Agent, Task, Crew, ProcessType

# Define agents
researcher = Agent(
    role="Senior Researcher",
    goal="Conduct comprehensive research",
    backstory="Expert researcher with 10 years experience",
    verbose=True
)

writer = Agent(
    role="Technical Writer",
    goal="Create engaging content",
    backstory="Skilled writer who simplifies complex topics",
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research {topic}",
    expected_output="Research report",
    agent=researcher
)

writing_task = Task(
    description="Write blog post about {topic}",
    expected_output="Blog post",
    agent=writer,
    context=[research_task],
    output_file="outputs/{topic}_post.md"
)

# Create and execute crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=ProcessType.SEQUENTIAL,
    verbose=True
)

result = crew.launch(inputs={"topic": "AI Agents"})
```

**Run it:**
```bash
python 01_simple_crew.py
```

### 2. Hierarchical Crew (`02_hierarchical_crew.py`)

Demonstrates manager-driven task delegation:

```python
from deepagents.crew import Agent, Task, Crew, ProcessType

# Define specialized agents (no delegation)
data_collector = Agent(
    role="Data Collector",
    goal="Gather data",
    backstory="Expert at finding quality data",
    allow_delegation=False
)

analyst = Agent(
    role="Analyst",
    goal="Analyze data",
    backstory="Expert in statistical analysis",
    allow_delegation=False
)

# Tasks without pre-assignment (manager will delegate)
collect_task = Task(
    description="Collect data about {topic}",
    expected_output="Dataset"
)

analyze_task = Task(
    description="Analyze the data",
    expected_output="Analysis report"
)

# Hierarchical crew with manager
crew = Crew(
    agents=[data_collector, analyst],
    tasks=[collect_task, analyze_task],
    process=ProcessType.HIERARCHICAL,
    manager_llm="claude-sonnet-4.5",
    verbose=True
)

result = crew.launch(inputs={"topic": "AI in Healthcare"})
```

**Run it:**
```bash
python 02_hierarchical_crew.py
```

### 3. YAML Configuration (`03_yaml_config_crew.py`)

Define agents and tasks in YAML files:

**config/agents.yaml:**
```yaml
researcher:
  role: "Senior Researcher"
  goal: "Research {topic}"
  backstory: "Expert researcher..."
  verbose: true
```

**config/tasks.yaml:**
```yaml
research_task:
  description: "Research {topic}"
  expected_output: "Research report"
```

**Python code:**
```python
from deepagents.crew.decorators import CrewBase, agent, task, crew
from deepagents.crew.config import load_agents_config, load_tasks_config

class ResearchCrew(CrewBase):
    def __init__(self):
        super().__init__()
        self.agents_config = load_agents_config("config/agents.yaml")
        self.tasks_config = load_tasks_config("config/tasks.yaml")

    @agent
    def researcher(self):
        return Agent(**self.agents_config['researcher'])

    @task
    def research_task(self):
        return Task(**self.tasks_config['research_task'], agent=self.researcher())

    @crew
    def crew(self):
        return Crew(agents=self.agents, tasks=self.tasks, verbose=True)

crew = ResearchCrew()
result = crew.crew().launch(inputs={"topic": "AI"})
```

**Requirements:**
```bash
pip install pyyaml
```

**Run it:**
```bash
python 03_yaml_config_crew.py
```

## Core Concepts

### Agents

Agents are autonomous entities with specific roles and capabilities:

```python
agent = Agent(
    role="Role Name",              # Required: Agent's function
    goal="Goal description",       # Required: Agent's objective
    backstory="Backstory...",      # Required: Context and personality
    llm="claude-sonnet-4.5",      # Optional: Specific model
    tools=[tool1, tool2],         # Optional: Available tools
    verbose=True,                  # Optional: Logging
    memory=True,                   # Optional: Enable memory
    allow_delegation=False,        # Optional: Can delegate to others
)
```

### Tasks

Tasks represent specific work units:

```python
task = Task(
    description="Task description",          # Required: What to do
    expected_output="Expected output",       # Required: Success criteria
    agent=agent,                             # Optional: Assigned agent
    context=[previous_task],                 # Optional: Dependencies
    output_file="path/to/output.md",        # Optional: Save results
    callback=lambda output: print(output),   # Optional: Completion callback
)
```

### Crews

Crews orchestrate agents and tasks:

```python
crew = Crew(
    agents=[agent1, agent2],                 # All crew members
    tasks=[task1, task2],                    # Tasks to complete
    process=ProcessType.SEQUENTIAL,          # Execution mode
    verbose=True,                            # Logging
    memory=True,                             # Enable memory
    manager_llm="model-name",               # For hierarchical mode
)

result = crew.launch(inputs={"var": "value"})
```

## Process Types

### Sequential Process

- Tasks execute in order
- Each task waits for previous to complete
- Output flows through task chain via `context`
- Best for: pipelines, workflows with clear dependencies

### Hierarchical Process

- Manager agent coordinates execution
- Tasks dynamically delegated to appropriate agents
- Manager synthesizes results
- Best for: complex projects, adaptive workflows

## Memory Integration

Enable memory for agents to learn and retain context:

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True  # Enables persistent memory
)
```

Memory is stored in `~/.deepagents/crews/{agent_name}/` and persists across sessions.

## Variable Substitution

Use `{variable}` syntax in descriptions and file paths:

```python
task = Task(
    description="Research {topic} in {year}",
    output_file="reports/{topic}_{year}.md"
)

crew.launch(inputs={"topic": "AI", "year": "2025"})
# Results in: "Research AI in 2025"
# Saves to: "reports/AI_2025.md"
```

## Advanced Features

### Task Dependencies (Context)

```python
task2 = Task(
    description="Analyze the research",
    agent=analyst,
    context=[research_task]  # Gets output from research_task
)
```

### Callbacks

```python
def on_complete(output):
    print(f"Task completed: {output.summary}")

task = Task(
    description="...",
    callback=on_complete
)
```

### Custom Manager

```python
manager = Agent(
    role="Project Manager",
    goal="Coordinate team",
    backstory="Experienced PM",
    allow_delegation=True
)

crew = Crew(
    agents=[...],
    tasks=[...],
    process=ProcessType.HIERARCHICAL,
    manager_agent=manager  # Use custom manager
)
```

## Architecture

The crew module maps CrewAI concepts to DeepAgents:

- **Agent** → `create_deep_agent()` with role-based system prompt
- **Task** → Work unit with dependencies and outputs
- **Crew (Sequential)** → Chain of agent invocations
- **Crew (Hierarchical)** → Manager with subagents
- **Memory** → CompositeBackend with FilesystemBackend

## Installation

The crew module is included with DeepAgents:

```bash
# Install DeepAgents
pip install -e libs/deepagents

# Optional: For YAML support
pip install pyyaml
```

## Comparison with CrewAI

| Feature | CrewAI | DeepAgents Crew |
|---------|--------|-----------------|
| Agent Definition | ✅ role/goal/backstory | ✅ Same |
| Task Management | ✅ Explicit tasks | ✅ Same |
| Sequential Process | ✅ | ✅ |
| Hierarchical Process | ✅ | ✅ |
| YAML Configuration | ✅ | ✅ |
| Memory System | ✅ ChromaDB + SQLite | ✅ Filesystem + State |
| Code Execution | ✅ Docker sandbox | ✅ Via middleware |
| Tool Integration | ✅ | ✅ Via DeepAgents tools |
| Custom Templates | ✅ | ✅ Via system_prompt |

## Next Steps

1. **Try the examples**: Run the example scripts to see crews in action
2. **Create your own crew**: Use the patterns above to build custom crews
3. **Explore middleware**: Leverage DeepAgents' middleware for advanced features
4. **Integrate tools**: Add custom tools to your agents
5. **Configure memory**: Tune memory settings for your use case

## Resources

- [DeepAgents Documentation](../../README.md)
- [CrewAI Documentation](https://docs.crewai.com)
- [Design Document](../../DESIGN_CREWAI_INTEGRATION.md)

## Support

For issues or questions:
- Create an issue in the repository
- Check existing examples and documentation
- Review the design document for architecture details
