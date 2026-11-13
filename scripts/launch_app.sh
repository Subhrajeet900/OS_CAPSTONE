#!/usr/bin/env bash
# ==============================================================================
# Launch Streamlit CPU Scheduling Visualizer Web Interface
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PORT="${1:-8501}"

echo "=========================================================="
echo " Starting Smart CPU Scheduling Visualizer UI"
echo " Port: http://localhost:${PORT}"
echo "=========================================================="

streamlit run "${ROOT_DIR}/app.py" --server.port "${PORT}" --server.headless true

