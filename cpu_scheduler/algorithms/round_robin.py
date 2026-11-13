"""
Round Robin (RR) CPU Scheduling Algorithm.
"""

from collections import deque
from typing import List
from .base import BaseScheduler
from ..models import Process, ExecutionBlock, SimulationResult
from ..metrics import compute_simulation_metrics


class RoundRobinScheduler(BaseScheduler):
    """Round Robin Scheduling with configurable time quantum."""

    def __init__(self, time_quantum: float = 2.0):
        super().__init__(f"Round Robin (Quantum={time_quantum})")
        self.time_quantum = float(time_quantum)

    def run(self, processes: List[Process], **kwargs) -> SimulationResult:
        quantum = float(kwargs.get("quantum", self.time_quantum))
        if quantum <= 0:
            raise ValueError(f"Time quantum must be strictly positive (>0), got {quantum}")

        algo_name = f"Round Robin (Quantum={quantum:g})"
        procs = self.prepare_processes(processes)
        if not procs:
            return compute_simulation_metrics(algo_name, [], [])

        # Sort all processes initially by arrival time
        all_procs = sorted(procs, key=lambda p: (p.arrival_time, p.pid))
        ready_queue: deque[Process] = deque()
        timeline: List[ExecutionBlock] = []

        current_time = 0.0
        enqueued_set = set()

        # Enqueue initial arrivals at or before current_time
        for p in all_procs:
            if p.arrival_time <= current_time:
                ready_queue.append(p)
                enqueued_set.add(p.pid)

        completed_count = 0
        total_procs = len(all_procs)

        while completed_count < total_procs:
            if not ready_queue:
                # CPU is idle until next process arrival
                remaining_unarrived = [p for p in all_procs if p.pid not in enqueued_set]
                if not remaining_unarrived:
                    break

                next_arr_time = min(p.arrival_time for p in remaining_unarrived)
                if next_arr_time > current_time:
                    timeline.append(ExecutionBlock(
                        pid="IDLE",
                        start_time=current_time,
                        end_time=next_arr_time
                    ))
                    current_time = next_arr_time

                # Enqueue processes arriving at next_arr_time
                for p in all_procs:
                    if p.pid not in enqueued_set and p.arrival_time <= current_time:
                        ready_queue.append(p)
                        enqueued_set.add(p.pid)
                continue

            # Dequeue next process
            p = ready_queue.popleft()

            if p.start_time is None:
                p.start_time = current_time

            exec_time = min(quantum, p.remaining_time)
            finish_time = current_time + exec_time

            timeline.append(ExecutionBlock(
                pid=p.pid,
                start_time=current_time,
                end_time=finish_time
            ))

            p.remaining_time -= exec_time

            # Enqueue any new processes arriving during this time slice before re-enqueuing p
            for next_p in all_procs:
                if next_p.pid not in enqueued_set and next_p.arrival_time <= finish_time:
                    ready_queue.append(next_p)
                    enqueued_set.add(next_p.pid)

            if p.remaining_time > 1e-7:
                # Process still has CPU burst remaining; return to rear of queue
                ready_queue.append(p)
            else:
                p.remaining_time = 0.0
                p.completion_time = finish_time
                completed_count += 1

            current_time = finish_time

        return compute_simulation_metrics(algo_name, procs, timeline)

