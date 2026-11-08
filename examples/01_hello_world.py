"""Example 01 — Hello, World.

The smallest meaningful tkinter program. Demonstrates:
  * Creating the root application window with `tk.Tk()`.
  * Adding a `ttk.Label` widget.
  * Positioning the label with `.pack()`.
  * Starting the event loop with `.mainloop()`.

Run:  python examples/01_hello_world.py

Companion doc: 01_introduction.md
"""
# Standard library imports only — tkinter ships with CPython.
import tkinter as tk
from tkinter import ttk


def main() -> None:
    """Build and run the application.

    The function does not return until the user closes the window,
    because `mainloop()` blocks until the root window is destroyed.
    """
    # 1. Create the root window — exactly one per application process.
    root = tk.Tk()

    # 2. Configure the window's title bar text and initial size.
    root.title("Hello, Tkinter")
    root.geometry("320x160")          # width x height, in pixels

    # 3. Create a themed label widget. The first positional arg is the parent.
    #    ttk widgets are styled centrally via ttk.Style (see example 06).
    label = ttk.Label(root, text="Hello, World!", font=("TkDefaultFont", 16))

    # 4. Lay the label out inside its parent using pack().
    #    padx/pady give it 30 px of empty space on every side.
    label.pack(padx=30, pady=30)

    # 5. Start the event loop. This call BLOCKS the script here.
    #    While blocked, the window is alive and responsive — clicks,
    #    key presses, and resizes all flow through to widgets.
    root.mainloop()


# Standard Python idiom: only run main() if this file is executed directly.
# Lets the file also be imported without popping a window.
if __name__ == "__main__":
    main()
