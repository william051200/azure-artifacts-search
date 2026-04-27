@echo off
echo Installing build dependencies...
pip install -q pyinstaller -r requirements.txt
echo Building executable...
pyinstaller --onedir --noconsole --name ArtifactLens ^
    --hidden-import=search_artifact_app ^
    --hidden-import=search_artifact_app.app ^
    --hidden-import=search_artifact_app.api ^
    --hidden-import=search_artifact_app.config ^
    --hidden-import=search_artifact_app.theme ^
    --hidden-import=search_artifact_app.settings_dialog ^
    search_artifact_app\__main__.py
echo.
echo Done! Executable is at: dist\ArtifactLens\ArtifactLens.exe
pause
