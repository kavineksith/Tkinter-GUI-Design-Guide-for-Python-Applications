"""Example 11 — Canvas Drawing.

The Canvas widget is tkinter's 2D vector surface: lines, rectangles,
ovals, polygons, arcs, text, images, and embedded widgets. This demo
builds a small paint program: click-drag to draw freehand, double-click
to clear, and toggle color/brush size.

Run:  python examples/11_canvas_drawing.py

Companion doc: 02_widgets.md (section 2.4) and 05_event_handling.md
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class PaintApp(ttk.Frame):
    """A simple paint program built on tk.Canvas."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the toolbar and canvas."""
        super().__init__(master, padding=8)
        self.pack(fill="both", expand=True)

        # ----- Drawing state. -----
        # All instance state lives on self so handlers can mutate it.
        self.colors = ["#1F2937", "#DC2626", "#10B981", "#1565D8", "#F59E0B"]
        self.color_index = 0
        self.brush_size = 4
        self.last_x: int | None = None    # last x during a drag stroke
        self.last_y: int | None = None

        # ----- Toolbar at the top. -----
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x", pady=(0, 6))

        ttk.Label(toolbar, text="Color:").pack(side="left", padx=(0, 4))

        # Color swatches — use tk.Label with a bg color so we can show the
        # actual color (ttk.Label doesn't expose background reliably).
        self.swatches: list[tk.Label] = []
        for i, color in enumerate(self.colors):
            swatch = tk.Label(toolbar, bg=color, width=3, relief="raised",
                              borderwidth=2, cursor="hand2")
            swatch.pack(side="left", padx=2)
            swatch.bind("<Button-1>", lambda e, idx=i: self._select_color(idx))
            self.swatches.append(swatch)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        ttk.Label(toolbar, text="Brush size:").pack(side="left", padx=(0, 4))
        self.size_var = tk.IntVar(value=self.brush_size)
        self.size_var.trace_add("write", self._on_size_change)
        ttk.Scale(toolbar, from_=1, to=20, variable=self.size_var,
                  orient="horizontal", length=120).pack(side="left")

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        ttk.Button(toolbar, text="Clear", command=self._clear).pack(side="left")
        ttk.Button(toolbar, text="Save PNG...",
                   command=self._save_image).pack(side="left", padx=4)

        # ----- Canvas in the middle. -----
        # Note tk.Canvas, not ttk.Canvas — ttk has no Canvas equivalent.
        self.canvas = tk.Canvas(self, bg="white",
                                highlightthickness=1,
                                highlightbackground="#D1D5DB",
                                cursor="crosshair")
        self.canvas.pack(side="top", fill="both", expand=True)

        # Mouse events for freehand drawing.
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)         # move while button held
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._clear_via_event)

        # Highlight the initially selected swatch.
        self._select_color(0)

    # ----- Event handlers -----

    def _current_color(self) -> str:
        """Return the currently active color string."""
        return self.colors[self.color_index]

    def _select_color(self, idx: int) -> None:
        """Set the active color and update the swatch borders."""
        self.color_index = idx
        for i, swatch in enumerate(self.swatches):
            # Use relief to mark the active swatch.
            swatch.config(relief="sunken" if i == idx else "raised")

    def _on_size_change(self, *_args) -> None:
        """Sync the brush size from the Scale variable."""
        self.brush_size = self.size_var.get()

    def _on_press(self, event: tk.Event) -> None:
        """Begin a new stroke: draw a dot at the click point."""
        self.last_x = event.x
        self.last_y = event.y
        self._draw_dot(event.x, event.y)

    def _on_drag(self, event: tk.Event) -> None:
        """Continue a stroke: draw a line from the last point to here."""
        if self.last_x is None:
            return
        self.canvas.create_line(
            self.last_x, self.last_y, event.x, event.y,
            fill=self._current_color(),
            width=self.brush_size,
            capstyle="round",      # rounded line ends — smoother strokes
            joinstyle="round",
        )
        self.last_x = event.x
        self.last_y = event.y

    def _on_release(self, event: tk.Event) -> None:
        """End the stroke: forget the last position."""
        self.last_x = None
        self.last_y = None

    def _draw_dot(self, x: int, y: int) -> None:
        """Draw a single dot — used at the start of a stroke."""
        r = max(1, self.brush_size // 2)
        self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=self._current_color(), outline="",
        )

    def _clear(self) -> None:
        """Delete all canvas items (no undo!)."""
        self.canvas.delete("all")

    def _clear_via_event(self, event: tk.Event) -> None:
        """Same as _clear but ignores its unused event argument."""
        self._clear()

    def _save_image(self) -> None:
        """Save the canvas contents as a PostScript file.

        Tk's Canvas can only natively export to PostScript. To get PNG,
        install Pillow and use ImageGrab.grab(bbox).
        """
        from tkinter import filedialog, messagebox
        path = filedialog.asksaveasfilename(
            defaultextension=".ps",
            filetypes=[("PostScript", "*.ps")],
            title="Save canvas",
        )
        if not path:
            return
        try:
            # Canvas.postscript returns the PS content; we save it ourselves.
            ps = self.canvas.postscript(colormode="color")
            with open(path, "w", encoding="latin-1") as f:
                f.write(ps)
            messagebox.showinfo("Saved", f"Canvas saved to:\n{path}")
        except OSError as e:
            messagebox.showerror("Save failed", str(e))


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Canvas Drawing Demo")
    root.geometry("640x480")
    PaintApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
