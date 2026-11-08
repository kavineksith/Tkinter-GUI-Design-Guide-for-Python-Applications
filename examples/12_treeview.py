"""Example 12 — Treeview as a Table.

The ttk.Treeview is tkinter's only real "table" widget. This example
shows how to:

  * Define columns and headings.
  * Configure column widths and alignments.
  * Insert, update, delete, and select rows.
  * Sort by clicking column headers.
  * Attach a vertical scrollbar.

Run:  python examples/12_treeview.py

Companion doc: 02_widgets.md (section 2.4) and 08_advanced_topics.md (§ 8.8)
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


# Sample data — in a real app, this would come from a database or file.
SAMPLE_DATA: list[tuple[str, str, int, str]] = [
    ("Alice Johnson",   "alice@example.com",   32, "Engineering"),
    ("Bob Smith",       "bob@example.com",     28, "Sales"),
    ("Carol Davies",    "carol@example.com",   41, "Engineering"),
    ("Dan Park",        "dan@example.com",     35, "Marketing"),
    ("Eve Martinez",    "eve@example.com",     29, "Sales"),
    ("Frank Liu",       "frank@example.com",   45, "Engineering"),
    ("Grace O'Reilly",  "grace@example.com",   31, "HR"),
]


class TreeviewDemo(ttk.Frame):
    """A table of contacts with sortable columns and row selection."""

    # Column identifiers — used both as the Treeview column names
    # and as dict keys for each row's values tuple.
    COLUMNS = ("name", "email", "age", "department")

    def __init__(self, master: tk.Misc) -> None:
        """Build the tree and side panel."""
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)

        self._build_tree()
        self._build_side_panel()
        self._populate(SAMPLE_DATA)

    # ----- Construction -----

    def _build_tree(self) -> None:
        """Construct the Treeview with columns, headings, and a scrollbar."""
        container = ttk.Frame(self)
        container.pack(side="left", fill="both", expand=True)

        # show="headings" hides the tree column (the first default column).
        # For a flat table we want headings only.
        self.tree = ttk.Treeview(
            container,
            columns=self.COLUMNS,
            show="headings",
            selectmode="extended",   # allow Ctrl-click multi-select
        )
        self.tree.pack(side="left", fill="both", expand=True)

        # Headings with sort callbacks.
        for col, label in zip(self.COLUMNS,
                              ("Name", "Email", "Age", "Department")):
            self.tree.heading(
                col, text=label,
                # `command=` is evaluated at heading-click time.
                command=lambda c=col: self._sort_by(c),
            )

        # Column widths and alignments.
        self.tree.column("name",      width=180, anchor="w")
        self.tree.column("email",     width=220, anchor="w")
        self.tree.column("age",       width=60,  anchor="e")
        self.tree.column("department", width=140, anchor="w")

        # Vertical scrollbar wired in both directions.
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        # React to selection changes.
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_side_panel(self) -> None:
        """A small details panel that shows the currently selected row."""
        panel = ttk.LabelFrame(self, text="Details", padding=10)
        panel.pack(side="right", fill="y", padx=(8, 0))

        self.detail_vars = {col: tk.StringVar() for col in self.COLUMNS}
        for col in self.COLUMNS:
            ttk.Label(panel, text=col.capitalize() + ":").pack(anchor="w")
            ttk.Entry(panel, textvariable=self.detail_vars[col],
                      state="readonly", width=30).pack(anchor="w", pady=(0, 6))

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=6)
        ttk.Button(panel, text="Delete selected",
                   command=self._delete_selected).pack(fill="x")

    def _populate(self, rows: list[tuple]) -> None:
        """Insert a list of rows into the tree, replacing existing content."""
        # Clear current rows.
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            # The first positional arg "" is the parent — empty means root.
            # "end" means append at the end of the parent's children.
            self.tree.insert("", "end", values=row)

    # ----- Sorting -----

    def _sort_by(self, col: str) -> None:
        """Sort the tree by the given column, toggling direction each click.

        The sort is in-memory — no DB call. Numeric columns sort by number.
        """
        # Collect (value, item_id) pairs.
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Determine sort direction by checking a flag stored on the column.
        descending = getattr(self, f"_sort_desc_{col}", False)
        # Toggle for next time.
        setattr(self, f"_sort_desc_{col}", not descending)

        # Try numeric sort if the column looks numeric.
        try:
            items.sort(key=lambda t: int(t[0]), reverse=descending)
        except ValueError:
            items.sort(key=lambda t: t[0].lower(), reverse=descending)

        # Re-insert in sorted order by reordering, not deleting.
        for index, (_, item_id) in enumerate(items):
            self.tree.move(item_id, "", index)

    # ----- Selection -----

    def _on_select(self, _event: tk.Event) -> None:
        """Update the details panel from the first selected row."""
        selection = self.tree.selection()
        if not selection:
            for var in self.detail_vars.values():
                var.set("")
            return
        values = self.tree.item(selection[0], "values")
        for col, value in zip(self.COLUMNS, values):
            self.detail_vars[col].set(value)

    def _delete_selected(self) -> None:
        """Delete every selected row from the tree."""
        for item_id in self.tree.selection():
            self.tree.delete(item_id)
        # Clear the details panel since selection is now empty.
        for var in self.detail_vars.values():
            var.set("")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Treeview Demo")
    root.geometry("760x360")
    TreeviewDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
