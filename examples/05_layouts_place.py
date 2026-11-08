"""Example 05 — Layout Manager: place.

Demonstrates the place geometry manager, which positions widgets at
absolute pixel coordinates OR at relative fractions of the parent.

Use place() sparingly — it's the most powerful but least flexible
when the window resizes or the system font changes.

Run:  python examples/05_layouts_place.py

Companion doc: 03_layout_managers.md (section 3.3)
"""
import tkinter as tk
from tkinter import ttk


class PlaceDemo(ttk.Frame):
    """A floating, centered card UI built with place().

    Three patterns are shown:
      1. Absolute coordinates (`x=`, `y=`).
      2. Centered using `relx=0.5, rely=0.5, anchor="center"`.
      3. Banner sized relative to the parent (`relwidth`, `relheight`).
    """

    def __init__(self, master: tk.Misc) -> None:
        """Construct the demo frame."""
        super().__init__(master)
        self.pack(fill="both", expand=True)

        # Give the frame a visible background so the relative sizing is obvious.
        # Note: ttk.Frame does not support `background=`; we use a tk.Frame here.
        # That's the one acceptable place to use classic widgets over ttk.
        self.config(borderwidth=0)

        # ----- 1. A banner sized relative to the parent. -----
        # relwidth / relheight are fractions of the parent (0.0..1.0).
        banner = tk.Label(
            self,
            text="Banner (80% wide, 18% tall)",
            bg="#1565D8", fg="white",
            font=("TkDefaultFont", 14, "bold"),
        )
        banner.place(relx=0.1, rely=0.05, relwidth=0.8, relheight=0.18)

        # ----- 2. A button at absolute pixel coordinates. -----
        # x=20, y=20 means: top-left corner of the button at (20, 20) inside self.
        abs_btn = ttk.Button(self, text="Absolute @ (20, 220)")
        abs_btn.place(x=20, y=220)

        # ----- 3. A centered card. -----
        # relx=0.5, rely=0.5, anchor="center" → the CENTER of the widget sits
        # at the center of the parent, regardless of the widget's size.
        card = ttk.LabelFrame(self, text="Centered card", padding=12)
        card.place(relx=0.5, rely=0.5, anchor="center", width=240, height=120)
        ttk.Label(card, text="I'm perfectly centered.").pack(pady=(0, 8))
        ttk.Button(card, text="OK").pack()

        # ----- 4. Bottom-right badge, anchored to that corner. -----
        badge = tk.Label(
            self,
            text="v1.0",
            bg="#10B981", fg="white",
            font=("TkDefaultFont", 9, "bold"),
        )
        # relx=1.0 → right edge of parent. rely=1.0 → bottom edge.
        # anchor="se" → south-east corner of the badge sits at that point,
        # with a small outward offset via negative x/y.
        badge.place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-8)


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("place() Demo")
    root.geometry("600x420")
    # Make the window background a soft gray so the banner stands out.
    root.configure(bg="#F3F4F6")
    PlaceDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
