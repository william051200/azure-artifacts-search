"""Azure DevOps Artifacts API client functions."""

import re
import requests

from search_artifact_app.config import build_base_url, API_VERSION


def is_build_specific_feed(name: str) -> bool:
    """Heuristic: returns True for per-build feeds (version numbers, darc-, GUIDs)."""
    return bool(
        re.match(r"^\d+[\.\-]\d+[\.\-]\d+", name)
        or re.match(r"^darc-", name, re.IGNORECASE)
        or re.match(r"^[0-9a-f]{8}-", name)
    )


def get_feeds(
    session: requests.Session,
    base_url: str,
    api_version: str = API_VERSION,
) -> list[dict]:
    """Fetch all feeds with pagination."""
    all_feeds = []
    skip = 0
    top = 1000
    while True:
        url = f"{base_url}/feeds"
        params = {"api-version": api_version, "$top": top, "$skip": skip}
        resp = session.get(url, params=params, timeout=30)
        if resp.status_code in (401, 403):
            raise PermissionError(
                "Authentication failed — check your Personal Access Token (PAT) "
                "and ensure it has the Packaging (Read) scope."
            )
        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError:
            raise ValueError(
                "Unexpected response from Azure DevOps (not JSON). "
                "Verify your Organization, Project, and PAT are correct."
            )
        feeds = data.get("value", [])
        if not feeds:
            break
        all_feeds.extend(feeds)
        total = data.get("count", len(feeds))
        skip += top
        if skip >= total:
            break
    return all_feeds


def search_feed_for_version(
    session: requests.Session,
    feed_id: str,
    feed_name: str,
    version: str,
    contains_match: bool = False,
    base_url: str = "",
    api_version: str = API_VERSION,
) -> list[dict]:
    """Page through all packages in a feed and return those matching the target version."""
    matches = []
    skip = 0
    top = 500
    version_lower = version.lower()
    while True:
        url = f"{base_url}/Feeds/{feed_id}/packages"
        params = {
            "api-version": api_version,
            "includeAllVersions": "true",
            "$top": top,
            "$skip": skip,
        }
        try:
            resp = session.get(url, params=params, timeout=30)
            resp.raise_for_status()
        except requests.RequestException:
            return matches
        data = resp.json()
        packages = data.get("value", [])
        if not packages:
            break
        for pkg in packages:
            versions = pkg.get("versions", [])
            for v in versions:
                pkg_ver = v.get("version", "")
                if contains_match:
                    is_match = version_lower in pkg_ver.lower()
                else:
                    is_match = pkg_ver == version
                if is_match:
                    matches.append({
                        "feed": feed_name,
                        "name": pkg.get("name", "?"),
                        "type": pkg.get("protocolType", "?"),
                        "version": pkg_ver,
                        "isLatest": v.get("isLatest", False),
                        "publishDate": v.get("publishDate", ""),
                    })
        total = data.get("count", len(packages))
        skip += top
        if skip >= total:
            break
    return matches
