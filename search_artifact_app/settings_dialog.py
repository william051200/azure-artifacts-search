"""Settings popup dialog."""

import tkinter as tk

from search_artifact_app.theme import (
    PARCHMENT, IVORY, WHITE, WARM_SAND, NEAR_BLACK,
    TERRACOTTA, CORAL, CHARCOAL_WARM, OLIVE_GRAY, STONE_GRAY,
    BORDER_WARM,
    FONT_SERIF_LG, FONT_SANS_LABEL,
)


def open_settings(parent) -> None:
    """Open a modal settings dialog that edits parent.org, .project, .api_version, .pat."""
    popup = tk.Toplevel(parent)
    popup.title("Settings")
    popup.geometry("420x340")
    popup.configure(bg=PARCHMENT)
    popup.resizable(False, False)
    popup.transient(parent)
    popup.grab_set()

    tk.Label(
        popup, text="Configuration", font=FONT_SERIF_LG,
        bg=PARCHMENT, fg=NEAR_BLACK,
    ).pack(pady=(20, 16))

    form = tk.Frame(popup, bg=PARCHMENT, padx=32)
    form.pack(fill="x")

    fields = [
        ("Organization", parent.org),
        ("Project", parent.project),
        ("API Version", parent.api_version),
    ]
    entries = {}
    for label_text, default in fields:
        tk.Label(
            form, text=label_text.upper(), font=("Segoe UI", 9, "bold"),
            bg=PARCHMENT, fg=STONE_GRAY, anchor="w",
        ).pack(fill="x", pady=(8, 0))
        entry = tk.Entry(
            form, font=("Segoe UI", 12), bg=WHITE, fg=NEAR_BLACK,
            relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
            insertbackground=NEAR_BLACK,
        )
        entry.insert(0, default)
        entry.pack(fill="x", ipady=4, pady=(2, 0))
        entries[label_text] = entry

    # PAT field with show/hide
    pat_label_frame = tk.Frame(form, bg=PARCHMENT)
    pat_label_frame.pack(fill="x", pady=(8, 0))
    tk.Label(
        pat_label_frame, text="PERSONAL ACCESS TOKEN", font=("Segoe UI", 9, "bold"),
        bg=PARCHMENT, fg=STONE_GRAY, anchor="w",
    ).pack(side="left")

    show_var = tk.BooleanVar(value=False)
    pat_entry = tk.Entry(
        form, font=("Segoe UI", 12), bg=WHITE, fg=NEAR_BLACK,
        relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
        insertbackground=NEAR_BLACK, show="•",
    )
    pat_entry.insert(0, parent.pat)
    pat_entry.pack(fill="x", ipady=4, pady=(2, 0))

    def _toggle_show():
        pat_entry.config(show="" if show_var.get() else "•")

    tk.Checkbutton(
        pat_label_frame, text="Show", variable=show_var,
        font=FONT_SANS_LABEL, bg=PARCHMENT, fg=OLIVE_GRAY,
        activebackground=PARCHMENT, selectcolor=WARM_SAND,
        command=_toggle_show,
    ).pack(side="right")

    entries["PAT"] = pat_entry

    btn_frame = tk.Frame(popup, bg=PARCHMENT)
    btn_frame.pack(pady=20)

    def _save():
        parent.org = entries["Organization"].get().strip() or parent.org
        parent.project = entries["Project"].get().strip() or parent.project
        parent.api_version = entries["API Version"].get().strip() or parent.api_version
        parent.pat = entries["PAT"].get().strip()
        parent.nav_label.config(text=f"{parent.org} / {parent.project}")
        popup.destroy()

    tk.Button(
        btn_frame, text="Save", font=("Segoe UI", 11, "bold"),
        bg=TERRACOTTA, fg=IVORY, relief="flat",
        activebackground=CORAL, cursor="hand2",
        padx=20, pady=6, command=_save,
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        btn_frame, text="Cancel", font=("Segoe UI", 11, "bold"),
        bg=WARM_SAND, fg=CHARCOAL_WARM, relief="flat",
        activebackground=BORDER_WARM, cursor="hand2",
        padx=16, pady=6, command=popup.destroy,
    ).pack(side="left")
