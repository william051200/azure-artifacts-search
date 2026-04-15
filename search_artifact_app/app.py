"""Main application window."""

import base64
import datetime
import os
import threading
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import ttk
import tkinter as tk

import requests
from dotenv import load_dotenv

from search_artifact_app.config import (
    ORG, PROJECT, API_VERSION,
    build_base_url, build_artifact_url, PROTOCOL_TYPE_MAP,
)
from search_artifact_app.theme import (
    PARCHMENT, IVORY, WHITE, WARM_SAND, NEAR_BLACK, DARK_SURFACE,
    TERRACOTTA, CORAL, CHARCOAL_WARM, OLIVE_GRAY, STONE_GRAY,
    WARM_SILVER, BORDER_CREAM, BORDER_WARM, ERROR_RED,
    FONT_SERIF_XL, FONT_SANS_SM, FONT_SANS_LABEL, FONT_MONO,
)
from search_artifact_app.api import is_build_specific_feed, get_feeds, search_feed_for_version
from search_artifact_app.settings_dialog import open_settings


class ArtifactSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Azure Artifacts Search")
        self.geometry("1200x720")
        self.configure(bg=PARCHMENT)
        self.resizable(True, True)
        self.minsize(900, 500)

        self._searching = False
        self._cancel = False

        # Load .env file if present
        load_dotenv()

        # Editable config — prefer .env values, fall back to defaults
        self.org = os.getenv("AZURE_DEVOPS_ORG", ORG)
        self.project = os.getenv("AZURE_DEVOPS_PROJECT", PROJECT)
        self.api_version = API_VERSION
        pat_env = os.getenv("AZURE_DEVOPS_PAT", "")
        self.pat = "" if pat_env.startswith("<") else pat_env

        self._build_ui()

    # ── UI Construction ──

    def _build_ui(self):
        self._build_nav()
        self._build_hero()
        self._build_input_card()
        self._build_status_bar()
        self._build_main_paned()
        self._build_footer()

    def _build_nav(self):
        nav = tk.Frame(self, bg=NEAR_BLACK, height=52)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        tk.Label(
            nav, text="Artifact Search", font=("Georgia", 16, "normal"),
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
            font=("Segoe UI", 12), bg=PARCHMENT, fg=OLIVE_GRAY,
        ).pack(pady=(6, 0))

    def _build_input_card(self):
        card = tk.Frame(self, bg=IVORY, highlightbackground=BORDER_CREAM, highlightthickness=1)
        card.pack(fill="x", padx=32, pady=(0, 16))
        card_inner = tk.Frame(card, bg=IVORY, padx=24, pady=20)
        card_inner.pack(fill="x")

        # Row 1: Version + Feed filter
        row1 = tk.Frame(card_inner, bg=IVORY)
        row1.pack(fill="x", pady=(0, 12))

        ver_frame = tk.Frame(row1, bg=IVORY)
        ver_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(
            ver_frame, text="VERSION", font=("Segoe UI", 9, "bold"),
            bg=IVORY, fg=STONE_GRAY, anchor="w",
        ).pack(fill="x")
        self.version_entry = tk.Entry(
            ver_frame, font=("Segoe UI", 13), bg=WHITE, fg=NEAR_BLACK,
            relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
            insertbackground=NEAR_BLACK,
        )
        self.version_entry.pack(fill="x", ipady=6, pady=(4, 0))
        self.version_entry.insert(0, "36.1.35")
        self.version_entry.bind("<Return>", lambda _: self._on_search())

        feed_frame = tk.Frame(row1, bg=IVORY)
        feed_frame.pack(side="left", fill="x", expand=True)
        tk.Label(
            feed_frame, text="FEED FILTER (OPTIONAL)", font=("Segoe UI", 9, "bold"),
            bg=IVORY, fg=STONE_GRAY, anchor="w",
        ).pack(fill="x")
        self.feed_entry = tk.Entry(
            feed_frame, font=("Segoe UI", 13), bg=WHITE, fg=NEAR_BLACK,
            relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
            insertbackground=NEAR_BLACK,
        )
        self.feed_entry.pack(fill="x", ipady=6, pady=(4, 0))
        self.feed_entry.bind("<Return>", lambda _: self._on_search())

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

        tk.Label(
            row2, text="Threads:", font=FONT_SANS_SM,
            bg=IVORY, fg=STONE_GRAY,
        ).pack(side="left", padx=(16, 4))
        self.thread_var = tk.StringVar(value="8")
        self.thread_spin = tk.Spinbox(
            row2, from_=1, to=32, textvariable=self.thread_var,
            width=4, font=FONT_SANS_SM, bg=WHITE, fg=NEAR_BLACK,
            relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
        )
        self.thread_spin.pack(side="left")

        self.cancel_btn = tk.Button(
            row2, text="Cancel", font=("Segoe UI", 11, "bold"),
            bg=WARM_SAND, fg=CHARCOAL_WARM, relief="flat",
            activebackground="#dfdbd0", cursor="hand2",
            padx=16, pady=6, state="disabled",
            command=self._on_cancel,
        )
        self.cancel_btn.pack(side="right", padx=(8, 0))

        self.search_btn = tk.Button(
            row2, text="Search", font=("Segoe UI", 11, "bold"),
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

        # ── Results table ──
        results_frame = tk.Frame(
            paned, bg=IVORY, highlightbackground=BORDER_CREAM, highlightthickness=1,
        )
        tree_container = tk.Frame(results_frame, bg=IVORY)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Claude.Treeview",
            background=IVORY, foreground=NEAR_BLACK, fieldbackground=IVORY,
            font=FONT_MONO, rowheight=28, borderwidth=0,
        )
        style.configure("Claude.Treeview.Heading",
            background=WARM_SAND, foreground=CHARCOAL_WARM,
            font=("Segoe UI", 9, "bold"), borderwidth=0, relief="flat",
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

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", style="Claude.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_container, style="Claude.Treeview",
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
        scrollbar.config(command=self.tree.yview)

        paned.add(results_frame, stretch="always")

        # ── Log panel ──
        log_outer = tk.Frame(
            paned, bg=IVORY, highlightbackground=BORDER_CREAM, highlightthickness=1,
        )
        log_header = tk.Frame(log_outer, bg=WARM_SAND, padx=16, pady=6)
        log_header.pack(fill="x")
        tk.Label(
            log_header, text="LOG", font=("Segoe UI", 9, "bold"),
            bg=WARM_SAND, fg=CHARCOAL_WARM, anchor="w",
        ).pack(side="left")
        tk.Button(
            log_header, text="Clear", font=FONT_SANS_LABEL,
            bg=WARM_SAND, fg=OLIVE_GRAY, relief="flat",
            activebackground=BORDER_WARM, cursor="hand2",
            command=self._clear_log,
        ).pack(side="right")

        log_container = tk.Frame(log_outer, bg=IVORY)
        log_container.pack(fill="both", expand=True)
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", style="Claude.Vertical.TScrollbar")
        log_scrollbar.pack(side="right", fill="y")
        self.log_text = tk.Text(
            log_container, font=FONT_MONO, bg=IVORY, fg=CHARCOAL_WARM,
            relief="flat", wrap="word", state="disabled", width=38,
            yscrollcommand=log_scrollbar.set, borderwidth=0,
            selectbackground=WARM_SAND, selectforeground=NEAR_BLACK,
        )
        self.log_text.tag_configure("timestamp", foreground=STONE_GRAY)
        self.log_text.tag_configure("info", foreground=CHARCOAL_WARM)
        self.log_text.tag_configure("success", foreground="#2e7d32")
        self.log_text.tag_configure("error", foreground=ERROR_RED)
        self.log_text.tag_configure("warn", foreground=TERRACOTTA)
        self.log_text.pack(fill="both", expand=True, padx=8, pady=4)
        log_scrollbar.config(command=self.log_text.yview)

        paned.add(log_outer, stretch="never")

    def _build_footer(self):
        footer = tk.Frame(self, bg=PARCHMENT, pady=6)
        footer.pack(fill="x")
        tk.Label(
            footer, text="Double-click a result to open it in Azure DevOps  ·  Azure Artifacts Search",
            font=FONT_SANS_LABEL, bg=PARCHMENT, fg=STONE_GRAY,
        ).pack()

    # ── Browser ──

    def _open_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        feed_name, pkg_type, pkg_name, pkg_version = values[0], values[1], values[2], values[3]
        proto = PROTOCOL_TYPE_MAP.get(pkg_type, pkg_type)
        url = build_artifact_url(self.org, self.project, feed_name, proto, pkg_name, pkg_version)
        webbrowser.open(url)

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

    def _set_inputs_state(self, state: str):
        """Enable or disable all input fields. state is 'normal' or 'disabled'."""
        for widget in (
            self.version_entry, self.feed_entry,
            self.include_build_cb, self.contains_match_cb,
            self.thread_spin, self.config_btn,
        ):
            widget.config(state=state)

    def _on_search(self):
        version = self.version_entry.get().strip()
        if not version or self._searching:
            return
        self._searching = True
        self._cancel = False
        self.search_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self._set_inputs_state("disabled")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.count_label.config(text="")
        self.status_var.set("Fetching feeds...")
        self._log(f"Starting search for version '{version}'...")
        threading.Thread(target=self._search_thread, args=(version,), daemon=True).start()

    def _on_cancel(self):
        self._cancel = True
        self.status_var.set("Cancelling...")
        self.cancel_btn.config(state="disabled")
        self._log("Cancellation requested.", "warn")

    def _search_thread(self, version: str):
        feed_filter = self.feed_entry.get().strip() or None
        include_build = self.include_build_var.get()
        contains_match = self.contains_match_var.get()
        base_url = build_base_url(self.org, self.project)
        api_ver = self.api_version

        session = requests.Session()
        session.headers["Accept"] = "application/json"
        if self.pat:
            token = base64.b64encode(f":{self.pat}".encode()).decode()
            session.headers["Authorization"] = f"Basic {token}"

        try:
            self._log("Fetching feed list from Azure DevOps...")
            feeds = get_feeds(session, base_url, api_ver)
            self._log(f"Retrieved {len(feeds)} total feeds.", "success")
        except Exception as e:
            self._log(f"Error fetching feeds: {e}", "error")
            self.after(0, lambda: self._finish_search(f"Error fetching feeds: {e}", []))
            return

        # Filter feeds
        if feed_filter:
            feeds = [f for f in feeds if feed_filter.lower() in f["name"].lower()]
            self._log(f"Feed filter '{feed_filter}' applied — {len(feeds)} feeds match.")
        if not include_build:
            before = len(feeds)
            feeds = [f for f in feeds if not is_build_specific_feed(f["name"])]
            skipped = before - len(feeds)
            if skipped:
                self._log(f"Skipped {skipped} per-build feeds.")

        total = len(feeds)
        all_matches = []
        completed = [0]
        lock = threading.Lock()
        max_workers = max(1, min(32, int(self.thread_var.get())))

        self.after(0, lambda: self.status_var.set(f"Searching {total} feeds for v{version}..."))
        self._log(f"Searching {total} feeds with {max_workers} threads...")

        def _search_one_feed(feed):
            if self._cancel:
                return []
            return search_feed_for_version(
                session, feed["id"], feed["name"], version, contains_match,
                base_url, api_ver,
            )

        cancelled = False
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_feed = {executor.submit(_search_one_feed, f): f for f in feeds}
                for future in as_completed(future_to_feed):
                    if self._cancel:
                        for f in future_to_feed:
                            f.cancel()
                        self._log("Search cancelled.", "warn")
                        cancelled = True
                        break

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
            self._log(f"Search error: {e}", "error")
            cancelled = True

        if cancelled:
            msg = "Search cancelled."
        elif all_matches:
            msg = f"Done — {len(all_matches)} match(es) across {total} feeds."
            self._log(msg, "success")
        else:
            msg = f"No packages found with version {version}."
            self._log(msg, "warn")
        self.after(0, lambda: self._finish_search(msg, all_matches))

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
