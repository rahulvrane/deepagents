"""Configuration loading for CrewAI-style YAML definitions."""

from typing import Dict, Any
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def load_agents_config(config_path: str) -> Dict[str, Any]:
    """Load agents from YAML configuration.

    Args:
        config_path: Path to agents YAML file.

    Returns:
        Dict[str, Any]: Agent configurations keyed by agent name.

    Raises:
        ImportError: If PyYAML is not installed.
        FileNotFoundError: If config file doesn't exist.
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for YAML configuration. "
            "Install with: pip install pyyaml"
        )

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Agent config file not found: {config_path}")

    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config or {}


def load_tasks_config(config_path: str) -> Dict[str, Any]:
    """Load tasks from YAML configuration.

    Args:
        config_path: Path to tasks YAML file.

    Returns:
        Dict[str, Any]: Task configurations keyed by task name.

    Raises:
        ImportError: If PyYAML is not installed.
        FileNotFoundError: If config file doesn't exist.
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for YAML configuration. "
            "Install with: pip install pyyaml"
        )

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Task config file not found: {config_path}")

    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config or {}


def agent_from_config(config: Dict[str, Any]) -> 'Agent':
    """Create Agent from config dict.

    Args:
        config: Agent configuration dictionary.

    Returns:
        Agent: Agent instance.
    """
    from .agent import Agent
    return Agent(**config)


def task_from_config(config: Dict[str, Any]) -> 'Task':
    """Create Task from config dict.

    Args:
        config: Task configuration dictionary.

    Returns:
        Task: Task instance.
    """
    from .task import Task
    return Task(**config)
