"""Search Azure DevOps Artifacts feeds for packages matching a specific version.

Usage:
    python search_artifact.py <version>                          # search all major feeds
    python search_artifact.py 36.1.35 --feed dotnet-eng          # search one feed by name
    python search_artifact.py 36.1.35 --feed-filter dotnet       # search feeds whose name contains 'dotnet'
    python search_artifact.py --list-feeds                       # list all available feeds
    python search_artifact.py --list-feeds --feed-filter dotnet  # list feeds matching a pattern
"""

import argparse
import sys
import requests

ORG = "dnceng"
PROJECT = "public"
BASE_URL = f"https://feeds.dev.azure.com/{ORG}/{PROJECT}/_apis/packaging"
API_VERSION = "7.1-preview.1"


def get_feeds(session: requests.Session) -> list[dict]:
    url = f"{BASE_URL}/feeds"
    resp = session.get(url, params={"api-version": API_VERSION})
    resp.raise_for_status()
    return resp.json().get("value", [])


def is_build_specific_feed(name: str) -> bool:
    """Heuristic: skip per-build feeds (names that look like version numbers or build IDs)."""
    import re
    # Matches: "10.0.100-...", "10-0-0-preview-...", "darc-...", GUIDs, etc.
    return bool(
        re.match(r"^\d+[\.\-]\d+[\.\-]\d+", name)
        or re.match(r"^darc-", name, re.IGNORECASE)
        or re.match(r"^[0-9a-f]{8}-", name)
    )


def search_feed_for_version(
    session: requests.Session, feed_id: str, feed_name: str, version: str
) -> list[dict]:
    """Page through all packages in a feed and return those that have the target version."""
    matches = []
    skip = 0
    top = 500

    while True:
        url = f"{BASE_URL}/Feeds/{feed_id}/packages"
        params = {
            "api-version": API_VERSION,
            "includeAllVersions": "true",
            "$top": top,
            "$skip": skip,
        }
        try:
            resp = session.get(url, params=params, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  ⚠ Error querying feed '{feed_name}': {e}")
            return matches

        data = resp.json()
        packages = data.get("value", [])

        if not packages:
            break

        for pkg in packages:
            pkg_name = pkg.get("name", "?")
            pkg_type = pkg.get("protocolType", "?")
            versions = pkg.get("versions", [])
            for v in versions:
                if v.get("version") == version:
                    matches.append(
                        {
                            "feed": feed_name,
                            "name": pkg_name,
                            "type": pkg_type,
                            "version": v.get("version"),
                            "isLatest": v.get("isLatest", False),
                            "publishDate": v.get("publishDate", ""),
                        }
                    )
                    break

        total = data.get("count", len(packages))
        skip += top
        if skip >= total:
            break

        print(f"  ... scanned {skip}/{total} packages in '{feed_name}'", flush=True)

    return matches


def main():
    parser = argparse.ArgumentParser(
        description="Search Azure DevOps Artifacts (dnceng/public) for a package by version."
    )
    parser.add_argument("version", nargs="?", help="Package version to search for (e.g. 36.1.35)")
    parser.add_argument("--feed", help="Search only this exact feed name", default=None)
    parser.add_argument("--feed-filter", help="Search feeds whose name contains this substring (case-insensitive)", default=None)
    parser.add_argument("--list-feeds", action="store_true", help="List available feeds and exit")
    parser.add_argument("--include-build-feeds", action="store_true",
                        help="Include per-build feeds (skipped by default, there are thousands)")
    args = parser.parse_args()

    if not args.list_feeds and not args.version:
        parser.error("Please provide a version to search for, or use --list-feeds.")

    session = requests.Session()
    session.headers["Accept"] = "application/json"

    print(f"Fetching feeds from {ORG}/{PROJECT} ...")
    feeds = get_feeds(session)
    print(f"Total feeds: {len(feeds)}")

    # --- List feeds mode ---
    if args.list_feeds:
        if args.feed_filter:
            feeds = [f for f in feeds if args.feed_filter.lower() in f["name"].lower()]
        if not args.include_build_feeds:
            feeds = [f for f in feeds if not is_build_specific_feed(f["name"])]
        print(f"Showing {len(feeds)} feed(s):\n")
        for f in sorted(feeds, key=lambda x: x["name"].lower()):
            print(f"  {f['name']}")
        return

    # --- Search mode: filter feeds ---
    if args.feed:
        feeds = [f for f in feeds if f["name"].lower() == args.feed.lower()]
        if not feeds:
            print(f"Feed '{args.feed}' not found.")
            sys.exit(1)
    elif args.feed_filter:
        feeds = [f for f in feeds if args.feed_filter.lower() in f["name"].lower()]
        if not args.include_build_feeds:
            feeds = [f for f in feeds if not is_build_specific_feed(f["name"])]
    else:
        if not args.include_build_feeds:
            feeds = [f for f in feeds if not is_build_specific_feed(f["name"])]

    print(f"Searching {len(feeds)} feed(s) for version '{args.version}' ...\n")

    all_matches = []
    for i, feed in enumerate(feeds, 1):
        fname = feed["name"]
        fid = feed["id"]
        print(f"[{i}/{len(feeds)}] Searching feed '{fname}' ...")
        matches = search_feed_for_version(session, fid, fname, args.version)
        if matches:
            all_matches.extend(matches)
            for m in matches:
                latest_tag = " (latest)" if m["isLatest"] else ""
                print(f"  ✓ {m['type']:6s}  {m['name']}  {m['version']}{latest_tag}")
        else:
            print(f"  No matches.")

    print()
    print("=" * 60)
    if all_matches:
        print(f"Found {len(all_matches)} package(s) with version {args.version}:\n")
        for m in all_matches:
            latest_tag = " (latest)" if m["isLatest"] else ""
            date_str = f"  ({m['publishDate'][:10]})" if m["publishDate"] else ""
            print(f"  [{m['feed']}] {m['type']:6s}  {m['name']}  {m['version']}{latest_tag}{date_str}")
    else:
        print(f"No packages found with version {args.version}.")
        print("Tip: try --include-build-feeds to also search per-build feeds.")


if __name__ == "__main__":
    main()
