"""Example 14 — Model–View–Controller Pattern.

A small Contact Manager app that demonstrates MVC separation:
  * Model: `ContactBook` — pure Python, no tkinter. Unit-testable.
  * View:  `ContactView`  — builds widgets, reads/writes only display state.
  * Controller: `ContactController` — handles user actions, calls model,
                refreshes view.

Run:  python examples/14_mvc_pattern.py

Companion doc: 06_architecture_patterns.md (section 6.3)

See also: templates/mvc_template.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
import tkinter as tk
from tkinter import ttk, messagebox


# ===========================================================================
# MODEL — pure Python, no tkinter imports.
# ===========================================================================

@dataclass
class Contact:
    """A single contact record."""
    name: str
    email: str
    phone: str = ""


class ContactBook:
    """In-memory contact storage. Pure Python — no tkinter dependency.

    Exposes the operations the controller needs and an observer
    callback so the view can refresh whenever the data changes.
    """

    def __init__(self) -> None:
        """Initialize an empty contact list."""
        self._contacts: list[Contact] = []
        # The observer callback; called with the new list after every change.
        self._on_change: callable | None = None

    # ----- CRUD -----
    def add(self, contact: Contact) -> None:
        """Add a contact to the end of the list."""
        self._contacts.append(contact)
        self._notify()

    def update(self, index: int, contact: Contact) -> None:
        """Replace the contact at `index` with the given one."""
        if 0 <= index < len(self._contacts):
            self._contacts[index] = contact
            self._notify()

    def remove(self, index: int) -> None:
        """Delete the contact at `index`."""
        if 0 <= index < len(self._contacts):
            del self._contacts[index]
            self._notify()

    def all(self) -> list[Contact]:
        """Return a copy of the contact list."""
        return list(self._contacts)

    # ----- Observer -----
    def subscribe(self, callback) -> None:
        """Register a single observer called after every mutation."""
        self._on_change = callback
        # Fire immediately so the view shows the current state.
        callback(self.all())

    def _notify(self) -> None:
        """Invoke the observer if one is registered."""
        if self._on_change is not None:
            self._on_change(self.all())


# ===========================================================================
# VIEW — only tkinter, no business logic.
# ===========================================================================

class ContactView(ttk.Frame):
    """The visual representation of the contact manager.

    The view exposes methods that the controller can call to update
    the display, and routes user actions back to the controller via
    callbacks. The view never touches the model directly.
    """

    def __init__(self, master: tk.Misc) -> None:
        """Build the widget tree."""
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)

        # Callbacks filled in by the controller. Using None-sentinels
        # lets us call them safely even before the controller wires them.
        self.on_add:    callable = lambda: None
        self.on_update: callable = lambda: None
        self.on_delete: callable = lambda: None

        # Input variables.
        self.name_var  = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self._selected_index: int | None = None

        # Form on the left.
        form = ttk.LabelFrame(self, text="Contact", padding=10)
        form.pack(side="left", fill="both", expand=True, padx=(0, 8))

        for row, (label, var) in enumerate([
            ("Name:",  self.name_var),
            ("Email:", self.email_var),
            ("Phone:", self.phone_var),
        ]):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="e", padx=(0, 6), pady=2)
            ttk.Entry(form, textvariable=var).grid(row=row, column=1, sticky="ew", pady=2)
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(form)
        buttons.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(buttons, text="Add",    command=lambda: self.on_add()).pack(side="left", padx=2)
        ttk.Button(buttons, text="Update", command=lambda: self.on_update()).pack(side="left", padx=2)
        ttk.Button(buttons, text="Delete", command=lambda: self.on_delete()).pack(side="left", padx=2)

        # List on the right.
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
        # When the user selects a row, populate the form.
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ----- View → Controller signals -----

    def _on_select(self, _event: tk.Event) -> None:
        """Populate the form fields from the selected row.

        Stores the selected index so the controller knows which row
        an "Update" or "Delete" applies to.
        """
        selection = self.tree.selection()
        if not selection:
            return
        # The Treeview item's text() carries the index as a string
        # (see render_contacts below — we set it explicitly).
        item_id = selection[0]
        # We store the index in a hidden attribute of the item via tags
        # is overkill; here we use the simpler approach of mapping item
        # id back to the index via the row order in the tree.
        children = self.tree.get_children("")
        self._selected_index = children.index(item_id)

        values = self.tree.item(item_id, "values")
        self.name_var.set(values[0])
        self.email_var.set(values[1])
        self.phone_var.set(values[2])

    # ----- Controller → View commands -----

    def render_contacts(self, contacts: list[Contact]) -> None:
        """Replace the tree contents with the given contact list."""
        # Preserve selection across refresh if possible.
        previous_index = self._selected_index

        self.tree.delete(*self.tree.get_children())
        for contact in contacts:
            self.tree.insert("", "end",
                             values=(contact.name, contact.email, contact.phone))

        # Re-select the previously selected index if it still exists.
        children = self.tree.get_children("")
        if previous_index is not None and 0 <= previous_index < len(children):
            self.tree.selection_set(children[previous_index])

    def get_form_values(self) -> Contact:
        """Read the form fields into a Contact object."""
        return Contact(
            name=self.name_var.get().strip(),
            email=self.email_var.get().strip(),
            phone=self.phone_var.get().strip(),
        )

    def clear_form(self) -> None:
        """Reset all input fields and the selection."""
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self._selected_index = None
        for item_id in self.tree.selection():
            self.tree.selection_remove(item_id)

    def selected_index(self) -> int | None:
        """Return the index of the currently selected row, or None."""
        return self._selected_index


# ===========================================================================
# CONTROLLER — wires view to model.
# ===========================================================================

class ContactController:
    """Coordinates user actions on the view with mutations of the model."""

    def __init__(self, model: ContactBook, view: ContactView) -> None:
        """Connect the view's signals to handlers and subscribe to the model.

        Args:
            model: the contact book (data source).
            view:  the view (display + input).
        """
        self.model = model
        self.view = view

        # Wire view signals.
        self.view.on_add    = self.handle_add
        self.view.on_update = self.handle_update
        self.view.on_delete = self.handle_delete

        # Subscribe to model changes so the view refreshes automatically.
        self.model.subscribe(self.view.render_contacts)

    def handle_add(self) -> None:
        """Add the form contents as a new contact."""
        contact = self.view.get_form_values()
        if not contact.name:
            messagebox.showwarning("Missing", "Name is required.")
            return
        self.model.add(contact)
        self.view.clear_form()

    def handle_update(self) -> None:
        """Update the selected contact with the form contents."""
        index = self.view.selected_index()
        if index is None:
            messagebox.showinfo("Update", "Select a contact first.")
            return
        self.model.update(index, self.view.get_form_values())
        self.view.clear_form()

    def handle_delete(self) -> None:
        """Delete the selected contact."""
        index = self.view.selected_index()
        if index is None:
            messagebox.showinfo("Delete", "Select a contact first.")
            return
        self.model.remove(index)
        self.view.clear_form()


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    """Build the root window and wire everything together."""
    root = tk.Tk()
    root.title("MVC Contact Manager")
    root.geometry("680x360")

    # The composition root: instantiate model, view, controller.
    model = ContactBook()
    view = ContactView(root)
    ContactController(model, view)

    # Seed a couple of contacts so the window isn't empty on first run.
    model.add(Contact("Alice", "alice@example.com", "555-0100"))
    model.add(Contact("Bob",   "bob@example.com",   "555-0101"))

    root.mainloop()


if __name__ == "__main__":
    main()
