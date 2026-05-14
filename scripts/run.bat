@echo off
echo Installing dependencies...
pip install -q -r requirements.txt
echo.
python -m artifactlens
if errorlevel 1 pause
