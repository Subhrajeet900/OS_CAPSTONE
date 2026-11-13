@echo off
REM Quick launcher for Smart CPU Scheduling Visualizer
python -m streamlit run "%~dp0app.py" --server.port 8501
pause

