"""
Command-Line Interface for Smart CPU Scheduling Visualizer.
Allows headless simulations, benchmarking, and CSV/PDF export from bash scripts or terminal.
"""

import argparse
import sys
import os
import csv
import json
from typing import List

from cpu_scheduler.models import Process, SimulationResult
from cpu_scheduler.algorithms import (
    FCFSScheduler,
    SJFNonPreemptiveScheduler,
    SRTFScheduler,
    PriorityNonPreemptiveScheduler,
    PriorityPreemptiveScheduler,
    RoundRobinScheduler
)
from cpu_scheduler.visualizer import plot_gantt_chart, plot_comparison_chart
from cpu_scheduler.exporter import (
    export_results_to_csv,
    export_comparison_to_csv,
    export_results_to_pdf
)


def load_processes_from_file(file_path: str) -> List[Process]:
    """Reads processes from a CSV or JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    processes = []
    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                processes.append(Process(
                    pid=str(item.get("pid", item.get("Process ID", "P"))),
                    arrival_time=float(item.get("arrival_time", item.get("Arrival Time", 0))),
                    burst_time=float(item.get("burst_time", item.get("Burst Time", 1))),
                    priority=int(item.get("priority", item.get("Priority", 0)))
                ))
    else:
        # Default CSV loader
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Normalize column keys
            for row in reader:
                cleaned = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in row.items() if k}
                pid = cleaned.get("pid") or cleaned.get("process_id") or f"P{len(processes)+1}"
                arrival = float(cleaned.get("arrival_time") or cleaned.get("arrival") or 0.0)
                burst = float(cleaned.get("burst_time") or cleaned.get("burst") or 1.0)
                priority = int(float(cleaned.get("priority") or 0))
                processes.append(Process(pid=pid, arrival_time=arrival, burst_time=burst, priority=priority))

    return processes


def print_simulation_table(result: SimulationResult):
    """Prints a formatted ASCII table of the simulation results."""
    print(f"\n{'='*78}")
    print(f" Algorithm: {result.algorithm_name}")
    print(f"{'='*78}")
    header = f"{'PID':<6} | {'Arrival':<8} | {'Burst':<6} | {'Priority':<8} | {'CT':<6} | {'TAT':<6} | {'WT':<6} | {'RT':<6}"
    print(header)
    print("-" * len(header))

    for p in sorted(result.processes, key=lambda x: x.pid):
        ct_str = f"{p.completion_time:g}" if p.completion_time is not None else "-"
        tat_str = f"{p.turnaround_time:g}" if p.turnaround_time is not None else "-"
        wt_str = f"{p.waiting_time:g}" if p.waiting_time is not None else "-"
        rt_str = f"{p.response_time:g}" if p.response_time is not None else "-"
        print(f"{p.pid:<6} | {p.arrival_time:<8g} | {p.burst_time:<6g} | {p.priority:<8} | {ct_str:<6} | {tat_str:<6} | {wt_str:<6} | {rt_str:<6}")

    print("-" * len(header))
    print(f"Total Execution Time : {result.total_time:g}")
    print(f"Total Idle Time      : {result.idle_time:g}")
    print(f"Average Waiting Time : {result.avg_waiting_time:.2f}")
    print(f"Average Turnaround   : {result.avg_turnaround_time:.2f}")
    print(f"Average Response Time: {result.avg_response_time:.2f}")
    print(f"CPU Utilization      : {result.cpu_utilization:.2f}%")
    print(f"Throughput           : {result.throughput:.4f} processes/unit")

    # Gantt Timeline text representation
    print("\nGantt Timeline:")
    timeline_str = " | ".join(f"[{b.start_time:g} - {b.end_time:g}: {b.pid}]" for b in result.timeline)
    print(timeline_str)
    print(f"{'='*78}\n")


def print_comparison_table(results: List[SimulationResult]):
    """Prints comparative summary across multiple algorithms."""
    print(f"\n{'='*88}")
    print(" MULTI-ALGORITHM BENCHMARK COMPARISON")
    print(f"{'='*88}")
    header = f"{'Algorithm':<28} | {'Avg WT':<8} | {'Avg TAT':<8} | {'Avg RT':<8} | {'CPU Util':<10} | {'Throughput':<10}"
    print(header)
    print("-" * len(header))

    best_algo = min(results, key=lambda r: r.avg_waiting_time)

    for r in results:
        marker = " *" if r == best_algo else ""
        print(f"{r.algorithm_name:<28} | {r.avg_waiting_time:<8.2f} | {r.avg_turnaround_time:<8.2f} | {r.avg_response_time:<8.2f} | {r.cpu_utilization:<9.1f}% | {r.throughput:<10.4f}{marker}")

    print("-" * len(header))
    print(f"* Best Algorithm by Minimum Waiting Time: {best_algo.algorithm_name} (Avg WT: {best_algo.avg_waiting_time:.2f})")
    print(f"{'='*88}\n")


def main():
    parser = argparse.ArgumentParser(description="Smart CPU Scheduling Visualizer CLI")
    parser.add_argument("--file", "-f", required=True, help="Path to input processes CSV/JSON file")
    parser.add_argument("--algo", "-a", default="all",
                        choices=["all", "fcfs", "sjf", "srtf", "priority", "priority_p", "rr"],
                        help="Scheduling algorithm to execute")
    parser.add_argument("--quantum", "-q", type=float, default=2.0, help="Time quantum for Round Robin")
    parser.add_argument("--priority-order", default="lower", choices=["lower", "higher"],
                        help="Priority ordering: 'lower' (0 is highest) or 'higher'")
    parser.add_argument("--export-csv", help="File path to save CSV output")
    parser.add_argument("--export-pdf", help="File path to save PDF report")
    parser.add_argument("--plot", help="File path to save Gantt chart PNG")

    args = parser.parse_args()

    try:
        processes = load_processes_from_file(args.file)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    if not processes:
        print("Error: No processes found in input file.", file=sys.stderr)
        sys.exit(1)

    lower_is_higher = (args.priority_order == "lower")

    schedulers = {
        "fcfs": FCFSScheduler(),
        "sjf": SJFNonPreemptiveScheduler(),
        "srtf": SRTFScheduler(),
        "priority": PriorityNonPreemptiveScheduler(lower_is_higher=lower_is_higher),
        "priority_p": PriorityPreemptiveScheduler(lower_is_higher=lower_is_higher),
        "rr": RoundRobinScheduler(time_quantum=args.quantum),
    }

    results = []

    if args.algo == "all":
        for algo_key, sched in schedulers.items():
            res = sched.run(processes, quantum=args.quantum, lower_is_higher=lower_is_higher)
            results.append(res)
            print_simulation_table(res)

        print_comparison_table(results)

        if args.export_csv:
            csv_content = export_comparison_to_csv(results)
            with open(args.export_csv, "w", encoding="utf-8") as f:
                f.write(csv_content)
            print(f"[OK] Comparison CSV exported to: {args.export_csv}")

        if args.export_pdf:
            best_res = min(results, key=lambda r: r.avg_waiting_time)
            fig_gantt = plot_gantt_chart(best_res)
            pdf_bytes = export_results_to_pdf(best_res, fig_gantt=fig_gantt, comparison_results=results)
            with open(args.export_pdf, "wb") as f:
                f.write(pdf_bytes)
            print(f"[OK] Comprehensive PDF benchmark report exported to: {args.export_pdf}")

    else:
        sched = schedulers[args.algo]
        res = sched.run(processes, quantum=args.quantum, lower_is_higher=lower_is_higher)
        print_simulation_table(res)
        results = [res]

        if args.plot:
            fig = plot_gantt_chart(res)
            fig.savefig(args.plot, bbox_inches="tight", dpi=150)
            print(f"[OK] Gantt chart saved to: {args.plot}")

        if args.export_csv:
            csv_content = export_results_to_csv(res)
            with open(args.export_csv, "w", encoding="utf-8") as f:
                f.write(csv_content)
            print(f"[OK] CSV exported to: {args.export_csv}")

        if args.export_pdf:
            fig = plot_gantt_chart(res)
            pdf_bytes = export_results_to_pdf(res, fig_gantt=fig)
            with open(args.export_pdf, "wb") as f:
                f.write(pdf_bytes)
            print(f"[OK] PDF report exported to: {args.export_pdf}")


if __name__ == "__main__":
    main()

