"""
Priority CPU Scheduling Algorithms:
- Priority Non-Preemptive
- Priority Preemptive
"""

from typing import List
from .base import BaseScheduler
from ..models import Process, ExecutionBlock, SimulationResult
from ..metrics import compute_simulation_metrics


class PriorityNonPreemptiveScheduler(BaseScheduler):
    """Priority Scheduling - Non-Preemptive."""

    def __init__(self, lower_is_higher: bool = True):
        super().__init__("Priority (Non-Preemptive)")
        self.lower_is_higher = lower_is_higher

    def run(self, processes: List[Process], **kwargs) -> SimulationResult:
        lower_is_higher = kwargs.get("lower_is_higher", self.lower_is_higher)
        procs = self.prepare_processes(processes)
        if not procs:
            return compute_simulation_metrics(self.name, [], [])

        uncompleted = list(procs)
        timeline: List[ExecutionBlock] = []
        current_time = 0.0

        while uncompleted:
            ready = [p for p in uncompleted if p.arrival_time <= current_time]

            if not ready:
                next_proc = min(uncompleted, key=lambda p: p.arrival_time)
                timeline.append(ExecutionBlock(
                    pid="IDLE",
                    start_time=current_time,
                    end_time=next_proc.arrival_time
                ))
                current_time = next_proc.arrival_time
                ready = [p for p in uncompleted if p.arrival_time <= current_time]

            # Determine best process based on priority policy
            if lower_is_higher:
                best_proc = min(ready, key=lambda p: (p.priority, p.arrival_time, p.pid))
            else:
                best_proc = max(ready, key=lambda p: (p.priority, -p.arrival_time, p.pid))

            best_proc.start_time = current_time
            finish_time = current_time + best_proc.burst_time
            timeline.append(ExecutionBlock(
                pid=best_proc.pid,
                start_time=current_time,
                end_time=finish_time
            ))
            current_time = finish_time
            best_proc.completion_time = current_time
            best_proc.remaining_time = 0.0

            uncompleted.remove(best_proc)

        return compute_simulation_metrics(self.name, procs, timeline)


class PriorityPreemptiveScheduler(BaseScheduler):
    """Priority Scheduling - Preemptive."""

    def __init__(self, lower_is_higher: bool = True):
        super().__init__("Priority (Preemptive)")
        self.lower_is_higher = lower_is_higher

    def run(self, processes: List[Process], **kwargs) -> SimulationResult:
        lower_is_higher = kwargs.get("lower_is_higher", self.lower_is_higher)
        procs = self.prepare_processes(processes)
        if not procs:
            return compute_simulation_metrics(self.name, [], [])

        timeline: List[ExecutionBlock] = []
        current_time = 0.0
        active_processes = list(procs)

        while any(p.remaining_time > 1e-7 for p in active_processes):
            ready = [p for p in active_processes if p.arrival_time <= current_time and p.remaining_time > 1e-7]

            if not ready:
                upcoming = [p for p in active_processes if p.arrival_time > current_time and p.remaining_time > 1e-7]
                next_arr_time = min(p.arrival_time for p in upcoming)
                timeline.append(ExecutionBlock(
                    pid="IDLE",
                    start_time=current_time,
                    end_time=next_arr_time
                ))
                current_time = next_arr_time
                continue

            # Pick process with best priority
            if lower_is_higher:
                best_proc = min(ready, key=lambda p: (p.priority, p.arrival_time, p.pid))
            else:
                best_proc = max(ready, key=lambda p: (p.priority, -p.arrival_time, p.pid))

            if best_proc.start_time is None:
                best_proc.start_time = current_time

            future_arrivals = [p.arrival_time for p in active_processes if p.arrival_time > current_time and p.remaining_time > 1e-7]
            next_arrival = min(future_arrivals) if future_arrivals else None

            if next_arrival is not None:
                time_to_arrival = next_arrival - current_time
                exec_duration = min(best_proc.remaining_time, time_to_arrival)
            else:
                exec_duration = best_proc.remaining_time

            end_time = current_time + exec_duration
            timeline.append(ExecutionBlock(
                pid=best_proc.pid,
                start_time=current_time,
                end_time=end_time
            ))

            best_proc.remaining_time -= exec_duration
            if best_proc.remaining_time <= 1e-7:
                best_proc.remaining_time = 0.0
                best_proc.completion_time = end_time

            current_time = end_time

        return compute_simulation_metrics(self.name, procs, timeline)

