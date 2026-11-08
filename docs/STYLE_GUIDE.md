# Style Guide

A consistent set of conventions for tkinter code. Apply these across an entire project — consistency beats local cleverness.

## 1. File Conventions

- **One class per file.** A file may hold a few small related helpers, but a 1000-line file with five classes is a smell.
- **File names**: `snake_case.py`. Class names: `PascalCase`. Constants: `UPPER_SNAKE`.
- **Module length**: keep under 400 lines. Split larger modules.
- **Package layout**: see `06_architecture_patterns.md` section 6.8.

## 2. Import Conventions

```python
# Always:
import tkinter as tk
from tkinter import ttk

# OK, sparingly:
from tkinter import messagebox, filedialog, simpledialog, colorchooser

# Never:
from tkinter import *           # pollutes namespace, hard to lint
import tkinter.ttk as ttk        # fine, but inconsistent with the rest
```

## 3. Widget Construction

```python
# Good: positional parent, keyword options, named attribute.
self.email_entry = ttk.Entry(form, textvariable=self.email_var, width=30)
self.email_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=4)

# Bad: positional options (order-dependent, unreadable).
e = ttk.Entry(form, "", 30, None, None, "email")
```

- The parent is the only positional argument.
- Every option is a keyword argument.
- Assign every widget you'll need to reference later to `self.<name>`.

## 4. Layout Conventions

- Use `grid` for any form. Use `pack` for top-level region assembly.
- Use `place` only for overlays or floating widgets.
- Standard spacing: 8 px between related fields, 16 px between groups, 12 px window margin.
- Use `ttk.Frame(padding=...)` for uniform internal padding rather than per-widget `padx`/`pady`.
- Always call `columnconfigure(weight=1)` / `rowconfigure(weight=1)` for resizeable columns/rows.

## 5. Styling Conventions

- Define a single `PALETTE` dict in `myapp/styles/palette.py`. Import it.
- Use named ttk styles: `Accent.TButton`, `Danger.TButton`, `Heading.TLabel`.
- Configure fonts globally with `tkfont.nametofont("TkDefaultFont").configure(...)`.
- Never hardcode a font in a widget constructor — always use a style or `TkDefaultFont`.
- Use `clam` as the theme. Customize via `style.configure(".", ...)`.

## 6. Color Conventions

```python
PALETTE = {
    "bg":            "#FFFFFF",
    "surface":       "#F4F4F5",
    "primary":       "#1565D8",
    "primary_hover": "#0F4C9E",
    "accent":        "#10B981",
    "danger":        "#DC2626",
    "warning":       "#F59E0B",
    "text":          "#1F2937",
    "muted":         "#6B7280",
    "border":        "#D1D5DB",
}
```

- One primary action color per screen. All other actions are secondary.
- Use semantic, not visual, color names: `danger`, not `red`.
- Pair every state-dependent color with a hover variant.
- Don't rely on color alone — pair it with an icon or text label.

## 7. Spacing Scale

| Element | Padding |
|---|---|
| Window margin | 12 px |
| Field gap | 8 px |
| Group gap | 16 px |
| Button height padding | 6–8 px |
| Button width padding | 12–16 px |
| Toolbar button gap | 4 px |
| Card padding | 12 px |

## 8. Typography

- Body: `TkDefaultFont` (10–11 pt depending on OS).
- Headings: `TkDefaultFont` bold, size 14–18 pt.
- Code/logs: monospace, `Consolas` (Windows) / `Menlo` (macOS) / `DejaVu Sans Mono` (Linux).
- Avoid specifying fonts in widgets; configure them in styles.

## 9. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Class | PascalCase | `ContactForm` |
| Method | snake_case | `add_contact` |
| Private method | `_snake_case` | `_refresh_tree` |
| Callback | `on_<event>` or `handle_<action>` | `on_save_click`, `handle_delete` |
| Variable | snake_case | `current_path` |
| tk Variable | `<name>_var` | `email_var`, `dark_mode_var` |
| Widget attribute | `<name>_<widget>` | `email_entry`, `save_button` |
| Style name | `<CustomName>.<WidgetClass>` | `Accent.TButton` |

