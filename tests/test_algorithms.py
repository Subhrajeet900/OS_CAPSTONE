"""
Unit tests for CPU Scheduling algorithms and metrics.
"""

import pytest
from cpu_scheduler.models import Process, ExecutionBlock
from cpu_scheduler.algorithms import (
    FCFSScheduler,
    SJFNonPreemptiveScheduler,
    SRTFScheduler,
    PriorityNonPreemptiveScheduler,
    PriorityPreemptiveScheduler,
    RoundRobinScheduler
)
from cpu_scheduler.metrics import compute_simulation_metrics, merge_adjacent_timeline_blocks
from cpu_scheduler.exporter import export_results_to_csv, export_comparison_to_csv, export_results_to_pdf


def test_merge_adjacent_timeline_blocks():
    raw = [
        ExecutionBlock(pid="P1", start_time=0, end_time=2),
        ExecutionBlock(pid="P1", start_time=2, end_time=4),
        ExecutionBlock(pid="P2", start_time=4, end_time=6),
        ExecutionBlock(pid="IDLE", start_time=6, end_time=7),
        ExecutionBlock(pid="IDLE", start_time=7, end_time=9),
    ]
    merged = merge_adjacent_timeline_blocks(raw)
    assert len(merged) == 3
    assert merged[0].pid == "P1" and merged[0].start_time == 0 and merged[0].end_time == 4
    assert merged[1].pid == "P2" and merged[1].start_time == 4 and merged[1].end_time == 6
    assert merged[2].pid == "IDLE" and merged[2].start_time == 6 and merged[2].end_time == 9


def test_fcfs_simple():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=4),
        Process(pid="P2", arrival_time=1, burst_time=3),
        Process(pid="P3", arrival_time=2, burst_time=1),
    ]
    scheduler = FCFSScheduler()
    result = scheduler.run(procs)

    # P1: start 0, end 4, TAT 4, WT 0
    # P2: start 4, end 7, TAT 6, WT 3
    # P3: start 7, end 8, TAT 6, WT 5
    assert result.total_time == 8
    assert result.idle_time == 0
    p1 = next(p for p in result.processes if p.pid == "P1")
    p2 = next(p for p in result.processes if p.pid == "P2")
    p3 = next(p for p in result.processes if p.pid == "P3")

    assert p1.completion_time == 4
    assert p1.waiting_time == 0
    assert p2.completion_time == 7
    assert p2.waiting_time == 3
    assert p3.completion_time == 8
    assert p3.waiting_time == 5

    assert result.avg_waiting_time == pytest.approx((0 + 3 + 5) / 3)
    assert result.avg_turnaround_time == pytest.approx((4 + 6 + 6) / 3)


def test_fcfs_with_idle():
    procs = [
        Process(pid="P1", arrival_time=2, burst_time=3),
        Process(pid="P2", arrival_time=8, burst_time=2),
    ]
    scheduler = FCFSScheduler()
    result = scheduler.run(procs)

    # 0-2 idle, 2-5 P1, 5-8 idle, 8-10 P2
    assert result.total_time == 10
    assert result.idle_time == 5
    assert result.cpu_utilization == pytest.approx(50.0)


def test_sjf_non_preemptive():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=7),
        Process(pid="P2", arrival_time=2, burst_time=4),
        Process(pid="P3", arrival_time=4, burst_time=1),
        Process(pid="P4", arrival_time=5, burst_time=4),
    ]
    scheduler = SJFNonPreemptiveScheduler()
    result = scheduler.run(procs)

    # At 0: only P1 available -> runs 0..7
    # At 7: P2(4), P3(1), P4(4) available -> P3 runs 7..8
    # At 8: P2(4), P4(4) available -> P2 arrived earlier (2 < 5) -> P2 runs 8..12
    # At 12: P4 runs 12..16
    p1 = next(p for p in result.processes if p.pid == "P1")
    p2 = next(p for p in result.processes if p.pid == "P2")
    p3 = next(p for p in result.processes if p.pid == "P3")
    p4 = next(p for p in result.processes if p.pid == "P4")

    assert p1.completion_time == 7
    assert p3.completion_time == 8
    assert p2.completion_time == 12
    assert p4.completion_time == 16


