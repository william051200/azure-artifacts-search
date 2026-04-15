"""Default Azure DevOps configuration."""

ORG = "dnceng"
PROJECT = "public"
API_VERSION = "7.1-preview.1"


def build_base_url(org: str, project: str) -> str:
    return f"https://feeds.dev.azure.com/{org}/{project}/_apis/packaging"


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
