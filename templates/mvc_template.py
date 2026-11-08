"""MVC Template — drop-in scaffold for a model–view–controller app.

Copy this file as the starting point for a new MVC-structured app.
Fill in:
  * The `Item` dataclass — your domain object.
  * The `Repository` class — your persistence layer.
  * The `View` class — your UI.
  * The `Controller` class — wires them together.

See examples/14_mvc_pattern.py for a fully worked example.

Run:  python templates/mvc_template.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
import tkinter as tk
from tkinter import ttk, messagebox


# ===========================================================================
# MODEL — pure Python, no tkinter imports.
# ===========================================================================

@dataclass
class Item:
    """A single domain record.

    Replace this with your actual domain object.
    """
    id: int | None
    name: str
    description: str = ""


class Repository:
    """In-memory repository for Item objects.

    Replace this with your real persistence layer (SQLite, JSON file,
    REST client, etc.). The rest of the app does not change.
    """

    def __init__(self) -> None:
        """Initialize empty storage and the next-id counter."""
        self._items: list[Item] = []
        self._next_id = 1
        self._listeners: list[Callable[[list[Item]], None]] = []

    def all(self) -> list[Item]:
        """Return a copy of all items."""
        return list(self._items)

    def add(self, name: str, description: str) -> Item:
        """Add a new item and return it."""
        item = Item(id=self._next_id, name=name, description=description)
        self._next_id += 1
        self._items.append(item)
        self._notify()
        return item

    def update(self, item_id: int, name: str, description: str) -> None:
        """Update the item with the given id."""
        for i, item in enumerate(self._items):
            if item.id == item_id:
                self._items[i] = Item(id=item_id, name=name, description=description)
                self._notify()
                return

    def delete(self, item_id: int) -> None:
        """Delete the item with the given id."""
        self._items = [it for it in self._items if it.id != item_id]
        self._notify()

    # ----- Observer support -----

    def subscribe(self, listener: Callable[[list[Item]], None]) -> None:
        """Register a callback that fires after every mutation."""
        self._listeners.append(listener)
        listener(self.all())   # fire immediately so the view shows current state

    def _notify(self) -> None:
        """Notify all listeners after a mutation."""
        for listener in self._listeners:
            listener(self.all())


# ===========================================================================
# VIEW — only tkinter, no business logic.
# ===========================================================================

class View(ttk.Frame):
    """The visual representation of the application.

    Exposes callbacks the controller wires up; calls them on user actions.
    The view never calls the repository directly.
    """

    def __init__(self, master: tk.Misc) -> None:
        """Build the widget tree."""
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)

        # Controller wires these to its handlers.
        self.on_add:    Callable[[], None] = lambda: None
        self.on_update: Callable[[], None] = lambda: None
        self.on_delete: Callable[[], None] = lambda: None

        # ----- Form on the left. -----
        form = ttk.LabelFrame(self, text="Details", padding=10)
        form.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self._selected_id: int | None = None

        for row, (label, var) in enumerate([("Name:", self.name_var),
                                             ("Description:", self.desc_var)]):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="e", padx=(0, 6), pady=3)
            ttk.Entry(form, textvariable=var).grid(row=row, column=1, sticky="ew", pady=3)
        form.columnconfigure(1, weight=1)

        button_bar = ttk.Frame(form)
        button_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(button_bar, text="Add",    command=lambda: self.on_add()).pack(side="left", padx=2)
        ttk.Button(button_bar, text="Update", command=lambda: self.on_update()).pack(side="left", padx=2)
        ttk.Button(button_bar, text="Delete", command=lambda: self.on_delete()).pack(side="left", padx=2)

        # ----- Tree on the right. -----
        list_frame = ttk.LabelFrame(self, text="Items", padding=4)
        list_frame.pack(side="left", fill="both", expand=True)
        self.tree = ttk.Treeview(list_frame,
                                 columns=("id", "name", "description"),
                                 show="headings", height=10)
        self.tree.heading("id",          text="ID")
        self.tree.heading("name",        text="Name")
        self.tree.heading("description", text="Description")
        self.tree.column("id",          width=40,  anchor="center")
        self.tree.column("name",        width=140, anchor="w")
        self.tree.column("description", width=200, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=vsb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ----- View signals -----

    def _on_select(self, _event: tk.Event) -> None:
        """Populate the form from the selected row."""
        sel = self.tree.selection()
        if not sel:
            return
        # We use the database id as the iid, so we can read it directly.
        self._selected_id = int(sel[0])
        values = self.tree.item(sel[0], "values")
        self.name_var.set(values[1])
        self.desc_var.set(values[2])

    # ----- Controller → View commands -----

    def render_items(self, items: list[Item]) -> None:
        """Replace the tree contents with the given item list."""
        self.tree.delete(*self.tree.get_children())
        for item in items:
            self.tree.insert("", "end", iid=str(item.id),
                             values=(item.id, item.name, item.description))

    def clear_form(self) -> None:
        """Reset the form fields and selection."""
        self.name_var.set("")
        self.desc_var.set("")
        self._selected_id = None
        for item_id in self.tree.selection():
            self.tree.selection_remove(item_id)

    def selected_id(self) -> int | None:
        """Return the id of the currently selected row, or None."""
        return self._selected_id

    def form_values(self) -> tuple[str, str]:
        """Return (name, description) from the form."""
        return self.name_var.get().strip(), self.desc_var.get().strip()


# ===========================================================================
# CONTROLLER — wires view to model.
# ===========================================================================

class Controller:
    """Coordinates user actions on the view with mutations of the model."""

    def __init__(self, repo: Repository, view: View) -> None:
        """Connect the view's callbacks to handlers and subscribe to the repo.

        Args:
            repo: the persistence layer.
            view: the view.
        """
        self.repo = repo
        self.view = view

        self.view.on_add    = self.handle_add
        self.view.on_update = self.handle_update
        self.view.on_delete = self.handle_delete

        # Subscribe so the view refreshes automatically after every change.
        self.repo.subscribe(self.view.render_items)

    def handle_add(self) -> None:
        """Add a new item from the form."""
        name, desc = self.view.form_values()
        if not name:
            messagebox.showwarning("Missing", "Name is required.")
            return
        self.repo.add(name, desc)
        self.view.clear_form()

    def handle_update(self) -> None:
        """Update the selected item from the form."""
        item_id = self.view.selected_id()
        if item_id is None:
            messagebox.showinfo("Update", "Select an item first.")
            return
        name, desc = self.view.form_values()
        if not name:
            messagebox.showwarning("Missing", "Name is required.")
            return
        self.repo.update(item_id, name, desc)
        self.view.clear_form()

    def handle_delete(self) -> None:
        """Delete the selected item."""
        item_id = self.view.selected_id()
        if item_id is None:
            messagebox.showinfo("Delete", "Select an item first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this item?"):
            return
        self.repo.delete(item_id)
        self.view.clear_form()


# ===========================================================================
# Entry point — composition root.
# ===========================================================================

def main() -> None:
    """Construct the root window, instantiate model/view/controller, run."""
    root = tk.Tk()
    root.title("MVC Template")
    root.geometry("680x360")

    # The composition root: dependencies are wired here, nowhere else.
    repo = Repository()
    view = View(root)
    Controller(repo, view)

    # Optional: seed some data so the window isn't empty on first run.
    repo.add("First item",  "Seed data")
    repo.add("Second item", "Seed data")

    root.mainloop()


if __name__ == "__main__":
    main()
