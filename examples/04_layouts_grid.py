"""Example 04 — Layout Manager: grid.

Demonstrates the grid geometry manager, which is the recommended choice
for any form-like UI with labeled input fields.

Run:  python examples/04_layouts_grid.py

Companion doc: 03_layout_managers.md (section 3.2)
"""
import tkinter as tk
from tkinter import ttk


class GridDemo(ttk.Frame):
    """A small registration form built with grid().

    Highlights:
      * Label/entry pairs aligned into rows.
      * Sticky alignment (`e` for labels, `ew` for entries).
      * A row spanning two columns for the comment field.
      * `columnconfigure(weight=1)` so the entry column stretches.
      * Buttons right-aligned at the bottom using a nested frame.
    """

    def __init__(self, master: tk.Misc) -> None:
        """Construct the form."""
        super().__init__(master, padding=14)
        self.pack(fill="both", expand=True)

        # Title row spanning both columns.
        ttk.Label(
            self, text="Registration Form", font=("TkDefaultFont", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # ----- Form fields, one per row. -----
        # Each row: a right-aligned label in column 0, an input in column 1.
        fields = [
            ("Full name:", ttk.Entry(self)),
            ("Email:", ttk.Entry(self)),
            ("Country:", ttk.Combobox(
                self,
                values=["United States", "Canada", "United Kingdom", "Australia",
                        "India", "Germany", "France", "Sri Lanka"],
                state="readonly",
            )),
        ]
        for i, (label_text, widget) in enumerate(fields, start=1):
            ttk.Label(self, text=label_text).grid(
                row=i, column=0, sticky="e", padx=(0, 8), pady=4
            )
            widget.grid(row=i, column=1, sticky="ew", pady=4)

        # ----- A multi-line comment spanning two columns. -----
        ttk.Label(self, text="Notes:").grid(
            row=len(fields) + 1, column=0, sticky="ne", padx=(0, 8), pady=4
        )
        # Wrap the Text in a Frame so we can attach a scrollbar cleanly.
        comment_frame = ttk.Frame(self)
        comment_frame.grid(row=len(fields) + 1, column=1, sticky="nsew", pady=4)
        comment = tk.Text(comment_frame, width=40, height=4, wrap="word")
        comment.pack(side="left", fill="both", expand=True)
        comment_scroll = ttk.Scrollbar(comment_frame, command=comment.yview)
        comment_scroll.pack(side="right", fill="y")
        comment.config(yscrollcommand=comment_scroll.set)

        # Let the comment row stretch vertically too.
        self.rowconfigure(len(fields) + 1, weight=1)

        # ----- Bottom button bar, right-aligned. -----
        # We use a nested frame so pack/grid mixes are confined to it.
        button_bar = ttk.Frame(self)
        button_bar.grid(row=len(fields) + 2, column=0, columnspan=2,
                        sticky="e", pady=(12, 0))
        ttk.Button(button_bar, text="Cancel").pack(side="left", padx=(0, 6))
        ttk.Button(button_bar, text="Submit",
                   command=self._on_submit).pack(side="left")

        # Configure column 1 so that it grows when the window grows.
        # Column 0 (labels) stays at its natural width.
        self.columnconfigure(1, weight=1)

    def _on_submit(self) -> None:
        """Stub: pretend to submit. In a real app, this would validate and save."""
        from tkinter import messagebox
        messagebox.showinfo("Submitted", "Form submitted (demo).")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("grid() Demo")
    root.geometry("460x360")
    GridDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
