# Changelog

## v0.1.2

### UX Improvements

- **Right-click context menu** — Right-click any result row to choose between "Go to Feed" and "Go to Artifact" for flexible navigation.
- **Default double-click opens feed** — Double-clicking a result now opens the feed page instead of the artifact page.
- **Updated footer tip** — Footer tip updated to reflect the new double-click and right-click interactions.

---

## v0.1.1

### Performance

- **Feed list caching** — Feed list is prefetched in the background when the app launches; subsequent searches reuse the cache instead of re-fetching every time.
- **Auto-detect max threads** — Thread count now defaults to the number of CPU cores available on the machine, maximizing parallel throughput out of the box.

### UX Improvements

- **Redesigned footer** — New warm-themed footer bar with a 💡 tip on the left and version badge on the right, separated by a visual divider.
- **Window auto-centering** — App window now opens centered on screen so the footer is never hidden behind the taskbar.
- **Stop button** — "Cancel" renamed to "Stop" across the UI and all status/log messages for clarity.

### Bug Fixes

- **Stop is now instant** — Clicking Stop during a prefetch wait no longer blocks; the app polls every 200 ms and exits immediately.
- **Search-during-prefetch safety** — Clicking Search before prefetch completes now waits gracefully instead of triggering a duplicate fetch.
- **Footer visibility** — Footer now packs before the main paned window so it is always visible regardless of window size.

---

## v0.1.0

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
