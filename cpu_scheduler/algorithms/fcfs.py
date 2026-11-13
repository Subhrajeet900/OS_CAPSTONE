"""
First-Come, First-Served (FCFS) CPU Scheduling Algorithm.
"""

from typing import List
from .base import BaseScheduler
from ..models import Process, ExecutionBlock, SimulationResult
from ..metrics import compute_simulation_metrics


class FCFSScheduler(BaseScheduler):
    """First-Come, First-Served (Non-preemptive) Scheduler."""

    def __init__(self):
        super().__init__("FCFS (First Come First Serve)")

    def run(self, processes: List[Process], **kwargs) -> SimulationResult:
        procs = self.prepare_processes(processes)
        if not procs:
            return compute_simulation_metrics(self.name, [], [])

        # Sort primarily by arrival time; keep original order for ties
        procs.sort(key=lambda p: p.arrival_time)

        current_time = 0.0
        timeline: List[ExecutionBlock] = []

        for p in procs:
            if current_time < p.arrival_time:
                # CPU is idle until process arrives
                timeline.append(ExecutionBlock(
                    pid="IDLE",
                    start_time=current_time,
                    end_time=p.arrival_time
                ))
                current_time = p.arrival_time

            p.start_time = current_time
            finish_time = current_time + p.burst_time
            timeline.append(ExecutionBlock(
                pid=p.pid,
                start_time=current_time,
                end_time=finish_time
            ))
            current_time = finish_time
            p.completion_time = current_time
            p.remaining_time = 0.0

        return compute_simulation_metrics(self.name, procs, timeline)