def test_srtf_preemptive():
    # Silberschatz standard example
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=8),
        Process(pid="P2", arrival_time=1, burst_time=4),
        Process(pid="P3", arrival_time=2, burst_time=9),
        Process(pid="P4", arrival_time=3, burst_time=5),
    ]
    scheduler = SRTFScheduler()
    result = scheduler.run(procs)

    # P1 runs 0-1 (rem=7). At 1, P2 arrives (rem=4 < 7) -> P2 runs 1-5 (done).
    # At 5, P4(5), P1(7), P3(9) -> P4 runs 5-10 (done).
    # At 10, P1(7), P3(9) -> P1 runs 10-17 (done).
    # At 17, P3 runs 17-26 (done).
    p1 = next(p for p in result.processes if p.pid == "P1")
    p2 = next(p for p in result.processes if p.pid == "P2")
    p3 = next(p for p in result.processes if p.pid == "P3")
    p4 = next(p for p in result.processes if p.pid == "P4")

    assert p2.completion_time == 5
    assert p4.completion_time == 10
    assert p1.completion_time == 17
    assert p3.completion_time == 26

    assert p1.waiting_time == 9
    assert p2.waiting_time == 0
    assert p4.waiting_time == 2
    assert p3.waiting_time == 15
    assert result.avg_waiting_time == pytest.approx(6.5)


def test_priority_scheduling():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=10, priority=3),
        Process(pid="P2", arrival_time=0, burst_time=1, priority=1),
        Process(pid="P3", arrival_time=0, burst_time=2, priority=4),
    ]
    # lower_is_higher=True -> P2(1) > P1(3) > P3(4)
    sched = PriorityNonPreemptiveScheduler(lower_is_higher=True)
    res = sched.run(procs)

    p2 = next(p for p in res.processes if p.pid == "P2")
    p1 = next(p for p in res.processes if p.pid == "P1")
    p3 = next(p for p in res.processes if p.pid == "P3")

    assert p2.completion_time == 1
    assert p1.completion_time == 11
    assert p3.completion_time == 13


def test_round_robin():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=5),
        Process(pid="P2", arrival_time=1, burst_time=3),
        Process(pid="P3", arrival_time=2, burst_time=1),
    ]
    # Quantum = 2
    # 0-2: P1 (rem 3). Ready queue at 2: [P2 (arr 1), P3 (arr 2), P1 (rem 3)]
    # 2-4: P2 (rem 1). Ready queue at 4: [P3, P1, P2 (rem 1)]
    # 4-5: P3 (rem 0, finishes at 5). Ready queue at 5: [P1, P2]
    # 5-7: P1 (rem 1). Ready queue: [P2, P1]
    # 7-8: P2 (rem 0, finishes at 8). Ready queue: [P1]
    # 8-9: P1 (rem 0, finishes at 9).
    sched = RoundRobinScheduler(time_quantum=2)
    res = sched.run(procs)

    p1 = next(p for p in res.processes if p.pid == "P1")
    p2 = next(p for p in res.processes if p.pid == "P2")
    p3 = next(p for p in res.processes if p.pid == "P3")

    assert p3.completion_time == 5
    assert p2.completion_time == 8
    assert p1.completion_time == 9
    assert res.total_time == 9


def test_exports():
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=4),
        Process(pid="P2", arrival_time=1, burst_time=2),
    ]
    res = FCFSScheduler().run(procs)

    csv_data = export_results_to_csv(res)
    assert "Process ID,Arrival Time" in csv_data
    assert "P1,0.0,4.0" in csv_data

    comp_csv = export_comparison_to_csv([res])
    assert "Algorithm,Total Time" in comp_csv

    pdf_bytes = export_results_to_pdf(res)
    assert len(pdf_bytes) > 100
    assert pdf_bytes.startswith(b"%PDF")

