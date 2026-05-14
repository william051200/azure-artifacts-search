"""Background GitHub release checker and one-click upgrade trigger."""

from __future__ import annotations

import logging
import subprocess
import threading
from dataclasses import dataclass
from typing import Callable, Optional

import requests

from artifactlens.config import (
    APP_VERSION,
    GITHUB_REPO,
    INSTALL_SCRIPT_URL,
    UPDATE_CHECK_INTERVAL_SECONDS,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReleaseInfo:
    tag: str            # e.g. "v1.2.0"
    version: str        # e.g. "1.2.0" (tag stripped of leading 'v')
    html_url: str       # release page on GitHub


def _normalize(tag: str) -> str:
    return tag.lstrip("vV").strip()


def _parse_version(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in v.split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    """Return True if `latest` is a strictly newer semver-ish string than `current`."""
    try:
        return _parse_version(latest) > _parse_version(current)
    except Exception:
        return latest != current


class UpdateChecker:
    """Polls GitHub releases on a daemon thread and notifies the UI on updates.

    The callback is invoked with a `ReleaseInfo` exactly once per detected
    new version — never blocks the caller, never raises.
    """

    def __init__(
        self,
        on_update_available: Callable[[ReleaseInfo], None],
        current_version: str = APP_VERSION,
        interval_seconds: int = UPDATE_CHECK_INTERVAL_SECONDS,
        repo: str = GITHUB_REPO,
    ) -> None:
        self._callback = on_update_available
        self._current = current_version
        self._interval = interval_seconds
        self._repo = repo
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_notified: Optional[str] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, name="UpdateChecker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                info = self._fetch_latest()
                if info and is_newer(info.version, _normalize(self._current)):
                    if info.tag != self._last_notified:
                        self._last_notified = info.tag
                        try:
                            self._callback(info)
                        except Exception:
                            log.exception("Update callback failed")
            except Exception:
                log.debug("Update check failed", exc_info=True)
            if self._stop.wait(self._interval):
                return

    def _fetch_latest(self) -> Optional[ReleaseInfo]:
        url = f"https://api.github.com/repos/{self._repo}/releases/latest"
        resp = requests.get(
            url,
            headers={"User-Agent": "ArtifactLens-UpdateChecker", "Accept": "application/vnd.github+json"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        tag = data.get("tag_name")
        if not tag:
            return None
        return ReleaseInfo(
            tag=tag,
            version=_normalize(tag),
            html_url=data.get("html_url") or f"https://github.com/{self._repo}/releases/tag/{tag}",
        )


def trigger_upgrade(install_script_url: str = INSTALL_SCRIPT_URL) -> None:
    """Spawn a detached PowerShell that runs the installer with -RestartApp.

    The current process should exit shortly after calling this so the
    installer can overwrite the locked .exe.
    """
    command = (
        f"[Net.ServicePointManager]::SecurityProtocol = 'Tls12'; "
        f"$s = irm '{install_script_url}'; "
        f"$sb = [scriptblock]::Create($s); "
        f"& $sb -RestartApp"
    )
    creationflags = 0
    try:
        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
            | subprocess.DETACHED_PROCESS         # type: ignore[attr-defined]
        )
    except AttributeError:
        creationflags = 0
    subprocess.Popen(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command", command,
        ],
        close_fds=True,
        creationflags=creationflags,
    )
