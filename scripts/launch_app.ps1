<#
.SYNOPSIS
Smart CPU Scheduling Visualizer - PowerShell Streamlit App Launcher
#>

param (
    [int]$Port = 8501
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting Smart CPU Scheduling Visualizer UI" -ForegroundColor Cyan
Write-Host " Port: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

python -m streamlit run "$RootDir\app.py" --server.port $Port --server.headless true

