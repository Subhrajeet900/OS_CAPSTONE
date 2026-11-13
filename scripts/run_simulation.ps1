<#
.SYNOPSIS
Smart CPU Scheduling Visualizer - PowerShell Simulation Runner
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$File,

    [string]$Algo = "all",
    [double]$Quantum = 2.0,
    [string]$PriorityOrder = "lower",
    [string]$ExportCsv = "",
    [string]$ExportPdf = "",
    [string]$Plot = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

$cmd = @("python", "$RootDir\cli.py", "--file", $File, "--algo", $Algo, "--quantum", $Quantum, "--priority-order", $PriorityOrder)

if ($ExportCsv) { $cmd += @("--export-csv", $ExportCsv) }
if ($ExportPdf) { $cmd += @("--export-pdf", $ExportPdf) }
if ($Plot) { $cmd += @("--plot", $Plot) }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Running CPU Scheduling Simulation" -ForegroundColor Cyan
Write-Host " Input File : $File"
Write-Host " Algorithm  : $Algo"
Write-Host " Quantum    : $Quantum"
Write-Host "==========================================================" -ForegroundColor Cyan

& $cmd[0] $cmd[1..($cmd.Length - 1)]

