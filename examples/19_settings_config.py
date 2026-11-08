"""Example 19 — Settings & Configuration Persistence.

Shows the recommended pattern for saving user settings:

  * Settings live in a known, OS-appropriate location.
  * Settings are stored as JSON (easy to read, easy to write).
  * Settings are saved on exit and restored on startup.
  * Window geometry and last-used directory are persisted too.

Run:  python examples/19_settings_config.py

Companion doc: 07_best_practices.md (section 7.8)
"""
from __future__ import annotations

import json
import os
import tkinter as tk
from dataclasses import dataclass, asdict, field
from pathlib import Path
from tkinter import ttk, filedialog, messagebox


# ===========================================================================
# Settings model
# ===========================================================================

@dataclass
class AppSettings:
    """Persisted application settings.

    Attributes:
        window_geometry: e.g. "800x600+100+50" from root.geometry().
        last_directory: directory used by the most recent file dialog.
        dark_mode: True if the dark theme should be applied.
        recent_files: list of recently opened file paths (most-recent first).
    """
    window_geometry: str = "640x440"
    last_directory: str = str(Path.home())
    dark_mode: bool = False
    recent_files: list[str] = field(default_factory=list)


class SettingsStore:
    """JSON-backed settings persistence.

    Args:
        path: filesystem path to the JSON file.
    """

    def __init__(self, path: Path) -> None:
        """Construct the store, remembering the file path."""
        self.path = path

    def load(self) -> AppSettings:
        """Load settings from disk, returning defaults if missing/invalid."""
        if not self.path.exists():
            return AppSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            # Filter unknown keys so we can evolve the schema gracefully.
            known = {k: v for k, v in data.items() if k in AppSettings.__dataclass_fields__}
            return AppSettings(**known)
        except (json.JSONDecodeError, TypeError):
            # Corrupt settings file → fall back to defaults.
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        """Write settings to disk as pretty-printed JSON."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(settings), indent=2),
            encoding="utf-8",
        )


# ===========================================================================
# Where to store the settings file
# ===========================================================================

def user_config_path(app_name: str) -> Path:
    """Return a sensible per-user config file location.

    Uses ~/.config on Linux, %APPDATA% on Windows, ~/Library/Application Support
    on macOS. Falls back to ~/.<app_name> if env vars are missing.
    """
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / app_name / "settings.json"
    if os.path.exists("/Library/Application Support"):
        # macOS heuristic.
        return Path.home() / "Library" / "Application Support" / app_name / "settings.json"
    # Linux / generic Unix.
    xdg = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(xdg) / app_name / "settings.json"


# ===========================================================================
# UI
# ===========================================================================

class SettingsDemo(ttk.Frame):
    """A small UI bound to an AppSettings instance."""

    def __init__(self, master: tk.Misc, settings: AppSettings,
                 store: SettingsStore) -> None:
        """Build the UI from the given settings.

        Args:
            master: parent widget.
            settings: the loaded settings object.
            store: the persistence store — used to save on exit.
        """
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)
        self.settings = settings
        self.store = store

        # ----- Top: form bound to settings via tk variables. -----
        ttk.Label(self, text="Settings Demo",
                  font=("TkDefaultFont", 14, "bold")).pack(anchor="w", pady=(0, 8))

        # Dark mode checkbox.
        self.dark_var = tk.BooleanVar(value=settings.dark_mode)
        ttk.Checkbutton(self, text="Dark mode",
                        variable=self.dark_var).pack(anchor="w", pady=2)

        # Last directory display + Browse button.
        dir_frame = ttk.Frame(self)
        dir_frame.pack(fill="x", pady=2)
        ttk.Label(dir_frame, text="Last directory:").pack(side="left")
        self.dir_var = tk.StringVar(value=settings.last_directory)
        ttk.Entry(dir_frame, textvariable=self.dir_var,
                  state="readonly").pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(dir_frame, text="Browse...",
                   command=self._browse).pack(side="left")

        # Recent files list (display only).
        ttk.Label(self, text="Recent files:").pack(anchor="w", pady=(8, 0))
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True)
        self.recent_tree = ttk.Treeview(list_frame, columns=("path",), show="headings",
                                        height=5)
        self.recent_tree.heading("path", text="Path")
        self.recent_tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(list_frame, orient="vertical",
                            command=self.recent_tree.yview)
        vsb.pack(side="right", fill="y")
        self.recent_tree.config(yscrollcommand=vsb.set)
        for path in settings.recent_files:
            self.recent_tree.insert("", "end", values=(path,))

        # Add a recent file (demo only).
        add_frame = ttk.Frame(self)
        add_frame.pack(fill="x", pady=4)
        ttk.Label(add_frame, text="Add path:").pack(side="left")
        self.add_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.add_var).pack(
            side="left", fill="x", expand=True, padx=6)
        ttk.Button(add_frame, text="Add",
                   command=self._add_recent).pack(side="left")

        # Status label.
        self.status = ttk.Label(self, text="", anchor="w")
        self.status.pack(side="bottom", fill="x", pady=(8, 0))

    # ----- Helpers -----

    def _browse(self) -> None:
        """Open a directory dialog starting from the saved last_directory."""
        path = filedialog.askdirectory(
            initialdir=self.settings.last_directory,
            title="Choose directory",
        )
        if path:
            self.dir_var.set(path)

    def _add_recent(self) -> None:
        """Add the entered path to the recent list (max 10)."""
        path = self.add_var.get().strip()
        if not path:
            return
        # Prepend and dedupe, keeping the most-recent-first order.
        recent = [path] + [p for p in self.settings.recent_files if p != path]
        self.settings.recent_files = recent[:10]
        # Refresh the visible list.
        self.recent_tree.delete(*self.recent_tree.get_children())
        for p in self.settings.recent_files:
            self.recent_tree.insert("", "end", values=(p,))
        self.add_var.set("")

    def persist_and_close(self) -> None:
        """Read the form state into settings and write them to disk.

        Called when the user closes the window.
        """
        self.settings.dark_mode = self.dark_var.get()
        self.settings.last_directory = self.dir_var.get()
        # Persist current window geometry so we can restore it next launch.
        root = self.winfo_toplevel()
        self.settings.window_geometry = root.geometry()
        try:
            self.store.save(self.settings)
            self.status.config(text="Settings saved.")
        except OSError as e:
            messagebox.showerror("Save failed", str(e))


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    """Load settings, build UI, restore geometry, start loop."""
    store = SettingsStore(user_config_path("TkinterGuideDemo"))
    settings = store.load()

    root = tk.Tk()
    root.title("Settings & Config Demo")
    # Restore the saved window geometry — fall back to default if invalid.
    try:
        root.geometry(settings.window_geometry)
    except tk.TclError:
        pass

    app = SettingsDemo(root, settings, store)

    def on_close() -> None:
        app.persist_and_close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
