"""Example 03 — Layout Manager: pack.

Demonstrates the pack geometry manager, which arranges widgets by
stacking them against one of the four edges of their parent.

Run:  python examples/03_layouts_pack.py

Companion doc: 03_layout_managers.md (section 3.1)
"""
import tkinter as tk
from tkinter import ttk


class PackDemo(ttk.Frame):
    """A classic top-bar / center / bottom-bar layout built with pack()."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the layout inside `master`.

        Layout overview::

            +-----------------------------------+
            |  Toolbar (top, fill x)            |
            +-----------------------------------+
            |                |                  |
            |   Sidebar      |   Main area      |
            |   (left, fill  |   (top, expand,  |
            |    y)          |    fill both)     |
            |                |                  |
            +-----------------------------------+
            |  Status bar (bottom, fill x)     |
            +-----------------------------------+

        Note: pack() is used at the outer level. Inside the main area
        we use pack() too — never mix managers within the same parent.
        """
        super().__init__(master, padding=8)
        self.pack(fill="both", expand=True)

        # --- Toolbar at the top, full width. ---
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="New").pack(side="left", padx=(0, 4))
        ttk.Button(toolbar, text="Open").pack(side="left", padx=(0, 4))
        ttk.Button(toolbar, text="Save").pack(side="left", padx=(0, 4))
        # Right-aligned button — packed first to the right side, then the
        # others to the left, so the right button stays on the right.
        ttk.Button(toolbar, text="Help").pack(side="right")

        # --- Status bar at the bottom. Packed BEFORE the middle so that
        #     the middle's `expand=True` doesn't push the status bar off-screen.
        #     pack() processes calls in order; bottom claims its slot first.
        status = ttk.Frame(self, relief="sunken")
        status.pack(side="bottom", fill="x")
        ttk.Label(status, text="Ready.").pack(side="left", padx=6, pady=3)
        ttk.Sizegrip(status).pack(side="right")  # resizable corner handle

        # --- Middle row: sidebar + main. ---
        middle = ttk.Frame(self)
        middle.pack(side="top", fill="both", expand=True)

        # Sidebar on the left, full height, fixed width.
        sidebar = ttk.Frame(middle, width=140, relief="groove", padding=6)
        sidebar.pack(side="left", fill="y", padx=(0, 8))
        # pack_propagate(False) tells the frame: keep your requested width
        # even though your contents are narrower.
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="Navigation", font=("TkDefaultFont", 11, "bold")).pack(
            anchor="w", pady=(0, 6)
        )
        for item in ("Inbox", "Drafts", "Sent", "Trash"):
            ttk.Button(sidebar, text=item).pack(fill="x", pady=2)

        # Main area on the right, fills the rest.
        main_area = ttk.Frame(middle, relief="groove", padding=12)
        main_area.pack(side="left", fill="both", expand=True)
        ttk.Label(
            main_area,
            text="Main content area.\nResize the window to see how pack() reacts.",
            justify="left",
        ).pack(anchor="w")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("pack() Demo")
    root.geometry("600x400")
    PackDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
