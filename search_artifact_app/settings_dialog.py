"""Settings popup dialog."""

import os
import tkinter as tk

from search_artifact_app.theme import (
    PARCHMENT, IVORY, WHITE, WARM_SAND, NEAR_BLACK,
    TERRACOTTA, CORAL, CHARCOAL_WARM, OLIVE_GRAY, STONE_GRAY,
    BORDER_WARM,
    FONT_SERIF_LG, FONT_SANS_MD, FONT_SANS_LABEL, FONT_SANS_LABEL_BOLD, FONT_SANS_BTN,
)


def _make_field(form, label_text: str, default: str, show: str = "") -> tk.Entry:
    """Create a labeled entry field and return the Entry widget."""
    tk.Label(
        form, text=label_text, font=FONT_SANS_LABEL_BOLD,
        bg=PARCHMENT, fg=STONE_GRAY, anchor="w",
    ).pack(fill="x", pady=(12, 0))
    entry = tk.Entry(
        form, font=FONT_SANS_MD, bg=WHITE, fg=NEAR_BLACK,
        relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
        insertbackground=NEAR_BLACK,
    )
    if show:
        entry.config(show=show)
    entry.insert(0, default)
    entry.pack(fill="x", ipady=5, pady=(3, 0))
    return entry


def open_settings(parent) -> None:
    """Open a modal settings dialog that edits parent.org, .project, .api_version, .pat."""
    popup = tk.Toplevel(parent)
    popup.title("Settings")
    popup.configure(bg=PARCHMENT)
    popup.resizable(False, False)
    popup.transient(parent)
    popup.grab_set()

    # Title
    tk.Label(
        popup, text="Configuration", font=FONT_SERIF_LG,
        bg=PARCHMENT, fg=NEAR_BLACK,
    ).pack(pady=(24, 8))

    # Form
    form = tk.Frame(popup, bg=PARCHMENT, padx=36)
    form.pack(fill="x")

    org_entry = _make_field(form, "ORGANIZATION", parent.org)
    project_entry = _make_field(form, "PROJECT", parent.project)

    # PAT field with show/hide toggle
    pat_header = tk.Frame(form, bg=PARCHMENT)
    pat_header.pack(fill="x", pady=(12, 0))
    tk.Label(
        pat_header, text="PERSONAL ACCESS TOKEN", font=FONT_SANS_LABEL_BOLD,
        bg=PARCHMENT, fg=STONE_GRAY, anchor="w",
    ).pack(side="left")

    show_var = tk.BooleanVar(value=False)

    pat_entry = tk.Entry(
        form, font=FONT_SANS_MD, bg=WHITE, fg=NEAR_BLACK,
        relief="flat", highlightbackground=BORDER_WARM, highlightthickness=1,
        insertbackground=NEAR_BLACK, show="•",
    )
    pat_entry.insert(0, parent.pat)
    pat_entry.pack(fill="x", ipady=5, pady=(3, 0))

    def _toggle_show():
        pat_entry.config(show="" if show_var.get() else "•")

    tk.Checkbutton(
        pat_header, text="Show", variable=show_var,
        font=FONT_SANS_LABEL, bg=PARCHMENT, fg=OLIVE_GRAY,
        activebackground=PARCHMENT, selectcolor=WARM_SAND,
        command=_toggle_show,
    ).pack(side="right")

    # Buttons
    btn_frame = tk.Frame(popup, bg=PARCHMENT)
    btn_frame.pack(pady=(24, 24))

    def _save():
        parent.org = org_entry.get().strip() or parent.org
        parent.project = project_entry.get().strip() or parent.project
        parent.pat = pat_entry.get().strip()
        parent.default_version = parent.version_entry.get().strip()
        parent.default_platform = parent.platform_var.get()
        parent.nav_label.config(text=f"{parent.org} / {parent.project}")

        # Persist settings to the .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        lines = [
            "# Azure DevOps Personal Access Token\n",
            f"AZURE_DEVOPS_PAT={parent.pat}\n",
            "\n",
            "# Azure DevOps Organization Name (change this to your org)\n",
            f"AZURE_DEVOPS_ORG={parent.org}\n",
            "\n",
            "# Azure DevOps Project Name\n",
            f"AZURE_DEVOPS_PROJECT={parent.project}\n",
            "\n",
            "# Azure DevOps API Version\n",
            f"API_VERSION={parent.api_version}\n",
            "\n",
            "# Default search version\n",
            f"DEFAULT_VERSION={parent.default_version}\n",
            "\n",
            "# Default platform filter\n",
            f"DEFAULT_PLATFORM={parent.default_platform}\n",
        ]
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        popup.destroy()

    tk.Button(
        btn_frame, text="Save", font=FONT_SANS_BTN,
        bg=TERRACOTTA, fg=IVORY, relief="flat",
        activebackground=CORAL, cursor="hand2",
        padx=20, pady=6, command=_save,
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        btn_frame, text="Cancel", font=FONT_SANS_BTN,
        bg=WARM_SAND, fg=CHARCOAL_WARM, relief="flat",
        activebackground=BORDER_WARM, cursor="hand2",
        padx=16, pady=6, command=popup.destroy,
    ).pack(side="left")

    # Size to fit content then center on parent
    popup.update_idletasks()
    w = max(popup.winfo_reqwidth(), 440)
    h = popup.winfo_reqheight()
    px = parent.winfo_x() + (parent.winfo_width() - w) // 2
    py = parent.winfo_y() + (parent.winfo_height() - h) // 2
    popup.geometry(f"{w}x{h}+{px}+{py}")

