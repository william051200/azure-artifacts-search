# Azure Artifacts Search

Search across Azure DevOps Artifacts feeds for packages by version.

## Setup & Run

**Option 1 — Quick start (requires Python):**
Double-click **`run.bat`** — it installs dependencies and launches the app automatically.

**Option 2 — Standalone .exe (no Python needed):**
Run **`build.bat`** once to create `dist\AzureArtifactsSearch.exe`, then share/run that file anywhere.

For private feeds, set your PAT in **⚙ Settings** inside the app.

1. Enter a version (e.g. `13.2.0`)
2. Click **Search**
3. Double-click a result to open it in Azure DevOps

Use **⚙ Settings** to change org, project, or PAT.
