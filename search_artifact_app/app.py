"""Main application window."""

import base64
import datetime
import os
import threading
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from tkinter import ttk
import tkinter as tk

import requests
from dotenv import load_dotenv

from search_artifact_app.config import (
    API_VERSION,
    build_base_url, build_artifact_url, build_feed_url, build_nuget_source_xml, PROTOCOL_TYPE_MAP,
    DEFAULT_THREADS, DEFAULT_PLATFORM, PLATFORM_OPTIONS,
    WINDOW_SIZE, WINDOW_MIN_SIZE, APP_VERSION, MAX_THREADS,
)
from search_artifact_app.theme import (
    PARCHMENT, IVORY, WHITE, WARM_SAND, NEAR_BLACK, DARK_SURFACE,
    TERRACOTTA, CORAL, CHARCOAL_WARM, OLIVE_GRAY, STONE_GRAY,
    WARM_SILVER, BORDER_CREAM, BORDER_WARM, ERROR_RED,
    FONT_SERIF_NAV, FONT_SERIF_XL, FONT_SANS_SM, FONT_SANS_MD,
    FONT_SANS_LG, FONT_SANS_LABEL, FONT_SANS_LABEL_BOLD, FONT_SANS_BTN,
    FONT_MONO,
)
from search_artifact_app.api import is_build_specific_feed, get_feeds, search_feed_for_version
from search_artifact_app.settings_dialog import open_settings


@dataclass
class SearchParams:
    """Snapshot of UI inputs captured on the main thread before search starts."""
    version: str
    feed_filter: str | None
    platform_filter: str
    include_build: bool
    contains_match: bool
    first_match_only: bool
    deduplicate_feeds: bool
    base_url: str
    api_version: str
    pat: str
    max_workers: int


class ArtifactSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ArtifactLens")
        self.geometry(WINDOW_SIZE)
        self.configure(bg=PARCHMENT)
        self.resizable(True, True)
        self.minsize(*WINDOW_MIN_SIZE)

        self._searching = False
        self._cancel = False
        self._session = None
        self._cached_feeds: list[dict] = []
        self._feeds_loaded = False
        self._feeds_loading = threading.Event()

        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        load_dotenv(env_path)
        self.org = os.getenv("AZURE_DEVOPS_ORG", "")
        self.project = os.getenv("AZURE_DEVOPS_PROJECT", "")
        self.api_version = os.getenv("API_VERSION", API_VERSION)
        pat_env = os.getenv("AZURE_DEVOPS_PAT", "")
        self.pat = "" if pat_env.startswith("<") else pat_env
        self.default_platform = os.getenv("DEFAULT_PLATFORM", DEFAULT_PLATFORM)
        self.default_version = os.getenv("DEFAULT_VERSION", "")

        self._build_ui()
        self._center_window()
        self._prefetch_feeds()

    # ── UI Construction ──

    def _build_ui(self):
        self._build_nav()
        self._build_hero()
        self._build_input_card()
        self._build_status_bar()
        self._build_footer()
        self._build_main_paned()

    def _center_window(self):
        """Center the window on screen, accounting for taskbar."""
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_nav(self):
        nav = tk.Frame(self, bg=NEAR_BLACK, height=52)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        tk.Label(
            nav, text="ArtifactLens", font=FONT_SERIF_NAV,
            bg=NEAR_BLACK, fg=IVORY,
        ).pack(side="left", padx=20)

        self.config_btn = tk.Button(
            nav, text="⚙ Settings", font=FONT_SANS_SM,
            bg=DARK_SURFACE, fg=WARM_SILVER, relief="flat",
            activebackground=CHARCOAL_WARM, activeforeground=IVORY,
            cursor="hand2", padx=10, pady=2,
            command=lambda: open_settings(self),
        )
        self.config_btn.pack(side="right", padx=20)

        self.nav_label = tk.Label(
            nav, text=f"{self.org} / {self.project}", font=FONT_MONO,
            bg=NEAR_BLACK, fg=WARM_SILVER,
        )
        self.nav_label.pack(side="right")

    def _build_hero(self):
        hero = tk.Frame(self, bg=PARCHMENT, pady=28)
        hero.pack(fill="x")
        tk.Label(
            hero, text="Find packages by version",
            font=FONT_SERIF_XL, bg=PARCHMENT, fg=NEAR_BLACK,
        ).pack()
        tk.Label(
            hero, text="Search across Azure DevOps Artifacts feeds for any version string.",
            font=FONT_SANS_MD, bg=PARCHMENT, fg=OLIVE_GRAY,
        ).pack(pady=(6, 0))

    def _make_labeled_entry(self, parent, label: str, default: str = "") -> tk.Entry:
        """Create a labeled entry field and return the Entry widget."""
        tk.Label(
            parent, text=label, font=FONT_SANS_LABEL_BOLD,
            bg=IVORY, fg=STONE_GRAY, anchor="w",
        ).pack(fill="x")
        entry = tk.Entry(
            parent, font=FONT_SANS_LG, bg=WHITE, fg=NEAR_BLACK,
            relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
            insertbackground=NEAR_BLACK,
        )
        entry.pack(fill="x", ipady=6, pady=(4, 0))
        if default:
            entry.insert(0, default)
        entry.bind("<Return>", lambda _: self._on_search())
        return entry

    def _build_input_card(self):
        card = tk.Frame(self, bg=IVORY, highlightbackground=BORDER_CREAM, highlightthickness=1)
        card.pack(fill="x", padx=32, pady=(0, 16))
        card_inner = tk.Frame(card, bg=IVORY, padx=24, pady=20)
        card_inner.pack(fill="x")

        # Row 1: Version + Feed filter + Platform
        row1 = tk.Frame(card_inner, bg=IVORY)
        row1.pack(fill="x", pady=(0, 12))

        ver_frame = tk.Frame(row1, bg=IVORY)
        ver_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.version_entry = self._make_labeled_entry(ver_frame, "VERSION", self.default_version)

        feed_frame = tk.Frame(row1, bg=IVORY)
        feed_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.feed_entry = self._make_labeled_entry(feed_frame, "FEED FILTER (OPTIONAL)")

        platform_frame = tk.Frame(row1, bg=IVORY)
        platform_frame.pack(side="left")
        tk.Label(
            platform_frame, text="PLATFORM", font=FONT_SANS_LABEL_BOLD,
            bg=IVORY, fg=STONE_GRAY, anchor="w",
        ).pack(fill="x")
        self.platform_var = tk.StringVar(value=self.default_platform)
        self.platform_combo = ttk.Combobox(
            platform_frame, textvariable=self.platform_var,
            values=PLATFORM_OPTIONS,
            state="readonly", font=FONT_SANS_MD, width=12,
        )
        self.platform_combo.pack(ipady=4, pady=(4, 0))

        # Row 2: Checkboxes + Buttons
        row2 = tk.Frame(card_inner, bg=IVORY)
        row2.pack(fill="x")

        self.include_build_var = tk.BooleanVar(value=True)
        self.include_build_cb = tk.Checkbutton(
            row2, text="Include per-build feeds", variable=self.include_build_var,
            font=FONT_SANS_SM, bg=IVORY, fg=OLIVE_GRAY,
            activebackground=IVORY, selectcolor=WARM_SAND,
        )
        self.include_build_cb.pack(side="left")

        self.contains_match_var = tk.BooleanVar(value=True)
        self.contains_match_cb = tk.Checkbutton(
            row2, text="Contains match", variable=self.contains_match_var,
            font=FONT_SANS_SM, bg=IVORY, fg=OLIVE_GRAY,
            activebackground=IVORY, selectcolor=WARM_SAND,
        )
        self.contains_match_cb.pack(side="left", padx=(12, 0))

        self.first_match_var = tk.BooleanVar(value=True)
        self.first_match_cb = tk.Checkbutton(
            row2, text="First match per feed", variable=self.first_match_var,
            font=FONT_SANS_SM, bg=IVORY, fg=OLIVE_GRAY,
            activebackground=IVORY, selectcolor=WARM_SAND,
        )
        self.first_match_cb.pack(side="left", padx=(12, 0))

        self.dedup_feeds_var = tk.BooleanVar(value=True)
        self.dedup_feeds_cb = tk.Checkbutton(
            row2, text="Deduplicate feeds", variable=self.dedup_feeds_var,
            font=FONT_SANS_SM, bg=IVORY, fg=OLIVE_GRAY,
            activebackground=IVORY, selectcolor=WARM_SAND,
        )
        self.dedup_feeds_cb.pack(side="left", padx=(12, 0))

        tk.Label(
            row2, text="Threads:", font=FONT_SANS_SM,
            bg=IVORY, fg=STONE_GRAY,
        ).pack(side="left", padx=(16, 4))
        self.thread_var = tk.StringVar(value=str(DEFAULT_THREADS))
        self.thread_spin = tk.Spinbox(
            row2, from_=1, to=MAX_THREADS, textvariable=self.thread_var,
            width=4, font=FONT_SANS_SM, bg=WHITE, fg=NEAR_BLACK,
            relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
        )
        self.thread_spin.pack(side="left")

        self.cancel_btn = tk.Button(
            row2, text="Stop", font=FONT_SANS_BTN,
            bg=WARM_SAND, fg=CHARCOAL_WARM, relief="flat",
            activebackground="#dfdbd0", cursor="hand2",
            padx=16, pady=6, state="disabled",
            command=self._on_cancel,
        )
        self.cancel_btn.pack(side="right", padx=(8, 0))

        self.search_btn = tk.Button(
            row2, text="Search", font=FONT_SANS_BTN,
            bg=TERRACOTTA, fg=IVORY, relief="flat",
            activebackground=CORAL, cursor="hand2",
            padx=20, pady=6,
            command=self._on_search,
        )
        self.search_btn.pack(side="right")

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Frame(self, bg=PARCHMENT)
        status_bar.pack(fill="x", padx=32)
        tk.Label(
            status_bar, textvariable=self.status_var,
            font=FONT_SANS_SM, bg=PARCHMENT, fg=STONE_GRAY, anchor="w",
        ).pack(side="left")
        self.count_label = tk.Label(
            status_bar, text="", font=FONT_SANS_SM,
            bg=PARCHMENT, fg=TERRACOTTA, anchor="e",
        )
        self.count_label.pack(side="right")

    def _build_main_paned(self):
        paned = tk.PanedWindow(
            self, orient="horizontal", bg=PARCHMENT,
            sashwidth=6, sashrelief="flat",
        )
        paned.pack(fill="both", expand=True, padx=32, pady=(8, 24))

        self._configure_tree_style()
        paned.add(self._build_results_table(paned), stretch="always")
        paned.add(self._build_log_panel(paned), stretch="never")

    def _configure_tree_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Claude.Treeview",
            background=IVORY, foreground=NEAR_BLACK, fieldbackground=IVORY,
            font=FONT_MONO, rowheight=28, borderwidth=0,
        )
        style.configure("Claude.Treeview.Heading",
            background=WARM_SAND, foreground=CHARCOAL_WARM,
            font=FONT_SANS_LABEL_BOLD, borderwidth=0, relief="flat",
        )
        style.map("Claude.Treeview",
            background=[("selected", WARM_SAND)],
            foreground=[("selected", NEAR_BLACK)],
        )
        style.map("Claude.Treeview.Heading",
            background=[("active", BORDER_WARM)],
        )
        style.configure("Claude.Vertical.TScrollbar",
            background=WARM_SAND, troughcolor=IVORY,
            arrowcolor=STONE_GRAY, borderwidth=0,
        )

    def _build_results_table(self, parent) -> tk.Frame:
        frame = tk.Frame(
            parent, bg=IVORY, highlightbackground=BORDER_CREAM, highlightthickness=1,
        )
        container = tk.Frame(frame, bg=IVORY)
        container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", style="Claude.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            container, style="Claude.Treeview",
            columns=("feed", "type", "name", "version", "latest"),
            show="headings", yscrollcommand=scrollbar.set,
        )
        for col, text, width, minw in [
            ("feed", "Feed", 180, 100),
            ("type", "Type", 70, 50),
            ("name", "Package Name", 300, 150),
            ("version", "Version", 100, 70),
            ("latest", "Latest", 55, 40),
        ]:
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, minwidth=minw)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _: self._open_selected())
        self.tree.bind("<Button-3>", self._show_context_menu)
        scrollbar.config(command=self.tree.yview)
        return frame

    def _build_log_panel(self, parent) -> tk.Frame:
        outer = tk.Frame(
            parent, bg=IVORY, highlightbackground=BORDER_CREAM, highlightthickness=1,
        )
        header = tk.Frame(outer, bg=WARM_SAND, padx=16, pady=6)
        header.pack(fill="x")
        tk.Label(
            header, text="LOG", font=FONT_SANS_LABEL_BOLD,
            bg=WARM_SAND, fg=CHARCOAL_WARM, anchor="w",
        ).pack(side="left")
        tk.Button(
            header, text="Clear", font=FONT_SANS_LABEL,
            bg=WARM_SAND, fg=OLIVE_GRAY, relief="flat",
            activebackground=BORDER_WARM, cursor="hand2",
            command=self._clear_log,
        ).pack(side="right")

        container = tk.Frame(outer, bg=IVORY)
        container.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(container, orient="vertical", style="Claude.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        self.log_text = tk.Text(
            container, font=FONT_MONO, bg=IVORY, fg=CHARCOAL_WARM,
            relief="flat", wrap="word", state="disabled", width=38,
            yscrollcommand=scrollbar.set, borderwidth=0,
            selectbackground=WARM_SAND, selectforeground=NEAR_BLACK,
        )
        self.log_text.tag_configure("timestamp", foreground=STONE_GRAY)
        self.log_text.tag_configure("info", foreground=CHARCOAL_WARM)
        self.log_text.tag_configure("success", foreground="#2e7d32")
        self.log_text.tag_configure("error", foreground=ERROR_RED)
        self.log_text.tag_configure("warn", foreground=TERRACOTTA)
        self.log_text.pack(fill="both", expand=True, padx=8, pady=4)
        scrollbar.config(command=self.log_text.yview)
        return outer

    def _build_footer(self):
        separator = tk.Frame(self, bg=BORDER_WARM, height=1)
        separator.pack(side="bottom", fill="x")
        footer = tk.Frame(self, bg=WARM_SAND, pady=6)
        footer.pack(side="bottom", fill="x")
        tk.Label(
            footer,
            text=f"💡 Tip: Double-click to open feed · Right-click for more options",
            font=FONT_SANS_LABEL, bg=WARM_SAND, fg=OLIVE_GRAY, anchor="w",
        ).pack(side="left", padx=16)
        tk.Label(
            footer,
            text=f"ArtifactLens v{APP_VERSION}",
            font=FONT_SANS_LABEL, bg=WARM_SAND, fg=STONE_GRAY, anchor="e",
        ).pack(side="right", padx=16)

    # ── Browser ──

    def _get_selected_values(self):
        """Return (feed_name, pkg_type, pkg_name, pkg_version) for the selected row, or None."""
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        return values[0], values[1], values[2], values[3]

    def _open_selected(self):
        """Double-click handler — opens the feed URL by default."""
        self._open_feed_url()

    def _open_feed_url(self):
        vals = self._get_selected_values()
        if not vals:
            return
        feed_name = vals[0]
        url = build_feed_url(self.org, self.project, feed_name)
        webbrowser.open(url)

    def _open_artifact_url(self):
        vals = self._get_selected_values()
        if not vals:
            return
        feed_name, pkg_type, pkg_name, pkg_version = vals
        proto = PROTOCOL_TYPE_MAP.get(pkg_type, pkg_type)
        url = build_artifact_url(self.org, self.project, feed_name, proto, pkg_name, pkg_version)
        webbrowser.open(url)

    def _copy_nuget_source(self):
        """Copy the NuGet <add key=...> XML snippet for the selected feed to clipboard."""
        vals = self._get_selected_values()
        if not vals:
            return
        feed_name = vals[0]
        snippet = build_nuget_source_xml(feed_name, self.org, self.project)
        self.clipboard_clear()
        self.clipboard_append(snippet)
        self._log(f"Copied NuGet source to clipboard: {feed_name}")

    def _show_context_menu(self, event):
        """Show right-click context menu on the results table."""
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        self.tree.selection_set(row_id)
        menu = tk.Menu(self, tearoff=0, font=FONT_SANS_SM,
                       bg=IVORY, fg=NEAR_BLACK, activebackground=WARM_SAND,
                       activeforeground=NEAR_BLACK)
        menu.add_command(label="Go to Feed", command=self._open_feed_url)
        menu.add_command(label="Go to Artifact", command=self._open_artifact_url)
        menu.add_separator()
        menu.add_command(label="Copy NuGet Source", command=self._copy_nuget_source)
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()

    # ── Logging ──

    def _log(self, message: str, tag: str = "info"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")

        def _append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", f"[{ts}] ", "timestamp")
            self.log_text.insert("end", f"{message}\n", tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")

        self.after(0, _append)

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # ── Search actions ──

    def _make_session(self, pat: str) -> requests.Session:
        """Create an authenticated requests session."""
        session = requests.Session()
        session.headers["Accept"] = "application/json"
        if pat:
            token = base64.b64encode(f":{pat}".encode()).decode()
            session.headers["Authorization"] = f"Basic {token}"
        return session

    def _prefetch_feeds(self):
        """Fetch feed list in background on startup so searches don't wait."""
        self.status_var.set("Loading feeds...")
        self._log("Prefetching feed list on startup...")
        self._feeds_loading.clear()

        def _fetch():
            base_url = build_base_url(self.org, self.project)
            session = self._make_session(self.pat)
            try:
                feeds = get_feeds(session, base_url, self.api_version)
                self._cached_feeds = feeds
                self._feeds_loaded = True
                self._log(f"Feed cache ready — {len(feeds)} feeds loaded.", "success")
                self.after(0, lambda: self.status_var.set(f"Ready — {len(feeds)} feeds cached"))
            except Exception as e:
                self._log(f"Prefetch failed: {e}. Feeds will be fetched on first search.", "warn")
                self.after(0, lambda: self.status_var.set("Ready (feeds not cached)"))
            finally:
                self._feeds_loading.set()
                session.close()

        threading.Thread(target=_fetch, daemon=True).start()

    def _set_inputs_state(self, state: str):
        """Enable or disable all input fields."""
        for widget in (
            self.version_entry, self.feed_entry,
            self.include_build_cb, self.contains_match_cb,
            self.first_match_cb, self.dedup_feeds_cb, self.thread_spin, self.config_btn,
        ):
            widget.config(state=state)
        self.platform_combo.config(state="disabled" if state == "disabled" else "readonly")

    def _capture_search_params(self) -> SearchParams:
        """Snapshot all UI values on the main thread so the worker never touches Tk."""
        return SearchParams(
            version=self.version_entry.get().strip(),
            feed_filter=self.feed_entry.get().strip() or None,
            platform_filter=self.platform_var.get(),
            include_build=self.include_build_var.get(),
            contains_match=self.contains_match_var.get(),
            first_match_only=self.first_match_var.get(),
            deduplicate_feeds=self.dedup_feeds_var.get(),
            base_url=build_base_url(self.org, self.project),
            api_version=self.api_version,
            pat=self.pat,
            max_workers=max(1, min(MAX_THREADS, int(self.thread_var.get()))),
        )

    def _on_search(self):
        version = self.version_entry.get().strip()
        if not version or self._searching:
            return
        self._searching = True
        self._cancel = False

        params = self._capture_search_params()

        self.search_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self._set_inputs_state("disabled")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.count_label.config(text="")
        self.status_var.set("Searching..." if self._feeds_loaded else "Fetching feeds...")
        self._log(f"Starting search for version '{version}'...")
        threading.Thread(target=self._search_thread, args=(params,), daemon=True).start()

    def _on_cancel(self):
        self._cancel = True
        self.status_var.set("Stopping...")
        self.cancel_btn.config(state="disabled")
        self._log("Stop requested.", "warn")
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass

    def _filter_feeds(self, feeds: list[dict], params: SearchParams) -> list[dict]:
        """Apply text, platform, and build-specific filters to the feed list."""
        if params.feed_filter:
            feeds = [f for f in feeds if params.feed_filter.lower() in f["name"].lower()]
            self._log(f"Feed filter '{params.feed_filter}' applied — {len(feeds)} feeds match.")
        if params.platform_filter and params.platform_filter != "No filter":
            feeds = [f for f in feeds if params.platform_filter.lower() in f["name"].lower()]
            self._log(f"Platform filter '{params.platform_filter}' applied — {len(feeds)} feeds match.")
        if params.deduplicate_feeds:
            before = len(feeds)
            seen = set()
            feeds = [f for f in feeds if f["name"] not in seen and not seen.add(f["name"])]
            deduped = before - len(feeds)
            if deduped:
                self._log(f"Deduplicated {deduped} duplicate feeds.")
        if not params.include_build:
            before = len(feeds)
            feeds = [f for f in feeds if not is_build_specific_feed(f["name"])]
            skipped = before - len(feeds)
            if skipped:
                self._log(f"Skipped {skipped} per-build feeds.")
        return feeds

    def _search_thread(self, params: SearchParams):
        # Wait for prefetch to complete if still in progress
        if not self._feeds_loading.is_set():
            self._log("Waiting for feed list to finish loading...")
            self.after(0, lambda: self.status_var.set("Waiting for feeds to load..."))
            while not self._feeds_loading.wait(timeout=0.2):
                if self._cancel:
                    self.after(0, lambda: self._finish_search("Search stopped.", []))
                    return

        session = self._make_session(params.pat)
        self._session = session

        if self._feeds_loaded:
            feeds = list(self._cached_feeds)
            self._log(f"Using cached feed list ({len(feeds)} feeds).", "success")
        else:
            try:
                self._log("Fetching feed list from Azure DevOps...")
                feeds = get_feeds(session, params.base_url, params.api_version)
                self._cached_feeds = feeds
                self._feeds_loaded = True
                self._log(f"Retrieved {len(feeds)} total feeds.", "success")
            except PermissionError as e:
                self._log(str(e), "error")
                self.after(0, lambda: self._finish_search(str(e), []))
                return
            except Exception as e:
                if self._cancel:
                    self.after(0, lambda: self._finish_search("Search stopped.", []))
                    return
                self._log(f"Error fetching feeds: {e}", "error")
                self.after(0, lambda: self._finish_search(f"Error fetching feeds: {e}", []))
                return

        feeds = self._filter_feeds(feeds, params)
        total = len(feeds)
        all_matches = []
        completed = [0]
        lock = threading.Lock()

        self.after(0, lambda: self.status_var.set(f"Searching {total} feeds for v{params.version}..."))
        self._log(f"Searching {total} feeds with {params.max_workers} threads...")

        cancelled = self._execute_parallel_search(
            session, feeds, params, all_matches, completed, lock, total,
        )

        if cancelled:
            msg = "Search stopped."
        elif all_matches:
            msg = f"Done — {len(all_matches)} match(es) across {total} feeds."
            self._log(msg, "success")
        else:
            msg = f"No packages found with version {params.version}."
            self._log(msg, "warn")
        self.after(0, lambda: self._finish_search(msg, all_matches))

    def _execute_parallel_search(
        self,
        session: requests.Session,
        feeds: list[dict],
        params: SearchParams,
        all_matches: list,
        completed: list[int],
        lock: threading.Lock,
        total: int,
    ) -> bool:
        """Run the parallel feed search. Returns True if cancelled."""

        def _search_one(feed):
            if self._cancel:
                return []
            return search_feed_for_version(
                session, feed["id"], feed["name"], params.version,
                params.contains_match, params.first_match_only,
                params.base_url, params.api_version,
            )

        try:
            with ThreadPoolExecutor(max_workers=params.max_workers) as executor:
                future_to_feed = {executor.submit(_search_one, f): f for f in feeds}
                for future in as_completed(future_to_feed):
                    if self._cancel:
                        for f in future_to_feed:
                            f.cancel()
                        executor.shutdown(wait=False, cancel_futures=True)
                        self._log("Search stopped.", "warn")
                        return True

                    feed = future_to_feed[future]
                    fname = feed["name"]
                    with lock:
                        completed[0] += 1
                        idx = completed[0]

                    self.after(0, lambda n=fname, i=idx: self.status_var.set(
                        f"[{i}/{total}]  {n}"
                    ))

                    try:
                        matches = future.result()
                    except Exception as exc:
                        if self._cancel:
                            return True
                        self._log(f"Error searching feed '{fname}': {exc}", "error")
                        matches = []

                    if matches:
                        with lock:
                            all_matches.extend(matches)
                        for m in matches:
                            row = (m["feed"], m["type"], m["name"], m["version"],
                                   "✓" if m["isLatest"] else "")
                            self.after(0, lambda r=row: self.tree.insert("", "end", values=r))
                            self._log(f"  ✓ [{m['feed']}] {m['type']}  {m['name']}", "success")
                        with lock:
                            count = len(all_matches)
                        self.after(0, lambda c=count: self.count_label.config(
                            text=f"{c} match{'es' if c != 1 else ''}"
                        ))
        except Exception as e:
            if not self._cancel:
                self._log(f"Search error: {e}", "error")
            return True

        return False

    def _finish_search(self, msg: str, matches: list):
        self.status_var.set(msg)
        self.count_label.config(
            text=f"{len(matches)} result{'s' if len(matches) != 1 else ''}" if matches else ""
        )
        self.search_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self._set_inputs_state("normal")
        self._searching = False
        self._cancel = False
        self._session = None
