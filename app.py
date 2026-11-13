"""
Smart CPU Scheduling Visualizer - Streamlit Application
A modern, interactive visualizer demonstrating OS CPU scheduling algorithms,
Gantt charts, performance metrics, side-by-side benchmarks, and CSV/PDF reports.
"""

import os
import tempfile

# Prevent matplotlib cache permission warning
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
from cpu_scheduler.presets import get_presets

# Configure Streamlit page layout and styling
st.set_page_config(
    page_title="Smart CPU Scheduling Visualizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished typography, badges, and card containers
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1D4ED8;
    }
    .metric-lbl {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
    }
    .badge-best {
        background-color: #10B981;
        color: white;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize process list and input mode in Streamlit session state."""
    if "processes" not in st.session_state:
        presets = get_presets()
        st.session_state.processes = [p.clone() for p in presets["Classic Convoy Effect (Silberschatz FCFS demo)"]["processes"]]
    if "time_quantum" not in st.session_state:
        st.session_state.time_quantum = 2.0
    if "priority_order" not in st.session_state:
        st.session_state.priority_order = "Lower value = Higher priority (Standard)"


init_session_state()

# ------------------------------------------------------------------------------
# SIDEBAR: Configuration & Process Management
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Visualizer Controls")

    # Mode Selection
    view_mode = st.radio(
        "Simulation Mode",
        ["Single Algorithm Detailed View", "Compare All Algorithms (Benchmark)"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📋 Input Method")
    input_source = st.selectbox(
        "Choose how to load processes:",
        ["Curated Presets", "Interactive Table Editor", "Upload CSV File", "Random Generator"]
    )

    presets = get_presets()

    if input_source == "Curated Presets":
        selected_preset_name = st.selectbox("Select Preset Case:", list(presets.keys()))
        preset_info = presets[selected_preset_name]
        st.info(f"💡 {preset_info['description']}")
        if st.button("Load Preset Data", use_container_width=True):
            st.session_state.processes = [p.clone() for p in preset_info["processes"]]
            st.session_state.time_quantum = float(preset_info.get("recommended_quantum", 2.0))
            st.rerun()

    elif input_source == "Upload CSV File":
        uploaded_file = st.file_uploader("Upload CSV (cols: pid, arrival_time, burst_time, priority)", type=["csv"])
        if uploaded_file is not None:
            try:
                df_up = pd.read_csv(uploaded_file)
                procs_up = []
                for idx, row in df_up.iterrows():
                    cleaned = {str(k).strip().lower().replace(" ", "_"): v for k, v in row.items()}
                    pid = str(cleaned.get("pid") or cleaned.get("process_id") or f"P{idx+1}")
                    at = float(cleaned.get("arrival_time") or cleaned.get("arrival") or 0.0)
                    bt = float(cleaned.get("burst_time") or cleaned.get("burst") or 1.0)
                    pri = int(float(cleaned.get("priority") or 0))
                    if bt <= 0:
                        st.error(f"Row {idx+1} ({pid}): Burst time must be > 0")
                        break
                    procs_up.append(Process(pid=pid, arrival_time=at, burst_time=bt, priority=pri))
                else:
                    if st.button("Apply Uploaded Processes", use_container_width=True):
                        st.session_state.processes = procs_up
                        st.success(f"Loaded {len(procs_up)} processes successfully!")
                        st.rerun()
            except Exception as ex:
                st.error(f"Error parsing CSV: {ex}")

    elif input_source == "Random Generator":
        n_procs = st.slider("Number of processes", 3, 10, 5)
        max_arr = st.slider("Max Arrival Time", 0, 15, 6)
        max_burst = st.slider("Max Burst Time", 1, 20, 10)
        if st.button("Generate Random Set", use_container_width=True):
            import random
            random_procs = []
            curr_at = 0
            for i in range(1, n_procs + 1):
                curr_at += random.randint(0, max(1, max_arr // n_procs))
                bt = random.randint(1, max_burst)
                pri = random.randint(1, 5)
                random_procs.append(Process(pid=f"P{i}", arrival_time=curr_at, burst_time=bt, priority=pri))
            st.session_state.processes = random_procs
            st.rerun()

    st.markdown("---")
    st.markdown("### 🎛️ Algorithm Parameters")

    time_quantum = st.number_input(
        "Round Robin Time Quantum",
        min_value=0.5,
        max_value=50.0,
        value=float(st.session_state.time_quantum),
        step=0.5,
        help="CPU time slice allocated to each process before context switching."
    )
    st.session_state.time_quantum = time_quantum

    priority_order_choice = st.selectbox(
        "Priority Convention",
        ["Lower value = Higher priority (Standard)", "Higher value = Higher priority"],
        index=0 if "Lower" in st.session_state.priority_order else 1
    )
    st.session_state.priority_order = priority_order_choice
    lower_is_higher = ("Lower" in priority_order_choice)


# ------------------------------------------------------------------------------
# MAIN CONTENT AREA
# ------------------------------------------------------------------------------
st.markdown('<div class="main-title">⚡ Smart CPU Scheduling Visualizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Interactive operating system simulator demonstrating how the CPU schedules processes, '
    'generates Gantt charts, computes turnaround/waiting times, and evaluates algorithmic performance.</div>',
    unsafe_allow_html=True
)

# Process Table Editor
with st.expander("📝 View & Edit Processes (Interactive Table)", expanded=(input_source == "Interactive Table Editor")):
    st.markdown("You can edit values directly in the table, add rows, or remove processes:")
    current_data = [
        {
            "PID": p.pid,
            "Arrival Time": float(p.arrival_time),
            "Burst Time": float(p.burst_time),
            "Priority": int(p.priority)
        }
        for p in st.session_state.processes
    ]
    df_editor = pd.DataFrame(current_data)
    edited_df = st.data_editor(
        df_editor,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor_table"
    )

    # Sync back to session state if valid
    updated_procs = []
    valid = True
    for idx, row in edited_df.iterrows():
        pid = str(row["PID"]).strip()
        try:
            at = float(row["Arrival Time"])
            bt = float(row["Burst Time"])
            pri = int(row["Priority"])
            if bt <= 0:
                st.warning(f"Row {idx+1} ({pid}): Burst time must be > 0. Skipping.")
                valid = False
            elif at < 0:
                st.warning(f"Row {idx+1} ({pid}): Arrival time cannot be negative. Skipping.")
                valid = False
            else:
                updated_procs.append(Process(pid=pid, arrival_time=at, burst_time=bt, priority=pri))
        except (ValueError, TypeError):
            valid = False

    if valid and updated_procs and len(updated_procs) != len(st.session_state.processes):
        st.session_state.processes = updated_procs

active_processes = [p.clone() for p in st.session_state.processes]

if not active_processes:
    st.warning("No processes found! Please add or load processes to begin the simulation.")
    st.stop()


# Build algorithm instances
schedulers = {
    "FCFS (First Come First Serve)": FCFSScheduler(),
    "SJF (Non-Preemptive)": SJFNonPreemptiveScheduler(),
    "SRTF (Preemptive SJF)": SRTFScheduler(),
    "Priority (Non-Preemptive)": PriorityNonPreemptiveScheduler(lower_is_higher=lower_is_higher),
    "Priority (Preemptive)": PriorityPreemptiveScheduler(lower_is_higher=lower_is_higher),
    "Round Robin": RoundRobinScheduler(time_quantum=time_quantum),
}


# ==============================================================================
# MODE 1: SINGLE ALGORITHM DETAILED VIEW
# ==============================================================================
if view_mode == "Single Algorithm Detailed View":
    col_algo, col_info = st.columns([2, 3])
    with col_algo:
        selected_algo = st.selectbox("Select Scheduling Algorithm:", list(schedulers.keys()), index=0)

    scheduler = schedulers[selected_algo]
    sim_result = scheduler.run(
        active_processes,
        quantum=time_quantum,
        lower_is_higher=lower_is_higher
    )

    # Display KPI Cards
    st.markdown("### 📊 Performance Summary")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{sim_result.avg_waiting_time:.2f}</div><div class="metric-lbl">Avg Waiting Time</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{sim_result.avg_turnaround_time:.2f}</div><div class="metric-lbl">Avg Turnaround</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{sim_result.avg_response_time:.2f}</div><div class="metric-lbl">Avg Response</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{sim_result.cpu_utilization:.1f}%</div><div class="metric-lbl">CPU Utilization</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{sim_result.total_time:g}</div><div class="metric-lbl">Total Time</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{sim_result.throughput:.3f}</div><div class="metric-lbl">Throughput (p/t)</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # Gantt Chart Section
    st.markdown("### 📈 Gantt Chart Timeline")
    fig_gantt = plot_gantt_chart(sim_result)
    st.pyplot(fig_gantt, use_container_width=True)

    # Process Metrics Table
    st.markdown("### 📋 Process Execution Details")
    df_metrics = pd.DataFrame(sim_result.get_process_dataframe_dict())
    st.dataframe(df_metrics, use_container_width=True)

    # Export Buttons
    st.markdown("### 💾 Export Results")
    exp_col1, exp_col2, _ = st.columns([1, 1, 2])
    with exp_col1:
        csv_data = export_results_to_csv(sim_result)
        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name=f"{selected_algo.replace(' ', '_').lower()}_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    with exp_col2:
        pdf_bytes = export_results_to_pdf(sim_result, fig_gantt=fig_gantt)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"{selected_algo.replace(' ', '_').lower()}_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ==============================================================================
# MODE 2: COMPARE ALL ALGORITHMS (BENCHMARK)
# ==============================================================================
else:
    st.markdown("### 🏁 Multi-Algorithm Benchmark Comparison")
    st.markdown("Simulating all algorithms simultaneously on the current process dataset:")

    all_results = []
    for algo_name, sched in schedulers.items():
        res = sched.run(active_processes, quantum=time_quantum, lower_is_higher=lower_is_higher)
        all_results.append(res)

    best_algo = min(all_results, key=lambda r: r.avg_waiting_time)
    st.success(
        f"🏆 **Best Performing Algorithm by Average Waiting Time:** **{best_algo.algorithm_name}** "
        f"with Avg Waiting Time = **{best_algo.avg_waiting_time:.2f} units** "
        f"and Avg Turnaround Time = **{best_algo.avg_turnaround_time:.2f} units**."
    )

    # Comparison Table
    summary_data = [r.get_summary_dict() for r in all_results]
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True)

    # Comparative Bar Chart
    st.markdown("### 📊 Comparative Performance Bar Chart")
    fig_comp = plot_comparison_chart(all_results)
    st.pyplot(fig_comp, use_container_width=True)

    # Individual Gantt Charts Carousel/Accordion
    st.markdown("### 🔍 Individual Gantt Charts for Each Algorithm")
    for res in all_results:
        with st.expander(f"Gantt Chart: {res.algorithm_name} (Avg WT: {res.avg_waiting_time:.2f}, TAT: {res.avg_turnaround_time:.2f})"):
            fig = plot_gantt_chart(res)
            st.pyplot(fig, use_container_width=True)

    # Export Section
    st.markdown("### 💾 Export Benchmark Results")
    exp_c1, exp_c2, _ = st.columns([1, 1, 2])
    with exp_c1:
        comp_csv = export_comparison_to_csv(all_results)
        st.download_button(
            label="📥 Download Comparison CSV",
            data=comp_csv,
            file_name="cpu_scheduling_comparison.csv",
            mime="text/csv",
            use_container_width=True
        )
    with exp_c2:
        best_gantt = plot_gantt_chart(best_algo)
        comp_pdf = export_results_to_pdf(best_algo, fig_gantt=best_gantt, comparison_results=all_results)
        st.download_button(
            label="📄 Download Full PDF Benchmark Report",
            data=comp_pdf,
            file_name="cpu_scheduling_benchmark_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ==============================================================================
# EDUCATIONAL ACCORDION
# ==============================================================================
st.markdown("---")
with st.expander("📚 Operating System Scheduling Concepts & Formulas Guide"):
    st.markdown("""
    #### Key Scheduling Metrics & Formulas:
    - **Turnaround Time (TAT)**: Total time from process arrival to its completion.  
      $$\\text{Turnaround Time} = \\text{Completion Time} - \\text{Arrival Time}$$
    - **Waiting Time (WT)**: Total time spent by a process waiting in the ready queue.  
      $$\\text{Waiting Time} = \\text{Turnaround Time} - \\text{Burst Time}$$
    - **Response Time (RT)**: Time from process arrival until its very first CPU execution.  
      $$\\text{Response Time} = \\text{First CPU Start Time} - \\text{Arrival Time}$$
    - **CPU Utilization**: Fraction of total elapsed time the CPU was actively executing processes.  
      $$\\text{CPU Utilization} = \\frac{\\text{Total Time} - \\text{Idle Time}}{\\text{Total Time}} \\times 100\\%$$
    - **Throughput**: Number of completed processes per unit time.  
      $$\\text{Throughput} = \\frac{\\text{Completed Processes}}{\\text{Total Time}}$$

    #### Algorithm Overview:
    1. **FCFS (First-Come, First-Served)**: Non-preemptive. Simple FIFO queue. Vulnerable to the *Convoy Effect* when a long CPU-bound process blocks subsequent short I/O-bound jobs.
    2. **SJF (Shortest Job First)**: Non-preemptive. Selects the arrived job with smallest total burst time. Minimizes average waiting time among non-preemptive algorithms, but prone to starvation for long processes.
    3. **SRTF (Shortest Remaining Time First)**: Preemptive variant of SJF. Preempts running job whenever a newly arrived process has a strictly shorter remaining burst. Theoretically optimal for minimizing average waiting time.
    4. **Priority Scheduling**: Allocates CPU based on assigned priority weights. Available in both non-preemptive and preemptive forms. Can cause starvation of low-priority jobs (mitigated in production OSs via aging).
    5. **Round Robin (RR)**: Preemptive time-sharing scheduler. Cycles through processes using a fixed *time quantum*. Excellent response time for interactive environments; quantum selection balances responsiveness against context switching overhead.
    """)

