"""Example 17 — Custom Composite Widget.

Shows the recommended way to build a reusable tkinter widget: subclass
ttk.Frame and add child widgets inside __init__. This "composition"
pattern is much safer than subclassing ttk.Button or ttk.Entry
directly, because ttk's C internals are not designed for subclassing.

The example defines:
  * `LabeledEntry` — a label + entry combo with validation.
  * `FormField` — a label + entry + inline-error-label widget.
And uses them in a small form to demonstrate.

Run:  python examples/17_custom_widget.py

Companion doc: 08_advanced_topics.md (section 8.1)
"""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk
from typing import Callable


class LabeledEntry(ttk.Frame):
    """A composite widget: a left-aligned label + a horizontal entry.

    Acts like a single widget from the caller's perspective. Exposes
    `get()` and `set()` to read/write its value.

    Args:
        master: parent widget.
        label: text of the left-hand label.
        label_width: width of the label column in characters.
        **kwargs: forwarded to the internal ttk.Entry.
    """

    def __init__(self, master: tk.Misc, label: str = "",
                 label_width: int = 12, **kwargs) -> None:
        """Construct the composite widget."""
        super().__init__(master)
        self._var = tk.StringVar()

        # Internal label widget, exposed via attribute for styling.
        self.label = ttk.Label(self, text=label, width=label_width, anchor="e")
        self.label.grid(row=0, column=0, sticky="e", padx=(0, 6))

        # Internal entry widget, holds the value.
        self.entry = ttk.Entry(self, textvariable=self._var, **kwargs)
        self.entry.grid(row=0, column=1, sticky="ew")

        # Let the entry column stretch when the widget resizes.
        self.columnconfigure(1, weight=1)

    # ----- Public API -----

    def get(self) -> str:
        """Return the current text value."""
        return self._var.get()

    def set(self, value: str) -> None:
        """Replace the current text value."""
        self._var.set(value)


class FormField(ttk.Frame):
    """A label + entry + inline error label, with built-in validation.

    Args:
        master: parent widget.
        label: text of the left-hand label.
        validator: callable returning (is_valid, error_message).
        **kwargs: forwarded to the internal ttk.Entry.
    """

    def __init__(self, master: tk.Misc, label: str,
                 validator: Callable[[str], tuple[bool, str]] | None = None,
                 **kwargs) -> None:
        """Construct the field and wire up validation."""
        super().__init__(master)
        self._validator = validator or (lambda v: (True, ""))

        ttk.Label(self, text=label, width=12, anchor="e").grid(
            row=0, column=0, sticky="e", padx=(0, 6))

        self._var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self._var, **kwargs)
        self.entry.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        # Error label — initially empty, turns red when validation fails.
        self.error_label = ttk.Label(self, text="", foreground="#DC2626",
                                     width=20, anchor="w")
        self.error_label.grid(row=0, column=2, sticky="w")

        # Re-validate whenever the value changes.
        self._var.trace_add("write", self._validate)

        self.columnconfigure(1, weight=1)

    # ----- Public API -----

    def get(self) -> str:
        """Return the current text value."""
        return self._var.get()

    def set(self, value: str) -> None:
        """Replace the current text value."""
        self._var.set(value)

    def is_valid(self) -> bool:
        """Return True if the current value passes validation."""
        ok, _msg = self._validator(self._var.get())
        return ok

    # ----- Internals -----

    def _validate(self, *_args) -> None:
        """Run the validator and update the error label."""
        ok, msg = self._validator(self._var.get())
        self.error_label.config(text="" if ok else msg)


# ---------------------------------------------------------------------------
# Demo form using the two custom widgets
# ---------------------------------------------------------------------------

def _validate_email(value: str) -> tuple[bool, str]:
    """Simple email regex validator (returns is_valid, error_message)."""
    if not value:
        return True, ""                # empty is OK in this demo
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
        return False, "Invalid email"
    return True, ""


def _validate_age(value: str) -> tuple[bool, str]:
    """Validate that the value is an integer between 0 and 150."""
    if not value:
        return True, ""
    try:
        n = int(value)
    except ValueError:
        return False, "Must be a number"
    if not 0 <= n <= 150:
        return False, "Out of range"
    return True, ""


class CustomWidgetDemo(ttk.Frame):
    """Build a small form using LabeledEntry and FormField."""

    def __init__(self, master: tk.Misc) -> None:
        """Construct the demo form."""
        super().__init__(master, padding=14)
        self.pack(fill="both", expand=True)

        ttk.Label(self, text="Custom Widget Demo",
                  font=("TkDefaultFont", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # LabeledEntry — simple combo, no validation.
        self.username = LabeledEntry(self, label="Username:")
        self.username.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)

        # FormField with email validator.
        self.email = FormField(self, label="Email:", validator=_validate_email)
        self.email.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)

        # FormField with age validator.
        self.age = FormField(self, label="Age:", validator=_validate_age)
        self.age.grid(row=3, column=0, columnspan=2, sticky="ew", pady=4)

        # Submit button — disabled until both fields are valid.
        self.submit = ttk.Button(self, text="Submit", command=self._on_submit)
        self.submit.grid(row=4, column=1, sticky="e", pady=(10, 0))

        # Re-check validity whenever any field changes.
        self.email.entry.bind("<KeyRelease>", lambda e: self._refresh_submit())
        self.age.entry.bind("<KeyRelease>",   lambda e: self._refresh_submit())

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def _refresh_submit(self) -> None:
        """Enable Submit only when all validators pass."""
        if self.email.is_valid() and self.age.is_valid():
            self.submit.config(state="normal")
        else:
            self.submit.config(state="disabled")

    def _on_submit(self) -> None:
        """Show a summary of what was entered."""
        from tkinter import messagebox
        messagebox.showinfo(
            "Submitted",
            f"Username: {self.username.get()!r}\n"
            f"Email:    {self.email.get()!r}\n"
            f"Age:      {self.age.get()!r}",
        )


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Custom Widget Demo")
    root.geometry("520x300")
    CustomWidgetDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
