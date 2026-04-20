"""Default Azure DevOps configuration."""

ORG = "dnceng"
PROJECT = "public"
API_VERSION = "7.1-preview.1"

# ── App defaults ──
DEFAULT_VERSION = "26.2.10196"
import os

DEFAULT_THREADS = os.cpu_count() or 8
MAX_THREADS = DEFAULT_THREADS
DEFAULT_PLATFORM = "Android"
PLATFORM_OPTIONS = ["No filter", "Android", "MacIOS"]
WINDOW_SIZE = "1200x720"
WINDOW_MIN_SIZE = (900, 500)
APP_VERSION = "0.1.2"


def build_base_url(org: str, project: str) -> str:
    return f"https://feeds.dev.azure.com/{org}/{project}/_apis/packaging"


def build_feed_url(org: str, project: str, feed: str) -> str:
    return f"https://dev.azure.com/{org}/{project}/_artifacts/feed/{feed}"


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
