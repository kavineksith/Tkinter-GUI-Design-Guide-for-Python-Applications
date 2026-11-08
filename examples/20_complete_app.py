"""Example 20 — Complete Application: Notepad.

A working notepad clone that brings together everything covered so far:

  * Menu bar with keyboard shortcuts and accelerator hints.
  * Toolbar with primary actions.
  * A multi-line tk.Text editor with scrollbar.
  * Status bar with line/column info and word count.
  * Open / save / save-as / new file operations.
  * Find dialog (custom Toplevel).
  * Recent files submenu.
  * Settings persistence (window size, last directory).
  * Confirmation on close if there are unsaved changes.

Run:  python examples/20_complete_app.py

Companion doc: All of the above — this is the capstone.
"""
from __future__ import annotations

import json
import os
import tkinter as tk
from dataclasses import dataclass, asdict
from pathlib import Path
from tkinter import ttk, filedialog, messagebox, simpledialog


# ===========================================================================
# Settings
# ===========================================================================

@dataclass
class NotepadSettings:
    """Persisted user settings for the notepad."""
    window_geometry: str = "720x520"
    last_directory: str = str(Path.home())
    recent_files: list[str] = None

    def __post_init__(self) -> None:
        """Default mutable fields to empty list if loaded as None."""
        if self.recent_files is None:
            self.recent_files = []


def settings_path() -> Path:
    """Return the path to the notepad's settings JSON file."""
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "TkinterGuideNotepad" / "settings.json"
    xdg = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(xdg) / "TkinterGuideNotepad" / "settings.json"


def load_settings() -> NotepadSettings:
    """Load settings from disk, falling back to defaults."""
    p = settings_path()
    if not p.exists():
        return NotepadSettings()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        known = {k: v for k, v in data.items()
                 if k in NotepadSettings.__dataclass_fields__}
        return NotepadSettings(**known)
    except (json.JSONDecodeError, TypeError):
        return NotepadSettings()


def save_settings(s: NotepadSettings) -> None:
    """Persist settings to disk."""
    p = settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(s), indent=2), encoding="utf-8")


# ===========================================================================
# Find dialog
# ===========================================================================

class FindDialog(tk.Toplevel):
    """A small modal dialog for finding text in the editor."""

    def __init__(self, master: tk.Misc, text_widget: tk.Text) -> None:
        """Construct and run the dialog.

        Args:
            master: the parent window.
            text_widget: the Text widget to search in.
        """
        super().__init__(master)
        self.title("Find")
        self.text_widget = text_widget
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Find:").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        # Re-run the search on every keystroke.
        self.search_var.trace_add("write", self._find_next)
        ttk.Entry(frame, textvariable=self.search_var, width=30).grid(
            row=0, column=1, padx=(4, 0))
        ttk.Button(frame, text="Find next", command=self._find_next).grid(
            row=0, column=2, padx=(4, 0))
        ttk.Button(frame, text="Close", command=self.destroy).grid(
            row=1, column=2, sticky="e", pady=(6, 0))

        self.last_start: str = "1.0"   # last search start index
        self.bind("<Escape>", lambda e: self.destroy())

    def _find_next(self, *_args) -> None:
        """Highlight the next occurrence of the search text."""
        needle = self.search_var.get()
        if not needle:
            return
        # search returns the index of the next match, or empty string.
        pos = self.text_widget.search(needle, self.last_start, stopindex="end",
                                       nocase=True)
        if not pos:
            # Wrap around.
            pos = self.text_widget.search(needle, "1.0", stopindex="end",
                                          nocase=True)
        if pos:
            # Remove previous selection highlight, then add the new one.
            self.text_widget.tag_remove("sel", "1.0", "end")
            end = f"{pos}+{len(needle)}c"
            self.text_widget.tag_add("sel", pos, end)
            self.text_widget.mark_set("insert", pos)
            self.text_widget.see(pos)
            # Next search starts after this match.
            self.last_start = end


# ===========================================================================
# Main application
# ===========================================================================