## 10. Event Handler Conventions

- Use `command=` for the primary action of a widget. Reserve `bind` for events that have no `command` equivalent.
- Bind to virtual events (`<<ComboboxSelected>>`) over raw events (`<Button-1>`) whenever possible.
- For app-wide shortcuts use `root.bind_all("<Control-s>", handler)`.
- Handler methods take `event` as the first parameter only if bound via `bind()`. `command=` handlers take no arguments.

## 11. Error Handling Conventions

- Wrap top-level handlers in `try/except`. Log + dialog. Never let the user see a traceback.
- Validate input before processing. Surface validation errors inline (next to the field) when possible.
- Catch specific exceptions (`OSError`, `ValueError`), not bare `Exception`.

```python
def on_save(self) -> None:
    """Save the current document."""
    path = self.current_path or self._prompt_for_path()
    if not path:
        return
    try:
        self._write_to(path)
    except OSError as e:
        logger.exception("Save failed")
        messagebox.showerror("Save failed", str(e), parent=self.root)
```

## 12. Documentation Conventions

Every module, class, and public method gets a docstring:

```python
"""Module purpose, in one line.

Optional longer description.
"""
from __future__ import annotations


class ContactBook:
    """In-memory contact storage.

    Pure Python — no tkinter dependency. Subscribe via `subscribe()`
    to receive notifications when the list changes.
    """

    def add(self, contact: Contact) -> None:
        """Append a contact to the end of the list.

        Args:
            contact: the Contact to add.

        Notifies subscribers after the mutation.
        """
        ...
```

- Use Google-style docstrings (the example above). Don't mix styles.
- Inline `#` comments for *why*; docstrings for *what*.

## 13. Type Hints

- Use `from __future__ import annotations` so type hints work on Python 3.8+.
- Annotate every public method's parameters and return type.
- Use `tk.Misc` as the type of a widget's `master`/`parent` argument (it's the common base of `Tk`, `Frame`, `Toplevel`).
- Use `tk.Event` for `bind` handlers, but you can mark `_event: tk.Event` if you don't use it.

## 14. Testing Conventions

- Unit-test models and helpers — they don't depend on tkinter.
- For GUI code: instantiate the app but don't call `mainloop()`. Drive via `var.set()`, `widget.invoke()`, and `event_generate()`.
- Use `pytest`. Keep tests in `tests/`, mirroring the source layout.

## 15. Git Conventions

- Commit messages: imperative mood, ≤72-char subject line, optional body.
  - `Add email validation to contact form`
  - `Fix crash when recent files list is empty`
- Keep commits small and focused — one feature or fix per commit.

## 16. Linting & Formatting

- **`ruff`** for linting: fast, configurable.
- **`black`** for formatting: opinionated, no config needed.
- **`mypy`** for type checking (optional but valuable).

Suggested `pyproject.toml` snippet:

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "W", "B", "UP"]
ignore = ["E501"]   # let black handle line length

[tool.mypy]
strict = true
```

## 17. Code Review Checklist

Before requesting review, verify:

- [ ] Every widget has a layout call (`pack` / `grid` / `place`).
- [ ] Every `PhotoImage` is held by an attribute.
- [ ] No `time.sleep()` on the GUI thread.
- [ ] No widget touched from a worker thread.
- [ ] All `command=` callbacks are functions, not calls.
- [ ] `bind` handlers use the correct event specifier (`<Return>` not `<Enter>` for keys — `Enter` is mouse enter!).
- [ ] All public classes and methods have docstrings.
- [ ] Type hints on public methods.
- [ ] No `from tkinter import *`.
- [ ] Layout resizes gracefully when the window grows.

## 18. Accessibility Checklist

- [ ] Keyboard focus is set to a sensible widget on startup.
- [ ] All buttons are reachable via Tab.
- [ ] Menus have `underline=` mnemonics.
- [ ] Color is never the only indicator of state — pair with text or icon.
- [ ] Use `TkDefaultFont` so the user's system font scaling is respected.
- [ ] Test with the OS's high-contrast mode.
