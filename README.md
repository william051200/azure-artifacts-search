# ArtifactLens

Search across Azure DevOps Artifacts feeds for packages by version.

## Installation

### Option A — Download the pre-built executable (recommended)

1. Go to the [latest release](https://github.com/william051200/ArtifactLens/releases/latest) (currently [v1.0.0](https://github.com/william051200/ArtifactLens/releases/tag/v1.0.0))
2. Under **Assets**, download **`ArtifactLens.zip`**
3. Right-click the downloaded zip → **Properties** → check **Unblock** (if shown) → **OK**
4. Extract the zip to any folder (e.g. `C:\Tools\ArtifactLens\`)
5. Run **`ArtifactLens.exe`** from the extracted folder — no Python or other dependencies required

> 💡 **Tip:** Pin `ArtifactLens.exe` to your Start menu or taskbar for quick access.

### Option B — Run from source (requires [Python](https://www.python.org/downloads/))

```bash
git clone https://github.com/william051200/ArtifactLens.git
cd ArtifactLens
```

Double-click **`scripts/run.bat`** — it installs dependencies and launches the app automatically.

### Option C — Build the executable yourself

1. Double-click **`scripts/build.bat`** (requires Python for the one-time build)
2. Find the output at `dist\ArtifactLens\ArtifactLens.exe`
3. Share the entire `dist\ArtifactLens\` folder — no Python required on target machines

## First-Time Setup

1. Launch the app and click **⚙ Settings**
2. Fill in your **Organization** and **Project** name from Azure DevOps
3. For private feeds, enter your **Personal Access Token (PAT)**
4. Click **Save** — settings are stored locally in a `.env` file

## Usage

1. Enter a version (e.g. `1.0.0`)
2. Optionally set a **feed filter**, **platform** (Android / MacIOS), or toggle search options
3. Click **Search**
4. Double-click a result to open the package in Azure DevOps

## Acknowledgements

UI design inspired by [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md).
