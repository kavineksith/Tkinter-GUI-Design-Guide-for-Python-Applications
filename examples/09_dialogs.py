"""Example 09 — Custom Dialogs (modal Toplevel).

Shows how to build a custom modal dialog — a Toplevel window that
blocks the caller until the user closes it, returning a result.

Use this pattern instead of `simpledialog.askstring` when you need
multiple fields, validation, or custom widgets in the dialog.

Run:  python examples/09_dialogs.py

Companion doc: 02_widgets.md (section 2.5) and 05_event_handling.md (§ 5.8)
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class LoginDialog(tk.Toplevel):
    """A modal dialog that asks the user for username and password.

    Attributes:
        result: tuple[str, str] | None — set to (username, password)
                when the user clicks OK, or None if cancelled.
    """

    def __init__(self, master: tk.Misc) -> None:
        """Construct the dialog as a modal Toplevel.

        Args:
            master: the parent window (will be disabled while this dialog
                    is open — that's what "modal" means).
        """
        super().__init__(master)
        self.title("Login")
        self.result: tuple[str, str] | None = None
        self.resizable(False, False)

        # Grab makes this dialog modal — no other window in this app
        # will receive events until we release the grab.
        self.transient(master)
        self.grab_set()

        self._build_ui()
        # Center the dialog over the parent window.
        self._center_over(master)

        # Bind Escape → cancel, Return → submit.
        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>",  lambda e: self._ok())

        # Block the caller until the window is destroyed.
        # The GUI remains responsive — events still flow — but the
        # Python call that opened this dialog pauses here.
        self.wait_window()

    def _build_ui(self) -> None:
        """Build the form."""
        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="e", padx=(0, 6), pady=4)
        self.user_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.user_var).grid(
            row=0, column=1, sticky="ew", pady=4)
        # Focus the first field so the user can type immediately.
        self.user_var.trace_add("write", lambda *_: None)   # no-op trace

        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e", padx=(0, 6), pady=4)
        self.pass_var = tk.StringVar()
        # show="*" masks the typed characters for password fields.
        ttk.Entry(frame, textvariable=self.pass_var, show="*").grid(
            row=1, column=1, sticky="ew", pady=4)

        button_bar = ttk.Frame(frame)
        button_bar.grid(row=2, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(button_bar, text="Cancel", command=self._cancel).pack(side="left", padx=(0, 6))
        ttk.Button(button_bar, text="OK",     command=self._ok).pack(side="left")

        frame.columnconfigure(1, weight=1)
        # Move keyboard focus into the username entry as soon as it exists.
        self.after_idle(lambda: self._focus_first_entry())

    def _focus_first_entry(self) -> None:
        """Set initial keyboard focus to the first input field."""
        # Find the first ttk.Entry by walking children.
        for child in self.winfo_children():
            for sub in child.winfo_children():
                if isinstance(sub, ttk.Entry):
                    sub.focus_set()
                    return

    def _center_over(self, parent: tk.Misc) -> None:
        """Center this dialog over the parent window."""
        self.update_idletasks()      # required so winfo_width returns real value
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _ok(self) -> None:
        """Validate and accept the dialog."""
        username = self.user_var.get().strip()
        password = self.pass_var.get()
        if not username:
            messagebox.showwarning("Missing", "Please enter a username.", parent=self)
            return
        if not password:
            messagebox.showwarning("Missing", "Please enter a password.", parent=self)
            return
        self.result = (username, password)
        self._close()

    def _cancel(self) -> None:
        """Discard the result and close."""
        self.result = None
        self._close()

    def _close(self) -> None:
        """Release the modal grab and destroy the dialog."""
        self.grab_release()
        self.destroy()


# ---------------------------------------------------------------------------
# Demo launcher
# ---------------------------------------------------------------------------

class DialogDemo(ttk.Frame):
    """A small window with one button that opens the login dialog."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the demo UI."""
        super().__init__(master, padding=20)
        self.pack(fill="both", expand=True)

        ttk.Label(self, text="Custom Dialog Demo",
                  font=("TkDefaultFont", 16, "bold")).pack(pady=(0, 12))
        ttk.Button(self, text="Open login dialog...",
                   command=self._open_login).pack()

        self.result_label = ttk.Label(self, text="No result yet.")
        self.result_label.pack(pady=12)

    def _open_login(self) -> None:
        """Construct the dialog and read the result after it closes."""
        # Note: __init__ blocks until the dialog is closed (wait_window).
        # After it returns, `.result` is filled in.
        dialog = LoginDialog(self.winfo_toplevel())
        if dialog.result is None:
            self.result_label.config(text="User cancelled.")
        else:
            user, pw = dialog.result
            # Demo only — never log passwords in real apps.
            self.result_label.config(text=f"Logged in as: {user} (pw hidden)")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Custom Dialogs Demo")
    root.geometry("420x220")
    DialogDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