class NotepadApp:
    """The complete notepad application.

    Owns the root window, the editor, the menu, and the file operations.
    Uses an Application Class architecture (see 06_architecture_patterns.md).
    """

    def __init__(self, root: tk.Tk) -> None:
        """Build the application chrome and load settings."""
        self.root = root
        self.root.title("Notepad — Untitled")
        self.settings = load_settings()
        try:
            self.root.geometry(self.settings.window_geometry)
        except tk.TclError:
            pass

        # Document state.
        self.current_path: str | None = None
        self.is_dirty = False

        self._build_widgets()
        self._build_menubar()
        self._build_toolbar()
        self._build_statusbar()
        self._refresh_recent_menu()
        self._update_status()

        # Mark as dirty whenever the user edits the text.
        self.text.bind("<<Modified>>", self._on_modified)
        # Update status bar on cursor movement.
        self.text.bind("<<CursorRow>>", self._update_status)  # custom event
        self.text.bind("<KeyRelease>", self._update_status)

        # Persist settings on close.
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----- Construction -----

    def _build_widgets(self) -> None:
        """Create the central text widget and its scrollbar."""
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Undo=True enables Ctrl+Z / Ctrl+Y for the text widget.
        self.text = tk.Text(container, wrap="word", undo=True,
                            font=("Consolas", 11), padx=8, pady=6)
        self.text.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(container, orient="vertical", command=self.text.yview)
        vsb.pack(side="right", fill="y")
        self.text.config(yscrollcommand=vsb.set)

    def _build_menubar(self) -> None:
        """Construct the top menu bar with File / Edit / Help."""
        self.root.option_add("*tearOff", False)
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu — built once; recent submenu is rebuilt on demand.
        self.file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=self.file_menu, underline=0)
        self.file_menu.add_command(label="New",  underline=0, accelerator="Ctrl+N",
                                    command=self.file_new)
        self.file_menu.add_command(label="Open...", underline=0, accelerator="Ctrl+O",
                                    command=self.file_open)
        self.file_menu.add_command(label="Save",  underline=0, accelerator="Ctrl+S",
                                    command=self.file_save)
        self.file_menu.add_command(label="Save As...", underline=1,
                                    command=self.file_save_as)
        self.file_menu.add_separator()
        # Placeholder for "Recent files" submenu — created empty,
        # populated by _refresh_recent_menu().
        self.recent_menu = tk.Menu(self.file_menu)
        self.file_menu.add_cascade(label="Recent files", menu=self.recent_menu)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", underline=1, command=self._on_close)

        # Edit menu.
        edit_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Edit", menu=edit_menu, underline=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z",
                              command=lambda: self.text.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y",
                              command=lambda: self.text.event_generate("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut",   accelerator="Ctrl+X",
                              command=lambda: self.text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy",  accelerator="Ctrl+C",
                              command=lambda: self.text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V",
                              command=lambda: self.text.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", accelerator="Ctrl+F",
                              command=self.edit_find)

        # Help menu.
        help_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Help", menu=help_menu, underline=0)
        help_menu.add_command(label="About", command=self.help_about)

        # Bindings.
        self.root.bind_all("<Control-n>", lambda e: self.file_new())
        self.root.bind_all("<Control-o>", lambda e: self.file_open())
        self.root.bind_all("<Control-s>", lambda e: self.file_save())
        self.root.bind_all("<Control-f>", lambda e: self.edit_find())

    def _build_toolbar(self) -> None:
        """Construct the horizontal toolbar below the menu bar."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side="top", fill="x")
        ttk.Button(toolbar, text="New",  command=self.file_new).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Open", command=self.file_open).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Save", command=self.file_save).pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(toolbar, text="Find", command=self.edit_find).pack(side="left", padx=2)

    def _build_statusbar(self) -> None:
        """A status bar at the bottom showing cursor position and word count."""
        self.status = ttk.Frame(self.root, relief="sunken")
        self.status.pack(side="bottom", fill="x")
        self.position_label = ttk.Label(self.status, text="Ln 1, Col 1")
        self.position_label.pack(side="left", padx=8, pady=2)
        self.word_label = ttk.Label(self.status, text="0 words")
        self.word_label.pack(side="left", padx=12)
        self.path_label = ttk.Label(self.status, text="(untitled)")
        self.path_label.pack(side="right", padx=8)

    # ----- File operations -----

    def _confirm_discard(self) -> bool:
        """If there are unsaved changes, ask the user how to proceed.

        Returns True if it's OK to proceed (discard or save first),
        False if the user cancelled.
        """
        if not self.is_dirty:
            return True
        choice = messagebox.askyesnocancel(
            "Unsaved changes",
            "Save changes before continuing?")
        if choice is None:           # Cancel
            return False
        if choice is True:           # Yes → save first
            return self.file_save()
        # choice is False → No, don't save → proceed anyway
        return True

    def file_new(self) -> None:
        """Clear the editor and start a new document."""
        if not self._confirm_discard():
            return
        self.text.delete("1.0", "end")
        self.text.edit_reset()      # clear undo stack
        self.current_path = None
        self._set_dirty(False)
        self.root.title("Notepad — Untitled")
        self.path_label.config(text="(untitled)")

    def file_open(self) -> None:
        """Open a file dialog and load the chosen file."""
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            initialdir=self.settings.last_directory,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror("Open failed", str(e))
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_reset()
        self.current_path = path
        self._set_dirty(False)
        self.root.title(f"Notepad — {os.path.basename(path)}")
        self.path_label.config(text=path)
        self.settings.last_directory = os.path.dirname(path)
        self._add_recent(path)

    def file_save(self) -> bool:
        """Save the current document to disk. Returns True on success."""
        if self.current_path is None:
            return self.file_save_as()
        try:
            with open(self.current_path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end-1c"))
        except OSError as e:
            messagebox.showerror("Save failed", str(e))
            return False
        self._set_dirty(False)
        return True

    def file_save_as(self) -> bool:
        """Prompt for a path and save the document there."""
        path = filedialog.asksaveasfilename(
            initialdir=self.settings.last_directory,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return False
        self.current_path = path
        # Reuse file_save() to do the actual write.
        result = self.file_save()
        if result:
            self.root.title(f"Notepad — {os.path.basename(path)}")
            self.path_label.config(text=path)
            self.settings.last_directory = os.path.dirname(path)
            self._add_recent(path)
        return result

    def _add_recent(self, path: str) -> None:
        """Add `path` to the top of the recent files list (max 10)."""
        recent = [path] + [p for p in self.settings.recent_files if p != path]
        self.settings.recent_files = recent[:10]
        self._refresh_recent_menu()

    def _refresh_recent_menu(self) -> None:
        """Rebuild the Recent files submenu from settings."""
        self.recent_menu.delete(0, "end")
        for path in self.settings.recent_files:
            # Use a default argument to capture the current value of `path`.
            self.recent_menu.add_command(
                label=path, command=lambda p=path: self._open_recent(p))
        if not self.settings.recent_files:
            self.recent_menu.add_command(label="(none)", state="disabled")

    def _open_recent(self, path: str) -> None:
        """Open a file from the Recent files submenu."""
        if not self._confirm_discard():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror("Open failed", str(e))
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_reset()
        self.current_path = path
        self._set_dirty(False)
        self.root.title(f"Notepad — {os.path.basename(path)}")
        self.path_label.config(text=path)

    # ----- Edit operations -----

    def edit_find(self) -> None:
        """Open the Find dialog."""
        FindDialog(self.root, self.text)

    # ----- Help -----

    def help_about(self) -> None:
        """Show the About dialog."""
        messagebox.showinfo(
            "About Notepad",
            "Notepad — capstone example\n"
            "Part of the Tkinter GUI Design Guide.",
            parent=self.root,
        )

    # ----- Status & dirty tracking -----

    def _set_dirty(self, dirty: bool) -> None:
        """Mark the document as modified (or not)."""
        self.is_dirty = dirty
        # The text widget's "modified" flag drives the <<Modified>> event.
        try:
            self.text.edit_modified(dirty)
        except tk.TclError:
            pass

    def _on_modified(self, _event: tk.Event) -> None:
        """Sync self.is_dirty from the text widget's modified flag."""
        self.is_dirty = self.text.edit_modified()
        title = self.root.title()
        prefix = "*" if self.is_dirty else ""
        # If title doesn't already start with *, add/remove the marker.
        if title.startswith("*"):
            title = title[1:]
        self.root.title(prefix + title)

    def _update_status(self, _event: tk.Event | None = None) -> None:
        """Refresh the cursor position and word count in the status bar."""
        # cursor position
        index = self.text.index("insert")
        line, col = index.split(".")
        self.position_label.config(text=f"Ln {int(line)}, Col {int(col) + 1}")
        # word count
        text = self.text.get("1.0", "end-1c")
        word_count = len(text.split())
        self.word_label.config(text=f"{word_count} words")

    # ----- Close -----

    def _on_close(self) -> None:
        """Confirm save, persist settings, then quit."""
        if not self._confirm_discard():
            return
        self.settings.window_geometry = self.root.geometry()
        try:
            save_settings(self.settings)
        except OSError:
            pass  # settings save failure should not block exit
        self.root.destroy()


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    """Construct the root and start the application."""
    root = tk.Tk()
    root.title("Notepad")
    NotepadApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
