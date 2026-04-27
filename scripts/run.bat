@echo off
echo Installing dependencies...
pip install -q -r requirements.txt
echo.
python -m search_artifact_app
if errorlevel 1 pause
