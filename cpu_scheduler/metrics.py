"""
Metrics calculation module for CPU Scheduling.
"""

from typing import List
from .models import Process, ExecutionBlock, SimulationResult


def merge_adjacent_timeline_blocks(raw_timeline: List[ExecutionBlock]) -> List[ExecutionBlock]:
    """Merges consecutive timeline blocks belonging to the same process or idle state."""
    if not raw_timeline:
        return []

    merged: List[ExecutionBlock] = []
    current = ExecutionBlock(
        pid=raw_timeline[0].pid,
        start_time=raw_timeline[0].start_time,
        end_time=raw_timeline[0].end_time
    )

    for block in raw_timeline[1:]:
        if block.pid == current.pid and abs(block.start_time - current.end_time) < 1e-7:
            current.end_time = block.end_time
        else:
            if current.duration > 0:
                merged.append(current)
            current = ExecutionBlock(
                pid=block.pid,
                start_time=block.start_time,
                end_time=block.end_time
            )

    if current.duration > 0:
        merged.append(current)

    return merged


def compute_simulation_metrics(
    algorithm_name: str,
    processes: List[Process],
    timeline: List[ExecutionBlock]
) -> SimulationResult:
    """Computes comprehensive scheduling metrics from execution history."""
    clean_timeline = merge_adjacent_timeline_blocks(timeline)

    n = len(processes)
    if n == 0:
        return SimulationResult(
            algorithm_name=algorithm_name,
            processes=[],
            timeline=[],
            total_time=0.0,
            idle_time=0.0,
            avg_waiting_time=0.0,
            avg_turnaround_time=0.0,
            avg_response_time=0.0,
            cpu_utilization=0.0,
            throughput=0.0
        )

    # Calculate per-process metrics
    for p in processes:
        if p.completion_time is not None:
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            if p.start_time is not None:
                p.response_time = p.start_time - p.arrival_time
            else:
                p.response_time = p.waiting_time
        else:
            p.turnaround_time = 0.0
            p.waiting_time = 0.0
            p.response_time = 0.0

    total_time = clean_timeline[-1].end_time if clean_timeline else 0.0
    idle_time = sum(b.duration for b in clean_timeline if b.is_idle)
    busy_time = max(0.0, total_time - idle_time)

    cpu_utilization = (busy_time / total_time * 100.0) if total_time > 0 else 0.0
    throughput = (n / total_time) if total_time > 0 else 0.0

    avg_waiting_time = sum(p.waiting_time or 0.0 for p in processes) / n
    avg_turnaround_time = sum(p.turnaround_time or 0.0 for p in processes) / n
    avg_response_time = sum(p.response_time or 0.0 for p in processes) / n

    return SimulationResult(
        algorithm_name=algorithm_name,
        processes=processes,
        timeline=clean_timeline,
        total_time=total_time,
        idle_time=idle_time,
        avg_waiting_time=avg_waiting_time,
        avg_turnaround_time=avg_turnaround_time,
        avg_response_time=avg_response_time,
        cpu_utilization=cpu_utilization,
        throughput=throughput
    )

