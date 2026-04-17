# Changelog

## v1.0.0

Initial release of **ArtifactLens**.

### Features

- **Cross-feed version search** — Search for packages by version string across all Azure DevOps Artifacts feeds in a project.
- **Parallel search** — Configurable thread pool (1–32 workers) for high-throughput feed scanning.
- **Platform filter** — Quick-select dropdown to narrow results by platform (Android / MacIOS / No filter).
- **Feed name filter** — Free-text substring filter to target specific feeds.
- **Contains match** — Toggle between exact version match and substring match.
- **First match per feed** — Early-termination optimization that skips remaining packages in a feed after the first hit, significantly improving speed.
- **Build-feed toggle** — Option to include or exclude ephemeral per-build feeds (version-prefixed, `darc-`, GUID-prefixed).
- **Real-time results** — Matches stream into the results table as each feed completes.
- **Live log panel** — Timestamped activity log with color-coded entries (info, success, warning, error).
- **Deep linking** — Double-click any result to open the package directly in Azure DevOps.
- **Settings dialog** — Configure organization, project, and Personal Access Token (PAT) from within the app; settings persist to a `.env` file.
- **Standalone distribution** — Build a portable `.exe` via PyInstaller; no Python installation required for end users.
