"""
Base class and common interfaces for scheduling algorithms.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models import Process, SimulationResult


class BaseScheduler(ABC):
    """Abstract base scheduler for all scheduling algorithms."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, processes: List[Process], **kwargs) -> SimulationResult:
        """Execute the scheduling algorithm on the provided processes."""
        pass

    @staticmethod
    def prepare_processes(processes: List[Process]) -> List[Process]:
        """Clone and validate processes."""
        if not processes:
            return []
        cloned = [p.clone() for p in processes]
        for p in cloned:
            if p.burst_time <= 0:
                raise ValueError(f"Process {p.pid} must have burst_time > 0, got {p.burst_time}")
            if p.arrival_time < 0:
                raise ValueError(f"Process {p.pid} must have arrival_time >= 0, got {p.arrival_time}")
        return cloned

