# ArtifactLens — How It Works

**ArtifactLens** searches across Azure DevOps Artifacts feeds to find packages by version — something the Azure DevOps UI doesn't support natively.

## How the Search Works

1. **Prefetch feeds** — When the app opens, it fetches the full list of feeds in the background and caches them so every search after that is instant.

2. **Filter** — When you hit Search, the cached feeds are narrowed down by your filters (feed name, platform, exclude build feeds).

3. **Parallel scan** — The remaining feeds are scanned in parallel using one thread per CPU core. Each thread pages through a feed's packages looking for your version string.

4. **Live results** — Matches appear in the table as they're found — no waiting for all feeds to finish.

## Project Structure

| File | What it does |
|---|---|
| `app.py` | UI and search orchestration |
| `api.py` | Calls the Azure DevOps REST API |
| `config.py` | App defaults and URL helpers |
| `theme.py` | Colors and fonts |

## Notable Details

- **Thread safe** — UI values are captured into a snapshot before threads start; background threads never touch the UI directly.
- **Stop is instant** — The cancel flag is checked at every stage, so the app never hangs.
- **Packaged as exe** — Built with PyInstaller `--onedir` to work on enterprise machines with AppLocker policies.
