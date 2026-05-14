"""Default Azure DevOps configuration."""

import os
import sys
from pathlib import Path

API_VERSION = "7.1-preview.1"

# ── App defaults ──

DEFAULT_THREADS = os.cpu_count() or 8
MAX_THREADS = DEFAULT_THREADS
DEFAULT_PLATFORM = "Android"
PLATFORM_OPTIONS = ["No filter", "Android", "MacIOS"]
WINDOW_SIZE = "1200x720"
WINDOW_MIN_SIZE = (900, 500)


def _read_version() -> str:
    """Resolve the VERSION file across source and PyInstaller layouts."""
    candidates: list[Path] = []
    # Source layout: repo root (parent of the package directory).
    candidates.append(Path(__file__).resolve().parent.parent / "VERSION")
    # PyInstaller --onedir: bundled next to the executable.
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "VERSION")
        # PyInstaller --onefile: extracted to a temp dir exposed via _MEIPASS.
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "VERSION")
    for path in candidates:
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return "0.0.0"


APP_VERSION = _read_version()

# ── Update checker ──

GITHUB_REPO = "william051200/ArtifactLens"
INSTALL_SCRIPT_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/scripts/install.ps1"
)
UPDATE_CHECK_INTERVAL_SECONDS = 3600


def build_base_url(org: str, project: str) -> str:
    return f"https://feeds.dev.azure.com/{org}/{project}/_apis/packaging"


def build_feed_url(org: str, project: str, feed: str) -> str:
    return f"https://dev.azure.com/{org}/{project}/_artifacts/feed/{feed}"


def build_nuget_source_xml(feed: str, org: str, project: str) -> str:
    url = f"https://pkgs.dev.azure.com/{org}/{project}/_packaging/{feed}/nuget/v3/index.json"
    return f'<add key="{feed}" value="{url}" />'


def build_artifact_url(org: str, project: str, feed: str, proto: str, package: str, version: str) -> str:
    return f"https://dev.azure.com/{org}/{project}/_artifacts/feed/{feed}/{proto}/{package}/overview/{version}"


# Map protocol type strings to Azure DevOps URL path segments
PROTOCOL_TYPE_MAP = {
    "NuGet": "NuGet",
    "npm": "Npm",
    "Maven": "Maven",
    "PyPI": "PyPI",
    "UPack": "UPack",
    "Cargo": "Cargo",
}
