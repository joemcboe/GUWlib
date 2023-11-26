@echo off
cd /d %~dp0

set script=GUI_export_history.py

if exist %script% (
    echo Starting %script%...
    python %script%
) else (
    echo Error: %script% not found.
    pause
)