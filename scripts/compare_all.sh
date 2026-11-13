#!/usr/bin/env bash
# ==============================================================================
# Compare All CPU Scheduling Algorithms and Generate Full Reports
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

INPUT_FILE="${1:-"${ROOT_DIR}/inputs/sample_processes.csv"}"
OUTPUT_CSV="${2:-"${ROOT_DIR}/benchmark_comparison.csv"}"
OUTPUT_PDF="${3:-"${ROOT_DIR}/benchmark_report.pdf"}"

echo "=========================================================="
echo " Benchmarking All CPU Scheduling Algorithms"
echo " Input File : $INPUT_FILE"
echo " Output CSV : $OUTPUT_CSV"
echo " Output PDF : $OUTPUT_PDF"
echo "=========================================================="

python "${ROOT_DIR}/cli.py" \
    --file "$INPUT_FILE" \
    --algo all \
    --quantum 2.0 \
    --export-csv "$OUTPUT_CSV" \
    --export-pdf "$OUTPUT_PDF"

echo "Benchmark completed successfully!"

