<#
.SYNOPSIS
Smart CPU Scheduling Visualizer - PowerShell Input File Manager
#>

param (
    [switch]$List,
    [string]$View = "",
    [string]$Validate = "",
    [int]$Generate = 0,
    [string]$OutputFile = "inputs\generated_processes.csv"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$InputsDir = Join-Path $RootDir "inputs"

if ($List) {
    Write-Host "Available process input files in $InputsDir`:" -ForegroundColor Cyan
    Get-ChildItem -Path $InputsDir -Filter *.csv | ForEach-Object { Write-Host " - $($_.Name)" }
    return
}

if ($View) {
    $target = if (Test-Path $View) { $View } else { Join-Path $InputsDir $View }
    Get-Content $target
    return
}

if ($Validate) {
    $target = if (Test-Path $Validate) { $Validate } else { Join-Path $InputsDir $Validate }
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
" "$target"
    return
}

if ($Generate -gt 0) {
    python -c "
import sys, random
n = int(sys.argv[1])
out = sys.argv[2]
with open(out, 'w', encoding='utf-8') as f:
    f.write('pid,arrival_time,burst_time,priority\n')
    current_arr = 0
    for i in range(1, n + 1):
        current_arr += random.choice([0, 1, 2, 3])
        bt = random.randint(1, 12)
        pri = random.randint(1, 5)
        f.write(f'P{i},{current_arr},{bt},{pri}\n')
print(f'Successfully generated {n} processes into {out}')
" "$Generate" "$OutputFile"
    return
}

Write-Host "Usage: .\scripts\manage_inputs.ps1 [-List] [-View <file>] [-Validate <file>] [-Generate <n> -OutputFile <path>]"

