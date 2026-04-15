# Azure Artifacts Search

Search across Azure DevOps Artifacts feeds for packages by version.

## Setup

```bash
git clone https://github.com/william051200/azure-artifacts-search.git
cd azure-artifacts-search
pip install -r requirements.txt
```

For private feeds, copy `.env.example` to `.env` and add your PAT — or set it in **⚙ Settings** inside the app.

## Run

```bash
python -m search_artifact_app
```

1. Enter a version (e.g. `13.2.0`)
2. Click **Search**
3. Double-click a result to open it in Azure DevOps

Use **⚙ Settings** to change org, project, or PAT.
