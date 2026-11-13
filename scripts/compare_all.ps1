<#
.SYNOPSIS
Smart CPU Scheduling Visualizer - PowerShell Benchmark Comparison Runner
#>

param (
    [string]$InputFile = "inputs\sample_processes.csv",
    [string]$OutputCsv = "benchmark_comparison.csv",
    [string]$OutputPdf = "benchmark_report.pdf"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Benchmarking All CPU Scheduling Algorithms" -ForegroundColor Cyan
Write-Host " Input File : $InputFile"
Write-Host " Output CSV : $OutputCsv"
Write-Host " Output PDF : $OutputPdf"
Write-Host "==========================================================" -ForegroundColor Cyan

python "$RootDir\cli.py" --file "$InputFile" --algo all --quantum 2.0 --export-csv "$OutputCsv" --export-pdf "$OutputPdf"
Write-Host "Benchmark completed successfully!" -ForegroundColor Green

