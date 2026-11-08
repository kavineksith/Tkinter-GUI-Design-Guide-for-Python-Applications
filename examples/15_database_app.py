"""Example 15 — Database-backed App (SQLite + ttk.Treeview).

A small CRUD app that persists contacts to a local SQLite database
file. Demonstrates:

  * SQLite via the stdlib `sqlite3` module (no external dependencies).
  * Repository pattern — all DB access lives in one class.
  * Loading data into a Treeview.
  * Insert / update / delete with auto-refresh.

Run:  python examples/15_database_app.py

Companion doc: 06_architecture_patterns.md (section 6.8)

Note: the database file is created next to this script as `contacts.db`.
"""
from __future__ import annotations

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass
from pathlib import Path


# ===========================================================================
# Model + Repository
# ===========================================================================

@dataclass
class Contact:
    """A single contact row."""
    id: int | None
    name: str
    email: str
    phone: str


class ContactRepository:
    """SQLite-backed contact storage.

    All SQL lives here. The rest of the app deals in Contact objects.
    """

    def __init__(self, db_path: str) -> None:
        """Open (or create) the database and ensure the schema exists.

        Args:
            db_path: filesystem path to the SQLite file.
        """
        self.conn = sqlite3.connect(db_path)
        # Row factory lets us access columns by name.
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        """Create the contacts table if it doesn't exist."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
            """
        )
        self.conn.commit()

    def all(self) -> list[Contact]:
        """Return every contact, ordered by name."""
        rows = self.conn.execute(
            "SELECT id, name, email, phone FROM contacts ORDER BY name"
        ).fetchall()
        return [Contact(r["id"], r["name"], r["email"], r["phone"]) for r in rows]

    def add(self, name: str, email: str, phone: str) -> None:
        """Insert a new contact."""
        self.conn.execute(
            "INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone),
        )
        self.conn.commit()

    def update(self, contact_id: int, name: str, email: str, phone: str) -> None:
        """Update an existing contact by id."""
        self.conn.execute(
            "UPDATE contacts SET name=?, email=?, phone=? WHERE id=?",
            (name, email, phone, contact_id),
        )
        self.conn.commit()

    def delete(self, contact_id: int) -> None:
        """Delete a contact by id."""
        self.conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
        self.conn.commit()

    def close(self) -> None:
        """Close the underlying connection."""
        self.conn.close()


# ===========================================================================
# View + Controller (kept in one class for brevity — see example 14 for
# the fully separated version).
# ===========================================================================

class ContactApp(ttk.Frame):
    """A simple CRUD UI bound to a ContactRepository."""

    def __init__(self, master: tk.Misc, repo: ContactRepository) -> None:
        """Build the UI and load initial data.

        Args:
            master: parent widget.
            repo: the database repository.
        """
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)
        self.repo = repo
        self._selected_id: int | None = None

        # ----- Form on the left. -----
        form = ttk.LabelFrame(self, text="Contact details", padding=10)
        form.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.name_var  = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        for row, (label, var) in enumerate([
            ("Name:",  self.name_var),
            ("Email:", self.email_var),
            ("Phone:", self.phone_var),
        ]):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="e", padx=(0, 6), pady=3)
            ttk.Entry(form, textvariable=var).grid(row=row, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)

        button_bar = ttk.Frame(form)
        button_bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(button_bar, text="New",   command=self._new).pack(side="left", padx=2)
        ttk.Button(button_bar, text="Save",  command=self._save).pack(side="left", padx=2)
        ttk.Button(button_bar, text="Delete",command=self._delete).pack(side="left", padx=2)

        # ----- Treeview on the right. -----
        list_frame = ttk.LabelFrame(self, text="Contacts", padding=4)
        list_frame.pack(side="left", fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("name", "email", "phone"),
                                 show="headings", height=10)
        self.tree.heading("name",  text="Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("phone", text="Phone")
        self.tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=vsb.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Initial data load.
        self._refresh()

    # ----- Helpers -----

    def _refresh(self) -> None:
        """Reload all contacts from the database and refill the tree."""
        self.tree.delete(*self.tree.get_children())
        for c in self.repo.all():
            # Store the database id in the Treeview item via the iid.
            self.tree.insert("", "end", iid=str(c.id),
                             values=(c.name, c.email, c.phone))

    def _clear_form(self) -> None:
        """Reset the form fields and the selection."""
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self._selected_id = None
        self.tree.selection_remove(*self.tree.selection())

    # ----- Event handlers -----

    def _on_select(self, _event: tk.Event) -> None:
        """Load the selected row into the form."""
        sel = self.tree.selection()
        if not sel:
            return
        # We used the database id as the item iid, so we can read it directly.
        self._selected_id = int(sel[0])
        values = self.tree.item(sel[0], "values")
        self.name_var.set(values[0])
        self.email_var.set(values[1])
        self.phone_var.set(values[2])

    def _new(self) -> None:
        """Start a new contact entry."""
        self._clear_form()

    def _save(self) -> None:
        """Insert a new contact or update the selected one."""
        name  = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        if not name:
            messagebox.showwarning("Missing", "Name is required.")
            return
        try:
            if self._selected_id is None:
                self.repo.add(name, email, phone)
            else:
                self.repo.update(self._selected_id, name, email, phone)
        except sqlite3.Error as e:
            messagebox.showerror("Database error", str(e))
            return
        self._clear_form()
        self._refresh()

    def _delete(self) -> None:
        """Delete the selected contact."""
        if self._selected_id is None:
            messagebox.showinfo("Delete", "Select a contact first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this contact?"):
            return
        try:
            self.repo.delete(self._selected_id)
        except sqlite3.Error as e:
            messagebox.showerror("Database error", str(e))
            return
        self._clear_form()
        self._refresh()


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    """Build the window and the database, then start the loop."""
    # Place the database next to this script for demo purposes.
    db_path = str(Path(__file__).parent / "contacts.db")
    repo = ContactRepository(db_path)

    root = tk.Tk()
    root.title("SQLite Contact Manager")
    root.geometry("680x380")

    def on_close() -> None:
        """Ensure the database connection is closed when the window closes."""
        repo.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    ContactApp(root, repo)
    root.mainloop()


if __name__ == "__main__":
    main()
