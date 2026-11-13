#!/usr/bin/env bash
# ==============================================================================
# Manage Input Files: Validate, Generate, and Inspect Process Sets
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
INPUTS_DIR="${ROOT_DIR}/inputs"

usage() {
    echo "Usage: $0 [command] [arguments]"
    echo ""
    echo "Commands:"
    echo "  --list                     List all sample input files"
    echo "  --view <file>              Display contents of an input file"
    echo "  --validate <file>          Validate formatting and values in a process file"
    echo "  --generate <n> <file>      Generate a new CSV with <n> random processes"
    echo "  -h, --help                 Display this help message"
    exit 1
}

CMD="${1:-"--list"}"

case "$CMD" in
    --list)
        echo "Available process input files in ${INPUTS_DIR}:"
        ls -1 "${INPUTS_DIR}"
        ;;
    --view)
        TARGET="${2:-}"
        if [[ -z "$TARGET" ]]; then
            echo "Error: Please specify file to view."
            exit 1
        fi
        if [[ ! -f "$TARGET" && -f "${INPUTS_DIR}/${TARGET}" ]]; then
            TARGET="${INPUTS_DIR}/${TARGET}"
        fi
        echo "Contents of $TARGET:"
        cat "$TARGET"
        ;;
    --validate)
        TARGET="${2:-}"
        if [[ -z "$TARGET" ]]; then
            echo "Error: Please specify file to validate."
            exit 1
        fi
        if [[ ! -f "$TARGET" && -f "${INPUTS_DIR}/${TARGET}" ]]; then
            TARGET="${INPUTS_DIR}/${TARGET}"
        fi
        python -c "
import sys, csv
from cpu_scheduler.models import Process

filepath = sys.argv[1]
try:
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        for idx, row in enumerate(reader, start=1):
            cleaned = {k.strip().lower().replace(' ', '_'): v.strip() for k, v in row.items() if k}
            pid = cleaned.get('pid') or cleaned.get('process_id') or f'P{idx}'
            at = float(cleaned.get('arrival_time') or cleaned.get('arrival') or 0)
            bt = float(cleaned.get('burst_time') or cleaned.get('burst') or 1)
            pr = int(float(cleaned.get('priority') or 0))
            if at < 0:
                raise ValueError(f'Row {idx} ({pid}): arrival_time must be >= 0')
            if bt <= 0:
                raise ValueError(f'Row {idx} ({pid}): burst_time must be > 0')
            count += 1
    print(f'Validation SUCCESS: {count} valid processes found in {filepath}')
except Exception as e:
    print(f'Validation FAILED: {e}')
    sys.exit(1)
" "$TARGET"
        ;;
    --generate)
        NUM_PROCS="${2:-5}"
        OUT_FILE="${3:-"${INPUTS_DIR}/generated_processes.csv"}"
        python -c "
import sys, random
n = int(sys.argv[1])
out = sys.argv[2]
with open(out, 'w', encoding='utf-8') as f:
    f.write('pid,arrival_time,burst_time,priority\n')
    current_arr = 0
    for i in range(1, n + 1):
        # Stagger arrivals realistically
        current_arr += random.choice([0, 1, 2, 3])
        bt = random.randint(1, 12)
        pri = random.randint(1, 5)
        f.write(f'P{i},{current_arr},{bt},{pri}\n')
print(f'Successfully generated {n} processes into {out}')
" "$NUM_PROCS" "$OUT_FILE"
        ;;
    -h|--help)
        usage
        ;;
    *)
        echo "Unknown command: $CMD"
        usage
        ;;
esac

