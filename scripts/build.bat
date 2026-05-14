@echo off
echo Installing build dependencies...
pip install -q pyinstaller -r requirements.txt
echo Building executable...
pyinstaller --onedir --noconsole --name ArtifactLens ^
    --hidden-import=artifactlens ^
    --hidden-import=artifactlens.app ^
    --hidden-import=artifactlens.api ^
    --hidden-import=artifactlens.config ^
    --hidden-import=artifactlens.theme ^
    --hidden-import=artifactlens.settings_dialog ^
    artifactlens\__main__.py
echo.
echo Done! Executable is at: dist\ArtifactLens\ArtifactLens.exe
pause
