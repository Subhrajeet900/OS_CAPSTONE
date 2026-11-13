#!/usr/bin/env bash
# ==============================================================================
# Smart CPU Scheduling Visualizer - Simulation Runner
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
    echo "Usage: $0 -f <input_csv_or_json> [-a <algorithm>] [-q <quantum>] [--export-csv <path>] [--export-pdf <path>] [--plot <path>]"
    echo ""
    echo "Options:"
    echo "  -f, --file FILE         Path to input process file (CSV or JSON) [Required]"
    echo "  -a, --algo ALGO         Algorithm: fcfs | sjf | srtf | priority | priority_p | rr | all (Default: all)"
    echo "  -q, --quantum INT       Round Robin time quantum (Default: 2.0)"
    echo "  --priority-order ORDER  Priority ordering: 'lower' (0 is highest) or 'higher' (Default: lower)"
    echo "  --export-csv PATH       Export metrics table to CSV file"
    echo "  --export-pdf PATH       Export report to PDF file"
    echo "  --plot PATH             Save Gantt chart to PNG image"
    echo "  -h, --help              Show this help message"
    exit 1
}

FILE=""
ALGO="all"
QUANTUM="2.0"
PRIORITY_ORDER="lower"
EXPORT_CSV=""
EXPORT_PDF=""
PLOT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--file)
            FILE="$2"
            shift 2
            ;;
        -a|--algo)
            ALGO="$2"
            shift 2
            ;;
        -q|--quantum)
            QUANTUM="$2"
            shift 2
            ;;
        --priority-order)
            PRIORITY_ORDER="$2"
            shift 2
            ;;
        --export-csv)
            EXPORT_CSV="$2"
            shift 2
            ;;
        --export-pdf)
            EXPORT_PDF="$2"
            shift 2
            ;;
        --plot)
            PLOT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

if [[ -z "$FILE" ]]; then
    echo "Error: Input file (-f / --file) is required."
    usage
fi

CMD_ARGS=("python" "${ROOT_DIR}/cli.py" "--file" "$FILE" "--algo" "$ALGO" "--quantum" "$QUANTUM" "--priority-order" "$PRIORITY_ORDER")

if [[ -n "$EXPORT_CSV" ]]; then
    CMD_ARGS+=("--export-csv" "$EXPORT_CSV")
fi
if [[ -n "$EXPORT_PDF" ]]; then
    CMD_ARGS+=("--export-pdf" "$EXPORT_PDF")
fi
if [[ -n "$PLOT" ]]; then
    CMD_ARGS+=("--plot" "$PLOT")
fi

echo "=========================================================="
echo " Running CPU Scheduling Simulation"
echo " Input File : $FILE"
echo " Algorithm  : $ALGO"
echo " Quantum    : $QUANTUM"
echo "=========================================================="

"${CMD_ARGS[@]}"

