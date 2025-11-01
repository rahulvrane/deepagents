"""Process types for crew execution."""

from enum import Enum


class ProcessType(Enum):
    """Crew process types.

    Attributes:
        SEQUENTIAL: Tasks execute in order, each waiting for previous to complete.
        HIERARCHICAL: Manager agent delegates tasks dynamically to worker agents.
    """

    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
