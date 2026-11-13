@echo off
REM ==============================================================================
REM Launch Streamlit CPU Scheduling Visualizer Web Interface
REM ==============================================================================
echo ==========================================================
echo  Starting Smart CPU Scheduling Visualizer UI
echo  URL: http://localhost:8501
echo ==========================================================
python -m streamlit run "%~dp0..\app.py" --server.port 8501
pause

