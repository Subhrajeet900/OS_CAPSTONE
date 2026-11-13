"""
Preconfigured textbook and real-world process benchmark presets.
"""

from typing import List, Dict
from .models import Process


def get_presets() -> Dict[str, Dict[str, any]]:
    """Returns a dictionary of predefined benchmark test cases."""
    return {
        "Classic Convoy Effect (Silberschatz FCFS demo)": {
            "description": "Demonstrates the Convoy Effect where short processes wait behind a heavy CPU burst job in FCFS.",
            "recommended_quantum": 4,
            "processes": [
                Process(pid="P1", arrival_time=0, burst_time=24, priority=3),
                Process(pid="P2", arrival_time=0, burst_time=3, priority=1),
                Process(pid="P3", arrival_time=0, burst_time=3, priority=2),
            ]
        },
        "SRTF vs Non-Preemptive SJF (Standard)": {
            "description": "Processes arriving at staggered intervals, highlighting preemption benefits in SRTF.",
            "recommended_quantum": 2,
            "processes": [
                Process(pid="P1", arrival_time=0, burst_time=8, priority=3),
                Process(pid="P2", arrival_time=1, burst_time=4, priority=1),
                Process(pid="P3", arrival_time=2, burst_time=9, priority=4),
                Process(pid="P4", arrival_time=3, burst_time=5, priority=2),
            ]
        },
        "Priority Scheduling Demonstration": {
            "description": "5 processes with varying priorities demonstrating preemptive vs non-preemptive priority execution.",
            "recommended_quantum": 2,
            "processes": [
                Process(pid="P1", arrival_time=0, burst_time=10, priority=3),
                Process(pid="P2", arrival_time=1, burst_time=1, priority=1),
                Process(pid="P3", arrival_time=2, burst_time=2, priority=4),
                Process(pid="P4", arrival_time=3, burst_time=1, priority=5),
                Process(pid="P5", arrival_time=4, burst_time=5, priority=2),
            ]
        },
        "Round Robin Interactive Slicing": {
            "description": "Multiple processes with varying bursts, ideal for experimenting with different time quantum values.",
            "recommended_quantum": 3,
            "processes": [
                Process(pid="P1", arrival_time=0, burst_time=5, priority=2),
                Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
                Process(pid="P3", arrival_time=2, burst_time=8, priority=3),
                Process(pid="P4", arrival_time=3, burst_time=6, priority=2),
            ]
        },
        "CPU Idle Gaps Simulation": {
            "description": "Staggered arrivals with idle CPU gaps between job submissions, testing scheduler idle time handling.",
            "recommended_quantum": 2,
            "processes": [
                Process(pid="P1", arrival_time=0, burst_time=3, priority=1),
                Process(pid="P2", arrival_time=6, burst_time=4, priority=2),
                Process(pid="P3", arrival_time=13, burst_time=2, priority=1),
            ]
        }
    }

