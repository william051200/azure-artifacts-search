"""Default Azure DevOps configuration."""

import os

ORG = ""
PROJECT = ""
API_VERSION = "7.1-preview.1"

# ── App defaults ──
DEFAULT_VERSION = ""

DEFAULT_THREADS = os.cpu_count() or 8
MAX_THREADS = DEFAULT_THREADS
DEFAULT_PLATFORM = "Android"
PLATFORM_OPTIONS = ["No filter", "Android", "MacIOS"]
WINDOW_SIZE = "1200x720"
WINDOW_MIN_SIZE = (900, 500)
APP_VERSION = "0.1.3"


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
