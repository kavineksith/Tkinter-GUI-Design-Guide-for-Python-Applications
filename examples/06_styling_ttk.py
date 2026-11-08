"""Example 06 — Styling & Theming with ttk.Style.

Shows how to:
  * Pick a theme (we use 'clam' for cross-platform consistency).
  * Define a custom color palette.
  * Configure a named style (e.g. 'Accent.TButton').
  * Use `style.map()` to drive state-dependent appearance.
  * Switch themes live (Light / Dark).

Run:  python examples/06_styling_ttk.py

Companion doc: 04_styling_and_theming.md
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


# ---------------------------------------------------------------------------
# Palette: defined once, imported everywhere in a real app.
# ---------------------------------------------------------------------------
PALETTE = {
    "light": {
        "bg":            "#FFFFFF",
        "surface":       "#F4F4F5",
        "primary":       "#1565D8",
        "primary_hover": "#0F4C9E",
        "danger":        "#DC2626",
        "danger_hover":  "#B91C1C",
        "text":          "#1F2937",
        "muted":         "#6B7280",
        "border":        "#D1D5DB",
    },
    "dark": {
        "bg":            "#0F172A",
        "surface":       "#1E293B",
        "primary":       "#3B82F6",
        "primary_hover": "#60A5FA",
        "danger":        "#EF4444",
        "danger_hover":  "#F87171",
        "text":          "#F1F5F9",
        "muted":         "#94A3B8",
        "border":        "#334155",
    },
}


class StyledApp(ttk.Frame):
    """A small panel that demonstrates several custom ttk styles."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the panel and apply the initial theme."""
        super().__init__(master, padding=20)
        self.pack(fill="both", expand=True)

        # ttk.Style: one instance per app. All styles are configured through it.
        self.style = ttk.Style(self)
        # 'clam' is the most consistent cross-platform theme.
        self.style.theme_use("clam")

        # Apply the light theme to start.
        self._mode = "light"
        self._apply_theme()

        # ----- Build the widgets that show off the styles. -----
        ttk.Label(self, text="Custom ttk Styles",
                  font=("TkDefaultFont", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Default button — uses the standard style.
        ttk.Label(self, text="Default.TButton:").grid(row=1, column=0, sticky="e", padx=(0, 8))
        ttk.Button(self, text="Default").grid(row=1, column=1, sticky="w", pady=4)

        # Accent button — uses our custom 'Accent.TButton' style.
        ttk.Label(self, text="Accent.TButton:").grid(row=2, column=0, sticky="e", padx=(0, 8))
        ttk.Button(self, text="Save", style="Accent.TButton").grid(
            row=2, column=1, sticky="w", pady=4)

        # Danger button — uses our custom 'Danger.TButton' style.
        ttk.Label(self, text="Danger.TButton:").grid(row=3, column=0, sticky="e", padx=(0, 8))
        ttk.Button(self, text="Delete", style="Danger.TButton").grid(
            row=3, column=1, sticky="w", pady=4)

        # Heading label style.
        ttk.Label(self, text="Heading.TLabel:").grid(row=4, column=0, sticky="e", padx=(0, 8))
        ttk.Label(self, text="Large Heading", style="Heading.TLabel").grid(
            row=4, column=1, sticky="w", pady=4)

        # ----- Theme switcher at the bottom. -----
        ttk.Separator(self, orient="horizontal").grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(12, 8))
        ttk.Label(self, text="Theme:").grid(row=6, column=0, sticky="e", padx=(0, 8))
        ttk.Button(self, text="Toggle Light/Dark",
                   command=self._toggle_theme).grid(row=6, column=1, sticky="w")

        self.columnconfigure(1, weight=1)

    # ----- Theme helpers -----

    def _toggle_theme(self) -> None:
        """Switch between light and dark mode."""
        self._mode = "dark" if self._mode == "light" else "light"
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply the current theme by reconfiguring ttk styles."""
        p = PALETTE[self._mode]

        # Root style '.' — every widget inherits from it.
        self.style.configure(
            ".",
            background=p["bg"],
            foreground=p["text"],
            bordercolor=p["border"],
            lightcolor=p["border"],
            darkcolor=p["border"],
            troughcolor=p["surface"],
            fieldbackground=p["surface"],
            focuscolor=p["primary"],
        )

        # Specific widget styles inherited from '.'.
        self.style.configure("TLabel", background=p["bg"], foreground=p["text"])
        self.style.configure("TFrame", background=p["bg"])
        self.style.configure("TButton", background=p["surface"], foreground=p["text"])
        self.style.map("TButton",
                       background=[("active", p["border"])])

        # Custom Accent button style.
        self.style.configure(
            "Accent.TButton",
            background=p["primary"],
            foreground="white",
            font=("TkDefaultFont", 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        self.style.map("Accent.TButton",
                       background=[("active", p["primary_hover"]),
                                  ("disabled", p["muted"])])

        # Custom Danger button style.
        self.style.configure(
            "Danger.TButton",
            background=p["danger"],
            foreground="white",
            font=("TkDefaultFont", 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        self.style.map("Danger.TButton",
                       background=[("active", p["danger_hover"])])

        # Heading label style.
        self.style.configure(
            "Heading.TLabel",
            background=p["bg"],
            foreground=p["text"],
            font=("TkDefaultFont", 18, "bold"),
        )


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Styling & Theming Demo")
    root.geometry("440x320")
    StyledApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
