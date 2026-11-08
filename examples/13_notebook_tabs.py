"""Example 13 — Notebook (Tabbed Interface).

ttk.Notebook is the standard way to organize multiple panels in one
window — the classic "tabs at the top" interface. This example shows
how to:

  * Add and remove tabs.
  * React to tab changes with <<NotebookTabChanged>>.
  * Disable a tab until its prerequisites are met.
  * Embed real content (a form, a treeview, a log) in each tab.

Run:  python examples/13_notebook_tabs.py

Companion doc: 02_widgets.md (section 2.2) and 05_event_handling.md
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox


class NotebookDemo(ttk.Frame):
    """A three-tab notebook: Settings, Data, Log."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the notebook and its three tabs."""
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)

        # ----- Notebook construction. -----
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        # Each tab is a Frame. The text shown on the tab is passed to add().
        self.tab_settings = self._build_settings_tab()
        self.tab_data     = self._build_data_tab()
        self.tab_log      = self._build_log_tab()

        self.nb.add(self.tab_settings, text="Settings", underline=0)
        self.nb.add(self.tab_data,     text="Data",     underline=0)
        # The third tab is disabled — we'll enable it after the user
        # enters a value in Settings, demonstrating the gating pattern.
        self.nb.add(self.tab_log,      text="Log",      underline=0,
                    state="disabled")

        # React to tab switches — update a status line.
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Status bar at the bottom shows which tab is active.
        self.status = ttk.Label(self, text="Active: Settings", relief="sunken",
                                anchor="w", padding=(8, 4))
        self.status.pack(side="bottom", fill="x", pady=(8, 0))

    # ----- Tab builders -----

    def _build_settings_tab(self) -> ttk.Frame:
        """The Settings tab: a small form whose state unlocks the Log tab."""
        tab = ttk.Frame(self.nb, padding=12)
        ttk.Label(tab, text="Settings",
                  font=("TkDefaultFont", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(tab, text="Username:").grid(row=1, column=0, sticky="e", padx=(0, 6))
        self.user_var = tk.StringVar()
        # trace_add fires the callback every time the variable changes.
        self.user_var.trace_add("write", self._on_user_change)
        ttk.Entry(tab, textvariable=self.user_var).grid(
            row=1, column=1, sticky="ew", pady=2)

        ttk.Label(tab, text="Notify me:").grid(row=2, column=0, sticky="e", padx=(0, 6))
        self.notify_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, variable=self.notify_var).grid(
            row=2, column=1, sticky="w", pady=2)

        tab.columnconfigure(1, weight=1)
        return tab

    def _build_data_tab(self) -> ttk.Frame:
        """The Data tab: a small Treeview of sample rows."""
        tab = ttk.Frame(self.nb, padding=12)
        tree = ttk.Treeview(tab, columns=("name", "value"), show="headings",
                            height=6)
        tree.heading("name",  text="Name")
        tree.heading("value", text="Value")
        tree.column("name",  width=160, anchor="w")
        tree.column("value", width=160, anchor="e")
        tree.pack(fill="both", expand=True)
        for n, v in [("alpha", "1"), ("beta", "2"), ("gamma", "3")]:
            tree.insert("", "end", values=(n, v))
        return tab

    def _build_log_tab(self) -> ttk.Frame:
        """The Log tab: a Text widget that we can write to."""
        tab = ttk.Frame(self.nb, padding=12)
        self.log_text = tk.Text(tab, width=60, height=10, wrap="word",
                                state="disabled")
        self.log_text.pack(fill="both", expand=True)
        ttk.Button(tab, text="Add log line",
                   command=lambda: self._append_log("Hello from the Log tab.")).pack(
            anchor="w", pady=(6, 0))
        return tab

    # ----- Notebook event handling -----

    def _on_tab_changed(self, _event: tk.Event) -> None:
        """Update the status bar text to reflect the new active tab."""
        current = self.nb.select()                    # returns the tab's widget id
        if not current:
            return
        # nb.tab(tab_id, 'text') returns the visible text on the tab.
        text = self.nb.tab(current, "text")
        self.status.config(text=f"Active: {text}")

    def _on_user_change(self, *_args) -> None:
        """Enable the Log tab as soon as the user types a username.

        This is the classic 'enable-when-form-valid' pattern.
        """
        if self.user_var.get().strip():
            self.nb.tab(self.tab_log, state="normal")
        else:
            # Disable and switch away if currently on the Log tab.
            self.nb.tab(self.tab_log, state="disabled")
            if self.nb.select() == str(self.tab_log):
                self.nb.select(self.tab_settings)

    def _append_log(self, message: str) -> None:
        """Append a line to the read-only log Text widget."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Notebook (Tabs) Demo")
    root.geometry("560x380")
    NotebookDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
