@echo off
echo Installing build dependencies...
pip install -q pyinstaller
echo Building executable...
pyinstaller --onefile --noconsole --name AzureArtifactsSearch search_artifact_app.py
echo.
echo Done! Executable is at: dist\AzureArtifactsSearch.exe
pause
