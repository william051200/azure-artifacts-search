# ArtifactLens

Search across Azure DevOps Artifacts feeds for packages by version.

## Installation

### Option A — One-line PowerShell install (recommended)

Open **PowerShell** and paste:

```powershell
irm https://raw.githubusercontent.com/william051200/ArtifactLens/main/scripts/install.ps1 | iex
```

This downloads the latest release, extracts it to
`%LOCALAPPDATA%\Programs\ArtifactLens`, and creates Start Menu + Desktop
shortcuts. No admin rights required. Re-run the same command any time to
upgrade.

### Option B — Download the pre-built executable

1. Go to the [latest release](https://github.com/william051200/ArtifactLens/releases/latest)
2. Under **Assets**, download **`ArtifactLens.zip`**
3. Right-click the downloaded zip → **Properties** → check **Unblock** (if shown) → **OK**
4. Extract the zip to any folder (e.g. `C:\Tools\ArtifactLens\`)
5. Run **`ArtifactLens.exe`** from the extracted folder — no Python or other dependencies required

> 💡 **Tip:** Pin `ArtifactLens.exe` to your Start menu or taskbar for quick access.

### Option C — Run from source (requires [Python](https://www.python.org/downloads/))

```bash
git clone https://github.com/william051200/ArtifactLens.git
cd ArtifactLens
```

Double-click **`scripts/run.bat`** — it installs dependencies and launches the app automatically.

### Option D — Build the executable yourself

1. Double-click **`scripts/build.bat`** (requires Python for the one-time build)
2. Find the output at `dist\ArtifactLens\ArtifactLens.exe`
3. Share the entire `dist\ArtifactLens\` folder — no Python required on target machines

## First-Time Setup

1. Launch the app and click **⚙ Settings**
2. Fill in your **Organization** and **Project** name from Azure DevOps
3. For private feeds, enter your **Personal Access Token (PAT)**
4. Click **Save** — settings are stored locally in a `.env` file

## Updates

ArtifactLens checks GitHub for new releases on startup and once per hour
afterwards. When a newer version is available, the version tag and an
**Update** button appear in the top navigation bar:

- **Click the version tag** to open the release notes on GitHub.
- **Click Update** to download and install the latest version automatically;
  the app closes, the installer overwrites it in place, and ArtifactLens
  re-launches when it's done.

## Usage

1. Enter a version (e.g. `1.0.0`)
2. Optionally set a **feed filter**, **platform** (Android / MacIOS), or toggle search options
3. Click **Search**
4. Double-click a result to open the package in Azure DevOps

## Acknowledgements

UI design inspired by [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md).
