# ArtifactLens

Search across Azure DevOps Artifacts feeds for packages by version.

## Getting Started

### 1. Download the project

```bash
git clone https://github.com/william051200/azure-artifacts-search.git
cd azure-artifacts-search
```

### 2. Run the app

**Option A — Quick start (requires [Python](https://www.python.org/downloads/)):**

Double-click **`run.bat`** — it installs dependencies and launches the app automatically.

**Option B — Build a standalone .exe (no Python needed after build):**

1. Double-click **`build.bat`** (requires Python for the one-time build)
2. Find the executable at `dist\ArtifactLens.exe`
3. Share or run that `.exe` anywhere — no Python required

## Usage

1. Enter a version (e.g. `13.2.0`)
2. Click **Search**
3. Double-click a result to open it in Azure DevOps

For private feeds, set your PAT in **⚙ Settings** inside the app.
