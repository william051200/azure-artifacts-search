# ArtifactLens — Release Notes (v0.1.0 → v0.1.3)

**ArtifactLens** is a desktop tool for searching across Azure DevOps Artifacts feeds by package version. These release notes cover everything since the initial release.

---

## What's New

### 🔗 Copy NuGet Source (v0.1.3)

Quickly grab the NuGet package source for any feed — right-click a result row and select **Copy NuGet Source** to copy an XML snippet like:

```xml
<add key="darc-pub-dotnet-macios-b364fe57"
     value="https://pkgs.dev.azure.com/dnceng/public/_packaging/darc-pub-dotnet-macios-b364fe57/nuget/v3/index.json" />
```

Paste it directly into your `nuget.config` — no need to look up feed URLs manually.

### 🖱️ Context Menu & Navigation (v0.1.2)

- **Right-click context menu** on any result row with options: Go to Feed, Go to Artifact, and Copy NuGet Source.
- **Double-click opens feed** — double-clicking now opens the feed page (previously opened the artifact page).
- **Deduplicate feeds** — new checkbox (on by default) to filter out duplicate feeds that appear in both org and project scope.

### ⚡ Performance Improvements (v0.1.1 – v0.1.2)

- **Feed list caching** — feeds are prefetched at launch and reused across searches.
- **Auto-detect thread count** — defaults to the number of CPU cores for maximum parallel throughput.
- **Early break on version match** — stops checking remaining versions of a package once a match is found.

### 🎨 UX Polish (v0.1.1)

- **Redesigned footer** with a 💡 tip and version badge.
- **Window auto-centering** — opens centered on screen.
- **Stop button** — clearer "Stop" label replaces "Cancel".

### 🐛 Bug Fixes (v0.1.1)

- **Instant stop** — clicking Stop during prefetch no longer blocks; exits within 200 ms.
- **Search-during-prefetch safety** — searching before prefetch finishes now waits gracefully.
- **Footer visibility** — footer is always visible regardless of window size.

---

## Core Features (since v0.1.0)

| Feature | Description |
|---|---|
| Cross-feed version search | Search by version across all feeds in a project |
| Parallel search | Configurable thread pool (1–32 workers) |
| Platform filter | Narrow results by Android / MacIOS |
| Feed name filter | Free-text substring filter |
| Contains match | Exact or substring version matching |
| First match per feed | Early termination for faster searches |
| Build-feed toggle | Include/exclude ephemeral per-build feeds |
| Real-time results | Matches stream in as each feed completes |
| Live log panel | Timestamped, color-coded activity log |
| Deep linking | Open feeds and artifacts directly in Azure DevOps |
| Settings dialog | Configure org, project, and PAT from within the app |
| Standalone `.exe` | Portable distribution via PyInstaller |

---

## Getting Started

Download `ArtifactLens.exe` from the `dist/` folder, or run from source with `run.bat`. See [README.md](README.md) for full setup instructions.
