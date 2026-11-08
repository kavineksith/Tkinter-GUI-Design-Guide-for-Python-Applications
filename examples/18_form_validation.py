"""Example 18 — Form Validation.

Tkinter's `Entry` widget has built-in validation hooks via
`validate=` and `validatecommand=`. This example shows:

  * Live numeric-only entry.
  * Live max-length entry.
  * A custom validator that runs Python code.
  * Common pitfalls and how to avoid them.

Run:  python examples/18_form_validation.py

Companion doc: 09_common_pitfalls.md (section 9.12) and 05_event_handling.md
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox


class ValidationDemo(ttk.Frame):
    """A form with three validated entries."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the form."""
        super().__init__(master, padding=14)
        self.pack(fill="both", expand=True)

        ttk.Label(self, text="Form Validation Demo",
                  font=("TkDefaultFont", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # ----- Entry 1: numeric only. -----
        ttk.Label(self, text="Age (digits only):").grid(
            row=1, column=0, sticky="e", padx=(0, 6), pady=4)
        self.age_var = tk.StringVar()
        age_entry = ttk.Entry(self, textvariable=self.age_var)
        age_entry.grid(row=1, column=1, sticky="ew", pady=4)
        # Register the validator function. Tkinter's validatecommand
        # needs a Tcl-side function reference; .register gives us one.
        age_vcmd = (self.register(self._validate_int), "%P")
        age_entry.config(validate="key", validatecommand=age_vcmd)
        # Also bound: when the value changes, clamp 0..150.
        self.age_var.trace_add("write", self._clamp_age)

        # ----- Entry 2: max-length string. -----
        ttk.Label(self, text="Username (max 12):").grid(
            row=2, column=0, sticky="e", padx=(0, 6), pady=4)
        self.user_var = tk.StringVar()
        user_entry = ttk.Entry(self, textvariable=self.user_var)
        user_entry.grid(row=2, column=1, sticky="ew", pady=4)
        # Use a lambda-style validator directly.
        user_vcmd = (self.register(lambda new_value: len(new_value) <= 12), "%P")
        user_entry.config(validate="key", validatecommand=user_vcmd)

        # ----- Entry 3: pattern (phone: digits and dashes only). -----
        ttk.Label(self, text="Phone (digits/dashes):").grid(
            row=3, column=0, sticky="e", padx=(0, 6), pady=4)
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(self, textvariable=self.phone_var)
        phone_entry.grid(row=3, column=1, sticky="ew", pady=4)
        phone_vcmd = (self.register(self._validate_phone), "%P")
        phone_entry.config(validate="key", validatecommand=phone_vcmd)

        # ----- Submit. -----
        self.submit = ttk.Button(self, text="Submit", command=self._on_submit)
        self.submit.grid(row=4, column=1, sticky="e", pady=(10, 0))

        self.columnconfigure(1, weight=1)

    # ----- Validators -----

    def _validate_int(self, new_value: str) -> bool:
        """Allow empty input OR a string of digits.

        Returns True to ACCEPT the edit (allowing it through), False to
        REJECT it (the keystroke is silently dropped).

        Note: returning the boolean is correct — Tk converts True to
        the string "1" automatically. Returning the string "break"
        would NOT work here (it's for bind(), not validatecommand).
        """
        if not new_value:
            return True
        return new_value.isdigit()

    def _clamp_age(self, *_args) -> None:
        """Bound the age to 0..150 by silently rewriting the variable.

        This is the safe way to "fix" a value after a validator lets it
        through. If we tried to call entry.delete/insert directly, Tk
        would disable the validator (see common pitfall 9.12).
        """
        value = self.age_var.get()
        if not value:
            return
        n = int(value)
        if n > 150:
            # Setting the variable here does NOT re-trigger validatecommand
            # (only the trace we are already inside fires).
            self.age_var.set("150")

    def _validate_phone(self, new_value: str) -> bool:
        """Allow empty or strings matching [0-9-]+."""
        if not new_value:
            return True
        return all(ch.isdigit() or ch == "-" for ch in new_value)

    # ----- Submit -----

    def _on_submit(self) -> None:
        """Validate the whole form before accepting."""
        errors = []
        if not self.age_var.get():
            errors.append("Age is required.")
        if not self.user_var.get():
            errors.append("Username is required.")
        if not self.phone_var.get():
            errors.append("Phone is required.")

        if errors:
            messagebox.showwarning("Validation", "\n".join(errors))
            return

        messagebox.showinfo(
            "Submitted",
            f"Age: {self.age_var.get()}\n"
            f"Username: {self.user_var.get()}\n"
            f"Phone: {self.phone_var.get()}",
        )


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Form Validation Demo")
    root.geometry("440x220")
    ValidationDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
