"""Example 10 — File Dialogs.

Demonstrates the built-in file dialogs and file-type filtering,
plus the recommended pattern of remembering the last-used directory.

Run:  python examples/10_file_dialogs.py

Companion doc: 02_widgets.md (section 2.5)
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class FileDialogDemo(ttk.Frame):
    """A panel with buttons for each file dialog type."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the panel."""
        super().__init__(master, padding=16)
        self.pack(fill="both", expand=True)

        # The "last used directory" — we persist this across dialogs
        # so the next one opens in the same place the user just was.
        # In a real app, persist this to disk on exit (see example 19).
        self.last_dir = os.path.expanduser("~")

        # ----- Build one button per dialog type. -----
        actions = [
            ("Open single file",          self._open_one),
            ("Open multiple files",        self._open_many),
            ("Save as...",                 self._save_as),
            ("Choose directory",           self._choose_dir),
        ]
        for label, handler in actions:
            ttk.Button(self, text=label, command=handler).pack(
                fill="x", pady=3)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        # Result display.
        ttk.Label(self, text="Result:", font=("TkDefaultFont", 10, "bold")).pack(
            anchor="w")
        self.result_text = tk.Text(self, height=6, wrap="word",
                                   state="disabled")
        self.result_text.pack(fill="both", expand=True)

    # ----- Helpers -----

    def _set_result(self, message: str) -> None:
        """Replace the contents of the result text box."""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", message)
        self.result_text.configure(state="disabled")

    def _remember_dir(self, path: str) -> None:
        """Update last_dir if `path` points to a real directory."""
        if path and os.path.isdir(path):
            self.last_dir = path
        elif path and os.path.isfile(path):
            self.last_dir = os.path.dirname(path)

    # ----- Dialog handlers -----

    def _open_one(self) -> None:
        """askopenfilename — single file."""
        path = filedialog.askopenfilename(
            title="Open file",
            initialdir=self.last_dir,
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("Images", "*.png *.jpg *.gif"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._remember_dir(path)
            self._set_result(f"Opened:\n{path}")

    def _open_many(self) -> None:
        """askopenfilenames — multiple files at once (returns a tuple)."""
        paths = filedialog.askopenfilenames(
            title="Open multiple files",
            initialdir=self.last_dir,
            filetypes=[("All files", "*.*")],
        )
        if paths:
            self._remember_dir(paths[0])
            self._set_result(f"Opened {len(paths)} files:\n" + "\n".join(paths))

    def _save_as(self) -> None:
        """asksaveasfilename — choose a destination path (does NOT write)."""
        path = filedialog.asksaveasfilename(
            title="Save as...",
            initialdir=self.last_dir,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self._remember_dir(path)
            # In a real app you would now open(path, 'w') and write content.
            # Here we just simulate by writing a one-line file.
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("Saved by File Dialog Demo.\n")
                self._set_result(f"Saved to:\n{path}")
            except OSError as e:
                messagebox.showerror("Save failed", str(e))

    def _choose_dir(self) -> None:
        """askdirectory — pick a folder."""
        path = filedialog.askdirectory(
            title="Choose directory",
            initialdir=self.last_dir,
        )
        if path:
            self._remember_dir(path)
            self._set_result(f"Directory chosen:\n{path}")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("File Dialogs Demo")
    root.geometry("480x360")
    FileDialogDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
