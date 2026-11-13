"""
Smart CPU Scheduling Visualizer package.
"""

from .models import Process, ExecutionBlock, SimulationResult
from .algorithms import (
    BaseScheduler,
    FCFSScheduler,
    SJFNonPreemptiveScheduler,
    SRTFScheduler,
    PriorityNonPreemptiveScheduler,
    PriorityPreemptiveScheduler,
    RoundRobinScheduler
)
from .metrics import compute_simulation_metrics
from .visualizer import plot_gantt_chart, plot_comparison_chart
from .exporter import export_results_to_csv, export_comparison_to_csv, export_results_to_pdf
from .presets import get_presets

__all__ = [
    "Process",
    "ExecutionBlock",
    "SimulationResult",
    "BaseScheduler",
    "FCFSScheduler",
    "SJFNonPreemptiveScheduler",
    "SRTFScheduler",
    "PriorityNonPreemptiveScheduler",
    "PriorityPreemptiveScheduler",
    "RoundRobinScheduler",
    "compute_simulation_metrics",
    "plot_gantt_chart",
    "plot_comparison_chart",
    "export_results_to_csv",
    "export_comparison_to_csv",
    "export_results_to_pdf",
    "get_presets",
]

