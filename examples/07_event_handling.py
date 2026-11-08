"""Example 07 — Event Handling.

Shows the three main event-handling mechanisms in tkinter:
  1. The `command=` option (for the primary action of a widget).
  2. `bind()` for low-level events (key presses, mouse motion, etc.).
  3. ttk virtual events like `<<ComboboxSelected>>`.

Also demonstrates the cross-platform mouse-wheel pattern, modifier
detection, and using `event.widget` to identify the source.

Run:  python examples/07_event_handling.py

Companion doc: 05_event_handling.md
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class EventsDemo(ttk.Frame):
    """A panel that prints a log line for every event it captures."""

    def __init__(self, master: tk.Misc) -> None:
        """Construct widgets and bind events."""
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)

        # ----- Left panel: widgets that emit events. -----
        left = ttk.LabelFrame(self, text="Interact here", padding=8)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        # Button uses command= — the simplest event mechanism.
        ttk.Button(left, text="command= demo", command=self._on_button).pack(
            anchor="w", pady=2)

        # Combobox emits a virtual event when the selection changes.
        self.combo = ttk.Combobox(
            left, values=["Red", "Green", "Blue"], state="readonly")
        self.combo.pack(anchor="w", pady=2)
        self.combo.bind("<<ComboboxSelected>>", self._on_combo_selected)

        # Entry: bind <Return> to "submit" and <Key> to "echo char".
        self.entry = ttk.Entry(left)
        self.entry.pack(anchor="w", fill="x", pady=2)
        self.entry.bind("<Return>", self._on_entry_return)
        self.entry.bind("<Key>", self._on_key)

        # Canvas: capture mouse motion and clicks for drawing.
        self.canvas = tk.Canvas(left, width=200, height=120,
                                bg="white", highlightthickness=1,
                                highlightbackground="#D1D5DB")
        self.canvas.pack(anchor="w", pady=4)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        # Cross-platform mouse wheel handling.
        self.canvas.bind("<MouseWheel>", self._on_wheel)        # Windows/macOS
        self.canvas.bind("<Button-4>", self._on_wheel)          # Linux up
        self.canvas.bind("<Button-5>", self._on_wheel)          # Linux down

        # Global key bindings on the root.
        # Use bind_all for true application-wide shortcuts.
        self.winfo_toplevel().bind_all("<Control-s>", self._on_save)
        self.winfo_toplevel().bind_all("<F1>", self._on_help)

        # ----- Right panel: log output. -----
        right = ttk.LabelFrame(self, text="Event log", padding=4)
        right.pack(side="left", fill="both", expand=True)
        self.log = tk.Text(right, width=42, height=18, state="disabled",
                           wrap="word", font=("Consolas", 9))
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(right, command=self.log.yview)
        scrollbar.pack(side="right", fill="y")
        self.log.config(yscrollcommand=scrollbar.set)

        # Track the number of canvas dots drawn for the wheel handler.
        self._dot_size = 4

    # ----- Event handlers -----

    def _log(self, message: str) -> None:
        """Append a line to the read-only log Text widget."""
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")                      # auto-scroll
        self.log.configure(state="disabled")    # user can't type in it

    def _on_button(self) -> None:
        """Handler attached via command= (no event argument)."""
        self._log("[command] Button clicked")

    def _on_combo_selected(self, event: tk.Event) -> None:
        """Handler for the <<ComboboxSelected>> virtual event."""
        # Read via the widget OR via the bound variable. We use the widget.
        value = event.widget.get()
        self._log(f"[virtual] Combobox selected: {value!r}")

    def _on_entry_return(self, event: tk.Event) -> None:
        """Fires when the user presses Enter while the entry has focus."""
        self._log(f"[<Return>] Submitted: {event.widget.get()!r}")

    def _on_key(self, event: tk.Event) -> None:
        """Fires for every keystroke while the entry has focus.

        Note: returning the string 'break' from this handler would
        suppress the default behavior (character insertion). We don't,
        so the default still happens — characters appear in the entry.
        """
        # Skip modifier-only events; only log printable keys.
        if event.char:
            self._log(f"[<Key>] char={event.char!r} keysym={event.keysym}")

    def _on_canvas_click(self, event: tk.Event) -> None:
        """Draw a small dot where the user clicked."""
        x, y = event.x, event.y
        size = self._dot_size
        self.canvas.create_oval(x - size, y - size, x + size, y + size,
                                fill="#1565D8", outline="")
        self._log(f"[<Button-1>] click at ({x}, {y})")

    def _on_canvas_motion(self, event: tk.Event) -> None:
        """Throttled log: print coords but only every 10th move event.

        Without throttling the log fills up instantly when the mouse
        moves. This is a common pattern: drop noisy events, log the rest.
        """
        # We don't keep a counter attribute until first call.
        count = getattr(self, "_motion_count", 0) + 1
        self._motion_count = count
        if count % 10 == 0:
            self._log(f"[<Motion>] x={event.x} y={event.y} (1 of 10)")

    def _on_wheel(self, event: tk.Event) -> None:
        """Handle mouse wheel rotation cross-platform.

        Windows / macOS: <MouseWheel>, read event.delta (positive = up).
        Linux/X11:       <Button-4> (up) / <Button-5> (down).
        """
        if event.num in (4, 5):
            delta = 120 if event.num == 4 else -120
        else:
            delta = event.delta
        # Adjust dot size: scroll up = bigger, down = smaller.
        self._dot_size = max(2, min(20, self._dot_size + (1 if delta > 0 else -1)))
        self._log(f"[wheel] delta={delta} -> dot size {self._dot_size}")

    def _on_save(self, event: tk.Event) -> None:
        """Global Ctrl+S handler."""
        self._log("[Ctrl+S] Save action triggered (no-op in demo)")

    def _on_help(self, event: tk.Event) -> None:
        """Global F1 handler."""
        self._log("[F1] Help (no-op in demo)")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Event Handling Demo")
    root.geometry("720x420")
    EventsDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
