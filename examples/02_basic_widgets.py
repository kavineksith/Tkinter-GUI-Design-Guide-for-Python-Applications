"""Example 02 — Basic Widgets Tour.

Shows the most common ttk widgets on a single screen so you can see
them at a glance: Label, Button, Entry, Checkbutton, Radiobutton,
Combobox, Spinbox, Scale, Progressbar, Separator.

Run:  python examples/02_basic_widgets.py

Companion doc: 02_widgets.md
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class WidgetsTour(ttk.Frame):
    """A scrolling showcase of the common ttk widgets.

    Each widget is paired with a label so you can see at a glance
    what each one looks like and how it's constructed.
    """

    def __init__(self, master: tk.Misc) -> None:
        """Construct the tour inside the given parent.

        Args:
            master: the parent widget (typically a `tk.Tk()` root).
        """
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)

        # ----- Variables -----
        # tk.Variable objects let us read the values of input widgets
        # elsewhere in the code without holding references to the widgets.
        self.check_var = tk.BooleanVar(value=True)
        self.radio_var = tk.StringVar(value="option2")
        self.combo_var = tk.StringVar()
        self.spin_var = tk.IntVar(value=5)
        self.scale_var = tk.DoubleVar(value=25.0)

        # ----- Build the form, row by row, with grid. -----
        # We use grid because alignment of label+widget pairs is its strength.
        self._row = 0
        self._add_label("Label:")
        ttk.Label(self, text="Static text").grid(row=self._row, column=1, sticky="w")
        self._row += 1

        self._add_label("Button:")
        ttk.Button(self, text="Click me", command=self._on_button).grid(
            row=self._row, column=1, sticky="w"
        )
        self._row += 1

        self._add_label("Entry:")
        ttk.Entry(self, textvariable=tk.StringVar()).grid(
            row=self._row, column=1, sticky="ew"
        )
        self._row += 1

        self._add_label("Checkbutton:")
        ttk.Checkbutton(self, text="Enable feature", variable=self.check_var).grid(
            row=self._row, column=1, sticky="w"
        )
        self._row += 1

        self._add_label("Radiobutton:")
        radio_frame = ttk.Frame(self)
        for value, label in (("option1", "First"), ("option2", "Second"), ("option3", "Third")):
            ttk.Radiobutton(
                radio_frame, text=label, value=value, variable=self.radio_var
            ).pack(side="left", padx=(0, 8))
        radio_frame.grid(row=self._row, column=1, sticky="w")
        self._row += 1

        self._add_label("Combobox:")
        ttk.Combobox(
            self,
            textvariable=self.combo_var,
            values=["Apple", "Banana", "Cherry"],
            state="readonly",  # readonly: user picks from the list, no free typing
        ).grid(row=self._row, column=1, sticky="ew")
        self._row += 1

        self._add_label("Spinbox:")
        ttk.Spinbox(self, from_=0, to=10, textvariable=self.spin_var).grid(
            row=self._row, column=1, sticky="w"
        )
        self._row += 1

        self._add_label("Scale:")
        ttk.Scale(self, from_=0, to=100, variable=self.scale_var, orient="horizontal").grid(
            row=self._row, column=1, sticky="ew"
        )
        self._row += 1

        self._add_label("Progressbar:")
        self.pb = ttk.Progressbar(self, maximum=100, value=25)
        self.pb.grid(row=self._row, column=1, sticky="ew")
        self._row += 1

        # A horizontal separator visually divides the form from the actions.
        ttk.Separator(self, orient="horizontal").grid(
            row=self._row, column=0, columnspan=2, sticky="ew", pady=(10, 5)
        )
        self._row += 1

        # ----- Bottom: a "Print state" button that dumps the variables. -----
        ttk.Button(self, text="Print state", command=self._print_state).grid(
            row=self._row, column=0, columnspan=2, sticky="w"
        )
        self._row += 1

        # Configure the column so the input column stretches horizontally.
        self.columnconfigure(1, weight=1)

    # ---------- Helpers ----------

    def _add_label(self, text: str) -> None:
        """Add a right-aligned label in column 0 for the current row."""
        ttk.Label(self, text=text).grid(row=self._row, column=0, sticky="e", padx=(0, 8))

    def _on_button(self) -> None:
        """Increment the progressbar by 10 each time the button is clicked."""
        self.pb["value"] = (self.pb["value"] + 10) % 100

    def _print_state(self) -> None:
        """Print the current value of every input variable to stdout."""
        print(
            f"check={self.check_var.get()} "
            f"radio={self.radio_var.get()!r} "
            f"combo={self.combo_var.get()!r} "
            f"spin={self.spin_var.get()} "
            f"scale={self.scale_var.get():.1f} "
            f"progress={self.pb['value']}"
        )


def main() -> None:
    """Create the root window and start the app."""
    root = tk.Tk()
    root.title("Basic Widgets Tour")
    root.geometry("500x460")
    WidgetsTour(root)
    root.mainloop()


if __name__ == "__main__":
    main()
