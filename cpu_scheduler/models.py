"""
Data models for CPU Scheduling Visualizer.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Process:
    """Represents a process to be scheduled."""
    pid: str
    arrival_time: float
    burst_time: float
    priority: int = 0

    # Runtime/Computed metrics
    remaining_time: float = field(init=False)
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    turnaround_time: Optional[float] = None
    waiting_time: Optional[float] = None
    response_time: Optional[float] = None

    def __post_init__(self):
        self.remaining_time = float(self.burst_time)
        self.arrival_time = float(self.arrival_time)
        self.burst_time = float(self.burst_time)
        self.priority = int(self.priority)

    def reset(self):
        """Reset runtime metrics for a fresh simulation run."""
        self.remaining_time = float(self.burst_time)
        self.start_time = None
        self.completion_time = None
        self.turnaround_time = None
        self.waiting_time = None
        self.response_time = None

    def clone(self) -> 'Process':
        """Clone the process with pristine initial state."""
        return Process(
            pid=self.pid,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert process and its computed metrics to a dictionary."""
        return {
            "Process ID": self.pid,
            "Arrival Time": self.arrival_time,
            "Burst Time": self.burst_time,
            "Priority": self.priority,
            "Start Time": self.start_time,
            "Completion Time": self.completion_time,
            "Turnaround Time": self.turnaround_time,
            "Waiting Time": self.waiting_time,
            "Response Time": self.response_time,
        }


@dataclass
class ExecutionBlock:
    """Represents an execution interval on the CPU."""
    pid: str
    start_time: float
    end_time: float

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def is_idle(self) -> bool:
        return self.pid.upper() in ("IDLE", "[IDLE]", "IDLE CPU")


@dataclass
class SimulationResult:
    """Holds complete results of a CPU scheduling simulation."""
    algorithm_name: str
    processes: List[Process]
    timeline: List[ExecutionBlock]
    total_time: float = 0.0
    idle_time: float = 0.0
    avg_waiting_time: float = 0.0
    avg_turnaround_time: float = 0.0
    avg_response_time: float = 0.0
    cpu_utilization: float = 0.0
    throughput: float = 0.0

    def get_process_dataframe_dict(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in sorted(self.processes, key=lambda x: x.pid)]

    def get_summary_dict(self) -> Dict[str, Any]:
        return {
            "Algorithm": self.algorithm_name,
            "Total Time": round(self.total_time, 2),
            "Idle Time": round(self.idle_time, 2),
            "Avg Waiting Time": round(self.avg_waiting_time, 2),
            "Avg Turnaround Time": round(self.avg_turnaround_time, 2),
            "Avg Response Time": round(self.avg_response_time, 2),
            "CPU Utilization (%)": round(self.cpu_utilization, 2),
            "Throughput (proc/unit time)": round(self.throughput, 4),
        }

