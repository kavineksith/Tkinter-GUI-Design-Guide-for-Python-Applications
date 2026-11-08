"""Example 08 — Menu Bar, Toolbar, and Context Menu.

Shows the standard "desktop app" chrome:
  * A top menu bar with File / Edit / Help menus.
  * A horizontal toolbar with buttons.
  * A right-click context menu on the text widget.

Run:  python examples/08_menubar_toolbar.py

Companion doc: 02_widgets.md (section 2.5) and 05_event_handling.md
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class AppWindow(ttk.Frame):
    """A typical desktop application window with menu bar and toolbar."""

    def __init__(self, master: tk.Misc) -> None:
        """Build menus, toolbar, and main text area."""
        super().__init__(master, padding=6)
        self.pack(fill="both", expand=True)

        # tk.Menu is the one widget that doesn't have a ttk equivalent —
        # we use tk.Menu directly. That's the only acceptable break from
        # the "prefer ttk" rule.
        self._build_menubar()
        self._build_toolbar()
        self._build_text_area()

    # ----- Menu bar -----

    def _build_menubar(self) -> None:
        """Create the top menu bar with File / Edit / Help menus."""
        # Tear-off menus are an old Tk feature; we always disable them.
        root = self.winfo_toplevel()
        root.option_add("*tearOff", False)

        menubar = tk.Menu(root)
        root.config(menu=menubar)   # IMPORTANT: assign with `menu=`, not pack()

        # --- File menu ---
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        # underline=0 → the 'F' is underlined; Alt+F opens this menu.
        # accelerator is just a visible hint; the binding must still be made.
        file_menu.add_command(label="New",  underline=0, accelerator="Ctrl+N",
                              command=self._on_new)
        file_menu.add_command(label="Open...", underline=0, accelerator="Ctrl+O",
                              command=self._on_open)
        file_menu.add_command(label="Save",  underline=0, accelerator="Ctrl+S",
                              command=self._on_save)
        file_menu.add_separator()    # visual divider
        file_menu.add_command(label="Exit", underline=1, command=self._on_exit)

        # --- Edit menu ---
        edit_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut",   accelerator="Ctrl+X",
                              command=self._on_cut)
        edit_menu.add_command(label="Copy",  accelerator="Ctrl+C",
                              command=self._on_copy)
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V",
                              command=self._on_paste)

        # --- Help menu ---
        help_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._on_about)

        # Wire the keyboard shortcuts globally.
        root.bind_all("<Control-n>", lambda e: self._on_new())
        root.bind_all("<Control-o>", lambda e: self._on_open())
        root.bind_all("<Control-s>", lambda e: self._on_save())

    # ----- Toolbar -----

    def _build_toolbar(self) -> None:
        """A horizontal strip of buttons below the menu bar."""
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x", pady=(0, 4))

        # Buttons share an icon-less style; in a real app, add small PNGs.
        ttk.Button(toolbar, text="New",   command=self._on_new).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Open",  command=self._on_open).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Save",  command=self._on_save).pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(toolbar, text="About", command=self._on_about).pack(side="left", padx=2)

    # ----- Text area + context menu -----

    def _build_text_area(self) -> None:
        """The main editing area, with a scrollbar and a right-click menu."""
        frame = ttk.Frame(self)
        frame.pack(side="top", fill="both", expand=True)

        self.text = tk.Text(frame, wrap="word", font=("TkDefaultFont", 11),
                            undo=True)
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scrollbar.set)

        # Insert some placeholder text.
        self.text.insert("1.0",
                         "Right-click here for a context menu.\n"
                         "Use Ctrl+N / Ctrl+O / Ctrl+S for file actions.\n")

        # Build the context menu (tk.Menu, same as the menubar).
        self.ctx_menu = tk.Menu(self, tearoff=False)
        self.ctx_menu.add_command(label="Cut",   command=self._on_cut)
        self.ctx_menu.add_command(label="Copy",  command=self._on_copy)
        self.ctx_menu.add_command(label="Paste", command=self._on_paste)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="Clear all", command=self._on_clear)

        # Bind right-click to show the menu at cursor position.
        # On macOS right-click is Button-2, but tkinter usually maps both.
        self.text.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event: tk.Event) -> None:
        """Display the context menu at the cursor position."""
        # post(x, y) takes screen coordinates, which event.x_root/y_root give.
        self.ctx_menu.tk_popup(event.x_root, event.y_root)

    # ----- Menu/toolbar command handlers -----

    def _on_new(self) -> None:
        """Clear the text area for a new document."""
        self.text.delete("1.0", "end")

    def _on_open(self) -> None:
        """Open a file dialog and load a text file."""
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Open document",
        )
        if not path:                 # user cancelled
            return
        with open(path, "r", encoding="utf-8") as f:
            self.text.delete("1.0", "end")
            self.text.insert("1.0", f.read())

    def _on_save(self) -> None:
        """Save the text area to a file chosen by the user."""
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save document",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", "end-1c"))

    def _on_exit(self) -> None:
        """Close the application."""
        self.winfo_toplevel().destroy()

    def _on_cut(self) -> None:
        """Cut the current selection to the clipboard."""
        self.text.event_generate("<<Cut>>")

    def _on_copy(self) -> None:
        """Copy the current selection to the clipboard."""
        self.text.event_generate("<<Copy>>")

    def _on_paste(self) -> None:
        """Paste from the clipboard into the text widget."""
        self.text.event_generate("<<Paste>>")

    def _on_clear(self) -> None:
        """Clear all text."""
        self.text.delete("1.0", "end")

    def _on_about(self) -> None:
        """Show the About dialog."""
        messagebox.showinfo(
            "About",
            "Menu Bar & Toolbar Demo\n"
            "Part of the Tkinter GUI Design Guide.",
            parent=self.winfo_toplevel(),
        )


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Menu Bar & Toolbar Demo")
    root.geometry("640x440")
    AppWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
