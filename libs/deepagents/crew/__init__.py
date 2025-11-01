"""CrewAI-style agent definitions for DeepAgents.

This module provides a CrewAI-compatible interface for defining agents, tasks,
and crews in the DeepAgents framework.
"""

from .agent import Agent
from .task import Task, TaskOutput
from .crew import Crew
from .process import ProcessType
from .decorators import CrewBase, agent, task, crew
from .config import load_agents_config, load_tasks_config

__all__ = [
    "Agent",
    "Task",
    "TaskOutput",
    "Crew",
    "ProcessType",
    "CrewBase",
    "agent",
    "task",
    "crew",
    "load_agents_config",
    "load_tasks_config",
]
