# ArtifactLens

Search across Azure DevOps Artifacts feeds for packages by version.

## Installation

### Option A — Download the pre-built executable (recommended)

1. Get the latest `ArtifactLens` folder from the `dist/` directory or your team's shared location
2. Run `ArtifactLens.exe` — no Python or other dependencies required

### Option B — Run from source (requires [Python](https://www.python.org/downloads/))

```bash
git clone https://github.com/william051200/azure-artifacts-search.git
cd azure-artifacts-search
```

Double-click **`scripts/run.bat`** — it installs dependencies and launches the app automatically.

### Option C — Build the executable yourself

1. Double-click **`scripts/build.bat`** (requires Python for the one-time build)
2. Find the output at `dist\ArtifactLens\ArtifactLens.exe`
3. Share the entire `dist\ArtifactLens\` folder — no Python required on target machines

## Usage

1. Enter a version (e.g. `1.0.0`)
2. Optionally set a **feed filter**, **platform** (Android / MacIOS), or toggle search options
3. Click **Search**
4. Double-click a result to open the package in Azure DevOps

For private feeds, set your PAT in **⚙ Settings** inside the app.
