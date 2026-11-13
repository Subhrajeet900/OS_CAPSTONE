"""
Matplotlib-based Visualizer for CPU Scheduling Gantt Charts and Comparisons.
"""

from typing import List, Optional, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# Distinct modern color palette for processes
PALETTE = [
    "#4361EE",  # Vibrant Blue
    "#3A0CA3",  # Indigo
    "#7209B7",  # Purple
    "#F72585",  # Rose Pink
    "#4CC9F0",  # Sky Blue
    "#2EC4B6",  # Teal
    "#FF9F1C",  # Orange
    "#E71D36",  # Crimson
    "#06D6A0",  # Mint Green
    "#118AB2",  # Ocean Blue
    "#8338EC",  # Violet
    "#FB5607",  # Vermilion
]

IDLE_COLOR = "#D1D5DB"  # Neutral Light Gray for Idle slots


def get_color_map(process_ids: List[str]) -> Dict[str, str]:
    """Assigns distinct colors to processes."""
    unique_pids = sorted(list({pid for pid in process_ids if pid.upper() not in ("IDLE", "[IDLE]", "IDLE CPU")}))
    color_map = {}
    for idx, pid in enumerate(unique_pids):
        color_map[pid] = PALETTE[idx % len(PALETTE)]
    return color_map


def plot_gantt_chart(simulation_result, title: Optional[str] = None) -> plt.Figure:
    """Generates an aesthetic, clear Matplotlib Gantt chart for a single simulation result."""
    timeline = simulation_result.timeline
    if not timeline:
        fig, ax = plt.subplots(figsize=(10, 2.5))
        ax.text(0.5, 0.5, "No execution timeline available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    pids = [b.pid for b in timeline]
    color_map = get_color_map(pids)

    fig, ax = plt.subplots(figsize=(max(11, len(timeline) * 0.9), 3.2), dpi=120)

    # Gather transition timestamps for x-ticks
    timestamps = [0.0]
    for block in timeline:
        timestamps.append(block.end_time)
    timestamps = sorted(list(set(timestamps)))

    bar_height = 0.55
    y_pos = 0.5

    for block in timeline:
        start = block.start_time
        width = block.duration

        if block.is_idle:
            color = IDLE_COLOR
            hatch = "///"
            text_color = "#374151"
            label = "IDLE"
        else:
            color = color_map.get(block.pid, "#4B5563")
            hatch = None
            text_color = "#FFFFFF"
            label = block.pid

        # Draw execution box
        ax.broken_barh(
            [(start, width)],
            (y_pos - bar_height / 2, bar_height),
            facecolors=color,
            edgecolor="#1F2937",
            linewidth=1.2,
            hatch=hatch
        )

        # Draw label inside or above block
        if width > 0.05:
            mid = start + width / 2.0
            ax.text(
                mid,
                y_pos,
                f"{label}\n({width:g})",
                ha="center",
                va="center",
                color=text_color,
                fontsize=9.5,
                fontweight="bold"
            )

    chart_title = title or f"Gantt Chart - {simulation_result.algorithm_name}"
    ax.set_title(chart_title, fontsize=13, fontweight="bold", pad=14, color="#111827")
    ax.set_xlabel("Time Units", fontsize=11, fontweight="semibold", labelpad=8)
    ax.set_yticks([])
    ax.set_ylim(0, 1)

    max_time = timestamps[-1] if timestamps else 1
    ax.set_xlim(-0.2, max_time + 0.5)

    # Selectively display x-ticks so labels don't collide if there are many steps
    if len(timestamps) <= 25:
        ax.set_xticks(timestamps)
    else:
        # Uniform ticks plus final time
        step = max(1, int(max_time / 15))
        ticks = list(range(0, int(max_time) + 1, step))
        if max_time not in ticks:
            ticks.append(max_time)
        ax.set_xticks(ticks)

    ax.tick_params(axis="x", labelsize=9.5)
    ax.grid(axis="x", linestyle="--", alpha=0.5, color="#9CA3AF")
    ax.set_axisbelow(True)

    # Build Legend
    legend_patches = [
        mpatches.Patch(color=c, label=pid)
        for pid, c in sorted(color_map.items())
    ]
    if any(b.is_idle for b in timeline):
        legend_patches.append(mpatches.Patch(facecolor=IDLE_COLOR, hatch="///", edgecolor="#374151", label="Idle CPU"))

    ax.legend(
        handles=legend_patches,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.32),
        ncol=min(len(legend_patches), 6),
        frameon=True,
        fontsize=9
    )

    plt.tight_layout()
    return fig


def plot_comparison_chart(simulation_results: list) -> plt.Figure:
    """Plots comparative bar charts of Average Waiting and Turnaround times across algorithms."""
    if not simulation_results:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.5, "No simulation results to compare", ha="center", va="center")
        ax.axis("off")
        return fig

    algos = [r.algorithm_name for r in simulation_results]
    avg_wt = [r.avg_waiting_time for r in simulation_results]
    avg_tat = [r.avg_turnaround_time for r in simulation_results]
    avg_rt = [r.avg_response_time for r in simulation_results]

    import numpy as np
    x = np.arange(len(algos))
    width = 0.25

    fig, ax = plt.subplots(figsize=(max(9, len(algos) * 2.2), 5), dpi=120)

    rects1 = ax.bar(x - width, avg_wt, width, label="Avg Waiting Time", color="#4361EE", edgecolor="#1E3A8A")
    rects2 = ax.bar(x, avg_tat, width, label="Avg Turnaround Time", color="#F72585", edgecolor="#880E4F")
    rects3 = ax.bar(x + width, avg_rt, width, label="Avg Response Time", color="#06D6A0", edgecolor="#004D40")

    ax.set_ylabel("Time Units", fontsize=11, fontweight="semibold")
    ax.set_title("Performance Comparison Across CPU Scheduling Algorithms", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(algos, rotation=15, ha="right", fontsize=9.5, fontweight="medium")
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    # Attach value labels above bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8.5,
                fontweight="bold"
            )

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.tight_layout()
    return fig

