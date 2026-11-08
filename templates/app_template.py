"""Application Template — minimal but production-shaped.

Copy this file as the starting point for a new tkinter application.
It demonstrates the recommended baseline:

  * Application class wrapping the root window.
  * `ttk` widgets + `clam` theme for cross-platform consistency.
  * A defined palette.
  * Sensible default geometry and minimum size.
  * A clear main entry point.

Usage:
    cp templates/app_template.py myapp/main.py
    # Edit the class name, palette, and _build_ui method.

Run:  python templates/app_template.py
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


# ---------------------------------------------------------------------------
# Palette — change these four colors to re-skin the entire app.
# ---------------------------------------------------------------------------
PALETTE = {
    "bg":            "#FFFFFF",
    "surface":       "#F4F4F5",
    "primary":       "#1565D8",
    "primary_hover": "#0F4C9E",
    "text":          "#1F2937",
    "muted":         "#6B7280",
    "border":        "#D1D5DB",
    "danger":        "#DC2626",
}


class AppTemplate(ttk.Frame):
    """Skeleton application.

    Replace this docstring with a description of what your app does.
    """

    def __init__(self, master: tk.Misc) -> None:
        """Construct the application's UI.

        Args:
            master: the root Tk window.
        """
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)

        # ----- Apply theme. -----
        self._apply_theme()

        # ----- Build the UI. -----
        self._build_ui()

    def _apply_theme(self) -> None:
        """Configure ttk styles using the PALETTE."""
        style = ttk.Style(self)
        # 'clam' looks consistent across Windows, macOS, and Linux.
        style.theme_use("clam")

        # Root style — every widget inherits from this.
        style.configure(
            ".",
            background=PALETTE["bg"],
            foreground=PALETTE["text"],
            bordercolor=PALETTE["border"],
            lightcolor=PALETTE["border"],
            darkcolor=PALETTE["border"],
            troughcolor=PALETTE["surface"],
            fieldbackground=PALETTE["surface"],
        )

        # Standard widget styles.
        style.configure("TFrame",  background=PALETTE["bg"])
        style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])
        style.configure("TButton", background=PALETTE["surface"], foreground=PALETTE["text"])
        style.map("TButton",
                  background=[("active", PALETTE["border"])])

        # Accent button style — use for the primary action on each screen.
        style.configure(
            "Accent.TButton",
            background=PALETTE["primary"],
            foreground="white",
            font=("TkDefaultFont", 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        style.map("Accent.TButton",
                  background=[("active", PALETTE["primary_hover"])])

    def _build_ui(self) -> None:
        """Construct the widget tree.

        Replace this method with your app's actual UI.
        """
        # Title.
        ttk.Label(self, text="App Template",
                  font=("TkDefaultFont", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Form fields — replace with your own.
        ttk.Label(self, text="Name:").grid(row=1, column=0, sticky="e", padx=(0, 6), pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var).grid(
            row=1, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Email:").grid(row=2, column=0, sticky="e", padx=(0, 6), pady=4)
        self.email_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var).grid(
            row=2, column=1, sticky="ew", pady=4)

        # Bottom action bar.
        actions = ttk.Frame(self)
        actions.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(actions, text="Cancel", command=self._on_cancel).pack(side="right", padx=(6, 0))
        ttk.Button(actions, text="Submit", style="Accent.TButton",
                   command=self._on_submit).pack(side="right")

        # Make column 1 stretch horizontally.
        self.columnconfigure(1, weight=1)

    # ----- Handlers — replace with your actual logic. -----

    def _on_submit(self) -> None:
        """Handle the Submit button click."""
        from tkinter import messagebox
        messagebox.showinfo(
            "Submitted",
            f"Name:  {self.name_var.get()!r}\n"
            f"Email: {self.email_var.get()!r}",
            parent=self.winfo_toplevel(),
        )

    def _on_cancel(self) -> None:
        """Close the application."""
        self.winfo_toplevel().destroy()


def main() -> None:
    """Entry point — construct the root window and start the loop."""
    root = tk.Tk()
    root.title("App Template")
    # Set a sensible default size and minimum size.
    root.geometry("480x280")
    root.minsize(360, 240)
    AppTemplate(root)
    root.mainloop()


if __name__ == "__main__":
    main()
