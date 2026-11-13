# Smart CPU Scheduling Visualizer

An operating system process scheduling simulator and visualizer built with **Python**, **Streamlit**, **Matplotlib**, and **Bash**. It demonstrates how an operating system decides which process gets CPU time, calculates execution and wait metrics, produces high-resolution Gantt charts, compares algorithmic performance side-by-side, and exports reports to CSV and PDF.

---

## Key Features

- **Process Input & Management**:
  - Add processes with Arrival Time ($AT$), Burst Time ($BT$), and Priority ($Priority$).
  - Preset textbook scenarios (Convoy Effect, SRTF vs SJF, Priority Scheduling, Round Robin slicing, Staggered CPU Idle gaps).
  - Dynamic in-browser interactive table editor (add, remove, or edit rows on the fly).
  - Bulk CSV/JSON file upload & automated random process generator.

- **Supported Scheduling Algorithms**:
  - **FCFS** (First-Come, First-Served)
  - **SJF** (Shortest Job First - Non-Preemptive)
  - **SRTF** (Shortest Remaining Time First - Preemptive SJF)
  - **Priority Scheduling (Non-Preemptive)** (Configurable: lower value = higher priority or vice-versa)
  - **Priority Scheduling (Preemptive)**
  - **Round Robin (RR)** with configurable time quantum and arrival queue management.

- **Metrics Calculation**:
  - **Completion Time ($CT$)**: Time when a process finishes execution.
  - **Turnaround Time ($TAT$)**: $TAT = CT - AT$
  - **Waiting Time ($WT$)**: $WT = TAT - BT$
  - **Response Time ($RT$)**: $RT = \text{First CPU Start Time} - AT$
  - **CPU Utilization**: $\frac{\text{Total Time} - \text{Idle Time}}{\text{Total Time}} \times 100\%$
  - **Throughput**: $\frac{\text{Processes Completed}}{\text{Total Time}}$
  - Average Turnaround Time, Average Waiting Time, and Average Response Time.

- **Visualizations**:
  - **Matplotlib Gantt Charts**: Color-coded process blocks, execution duration labels, transition timestamps, and hatched markers for CPU Idle periods.
  - **Comparative Bar Charts**: Side-by-side comparison of Average Waiting Time, Turnaround Time, and Response Time across all algorithms.

- **Export & Reports**:
  - **CSV Export**: Individual algorithm process metrics or multi-algorithm comparison tables.
  - **PDF Export**: Branded report containing summary cards, process metrics table, embedded Gantt chart timeline, and comparative benchmark analysis.

- **Bash & PowerShell Automation**:
  - Run headless simulations, batch benchmarks, and input generation from terminal/scripts.

---

## Project Architecture

```
OS_CAPSTONE/
├── app.py                     # Streamlit web user interface
├── cli.py                     # Command-line interface for headless execution & scripts
├── cpu_scheduler/             # Core scheduling engine
│   ├── __init__.py
│   ├── models.py              # Process, ExecutionBlock, SimulationResult dataclasses
│   ├── algorithms/            # Scheduling algorithm implementations
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract BaseScheduler & validation
│   │   ├── fcfs.py            # First-Come First-Served
│   │   ├── sjf.py             # SJF Non-Preemptive & SRTF Preemptive
│   │   ├── priority.py        # Priority Non-Preemptive & Preemptive
│   │   └── round_robin.py     # Round Robin with quantum & arrival queue logic
│   ├── metrics.py             # Metrics calculations (CT, TAT, WT, RT, utilization, throughput)
│   ├── visualizer.py          # Matplotlib Gantt chart & comparative chart plotting
│   ├── exporter.py            # CSV & PDF report generators (ReportLab & Matplotlib fallback)
│   └── presets.py             # Predefined textbook and benchmark scenarios
├── scripts/                   # Automation scripts (Bash and PowerShell)
│   ├── run_simulation.sh      # Run simulation on input file via Bash
│   ├── compare_all.sh         # Benchmark all algorithms & export reports via Bash
│   ├── manage_inputs.sh       # Validate, inspect, or generate CSV inputs via Bash
│   ├── launch_app.sh          # Launch Streamlit server via Bash
│   ├── run_simulation.ps1     # Native PowerShell simulation runner
│   ├── compare_all.ps1        # Native PowerShell benchmark runner
│   ├── manage_inputs.ps1      # Native PowerShell input manager
│   └── launch_app.ps1         # Native PowerShell Streamlit launcher
├── inputs/                    # Sample and benchmark CSV datasets
│   ├── sample_processes.csv
│   ├── convoy_effect.csv
│   ├── priority_sample.csv
│   └── staggered_arrivals.csv
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_algorithms.py     # Pytest unit tests for all algorithms & edge cases
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

##  Quickstart

### 1. Installation

Ensure Python 3.10+ is installed, then install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit Web Visualizer

**Option A (Direct command - Recommended for any terminal):**
```powershell
python -m streamlit run app.py
```

**Option B (Windows Batch / Quick Double-click):**
```cmd
.\run.bat
```
or:
```cmd
.\scripts\launch_app.bat
```

**Option C (PowerShell with ExecutionPolicy Bypass):**
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\launch_app.ps1
```

**Option D (Bash / Git Bash / Linux):**
```bash
./scripts/launch_app.sh
```

Then open your browser at `http://localhost:8501`.

---

##  CLI & Script Usage

### Run All Algorithms on an Input File
```bash
# Bash
./scripts/compare_all.sh inputs/sample_processes.csv

# PowerShell
.\scripts\compare_all.ps1 -InputFile inputs\sample_processes.csv
```

### Run a Single Algorithm (e.g. Round Robin with Quantum = 3)
```bash
# Bash
./scripts/run_simulation.sh -f inputs/sample_processes.csv -a rr -q 3 --plot gantt.png --export-csv results.csv

# PowerShell
.\scripts\run_simulation.ps1 -File inputs\sample_processes.csv -Algo rr -Quantum 3 -Plot gantt.png -ExportCsv results.csv
```

### Manage Input Files
```bash
# List available datasets
./scripts/manage_inputs.sh --list

# Validate a dataset
./scripts/manage_inputs.sh --validate inputs/sample_processes.csv

# Generate 6 random processes into a CSV
./scripts/manage_inputs.sh --generate 6 inputs/my_test.csv
```

---

## Running Unit Tests

Run the complete test suite with pytest:

```bash
python -m pytest -v
```

All algorithms, edge cases (idle gaps, preemption order, quantum context switching, and PDF/CSV export) are covered.

---

## Theoretical Background & Formulas

| Metric | Formula | Description |
| :--- | :--- | :--- |
| **Completion Time ($CT$)** | $\text{Timestamp of last CPU burst}$ | Time when process finishes |
| **Turnaround Time ($TAT$)** | $TAT = CT - AT$ | Total time from arrival to completion |
| **Waiting Time ($WT$)** | $WT = TAT - BT$ | Total time process spent in ready queue |
| **Response Time ($RT$)** | $RT = \text{First CPU start} - AT$ | Latency until process gets first CPU cycle |
| **CPU Utilization** | $\frac{\text{Total Busy Time}}{\text{Total Time}} \times 100\%$ | Efficiency of CPU usage |
| **Throughput** | $\frac{N}{\text{Total Time}}$ | Processes executed per unit time |


## do on ething to start - 
python -m streamlit run app.py