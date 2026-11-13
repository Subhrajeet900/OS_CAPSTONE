@echo off
REM ==============================================================================
REM Benchmark All CPU Scheduling Algorithms (Windows Batch)
REM ==============================================================================
set INPUT_FILE=%~1
if "%INPUT_FILE%"=="" set INPUT_FILE=%~dp0..\inputs\sample_processes.csv

echo ==========================================================
echo  Benchmarking All CPU Scheduling Algorithms
echo  Input File : %INPUT_FILE%
echo ==========================================================
python "%~dp0..\cli.py" --file "%INPUT_FILE%" --algo all --quantum 2.0 --export-csv "%~dp0..\benchmark_comparison.csv" --export-pdf "%~dp0..\benchmark_report.pdf"
pause

