# Azure Artifacts Search

A desktop app to search across Azure DevOps Artifacts feeds for packages by version. Built with Python and Tkinter.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

## Features

- **Multi-threaded search** — searches feeds in parallel (configurable 1–32 threads)
- **Paginated feed retrieval** — fetches all feeds, not just the first page
- **Contains matching** — find versions like `13.2.0-preview.1.26173.5` by searching `13.2.0`
- **Feed filtering** — filter feeds by name substring
- **Per-build feed toggle** — include or exclude auto-generated CI build feeds
- **Live results** — results appear in the table as each feed completes
- **Log panel** — real-time, color-coded log of what's happening
- **Double-click to open** — double-click a result to open it in Azure DevOps
- **Configurable** — change org, project, API version, and PAT from the Settings popup

## Prerequisites

- Python 3.10 or later
- Tkinter (included with most Python installations)

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/william051200/azure-artifacts-search.git
   cd azure-artifacts-search
   ```

2. **Create a virtual environment** (optional but recommended)

   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional — for private feeds)

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your Azure DevOps PAT and org/project. You can also set these from the Settings popup in the app.

## Usage

### Desktop App (GUI)

```bash
# Run as a package
python -m search_artifact_app

# Or use the launcher script
python search_artifact_app.py
```

1. Enter a version string (e.g. `13.2.0`)
2. Optionally enter a feed name filter
3. Check **Contains match** to find versions that contain your search text
4. Check **Include per-build feeds** to search auto-generated CI feeds
5. Adjust **Threads** for faster/slower searches
6. Click **Search** or press Enter
7. **Double-click** any result row to open it in Azure DevOps

#### Settings

Click **⚙ Settings** in the top-right to configure:

| Field | Description |
|-------|-------------|
| Organization | Azure DevOps org (default: `dnceng`) |
| Project | Azure DevOps project (default: `public`) |
| API Version | REST API version (default: `7.1-preview.1`) |
| Personal Access Token | PAT for private feeds (leave empty for public feeds) |

### CLI

```bash
# Search for a version
python search_artifact.py 36.1.35

# Search a specific feed
python search_artifact.py 36.1.35 --feed dotnet-eng

# Filter feeds by name
python search_artifact.py 36.1.35 --feed-filter dotnet

# List all feeds
python search_artifact.py --list-feeds

# Include per-build feeds
python search_artifact.py 36.1.35 --include-build-feeds
```

## Project Structure

```
├── search_artifact_app/        # GUI app package
│   ├── __init__.py
│   ├── __main__.py             # Entry point
│   ├── app.py                  # Main window
│   ├── api.py                  # Azure DevOps API client
│   ├── config.py               # Default configuration
│   ├── theme.py                # Colors and fonts
│   └── settings_dialog.py      # Settings popup
├── search_artifact.py          # CLI tool (standalone)
├── search_artifact_app.py      # GUI launcher (backward compat)
├── requirements.txt
├── .env.example                # Environment template
└── .gitignore
```
