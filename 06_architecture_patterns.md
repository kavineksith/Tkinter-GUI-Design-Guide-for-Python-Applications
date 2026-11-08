# 6. Architecture Patterns

A 50-line script can put everything in one file. A 5000-line app cannot. This section covers the patterns that keep tkinter code maintainable as it grows.

## 6.1 The Single-File Anti-Pattern

Beginners tend to write code like this:

```python
import tkinter as tk

root = tk.Tk()
root.title("Calculator")

# ... 800 lines of widget creation, callbacks, and logic intermixed ...

root.mainloop()
```

This works until the file hits ~300 lines, then it becomes unmaintainable. The cure is to introduce **structure**.

## 6.2 Pattern 1: Application Class

The smallest step up from the anti-pattern. Wrap the entire app in a class so callbacks can be methods and state lives on `self`.

```python
"""Minimal 'Application class' pattern."""
import tkinter as tk
from tkinter import ttk


class App:
    """Top-level application object.

    Owns the root window, the widget tree, and the user-facing callbacks.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("App Class Demo")
        self.root.geometry("400x200")
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the widget tree. Called once during init."""
        self.label = ttk.Label(self.root, text="Hello")
        self.label.pack(padx=20, pady=20)
        ttk.Button(self.root, text="Click", command=self.on_click).pack()

    def on_click(self) -> None:
        """Increment the click counter and update the label."""
        self._count = getattr(self, "_count", 0) + 1
        self.label.config(text=f"Clicked {self._count} times")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
```

**Benefits:**
- All state lives on `self` — no globals.
- Callbacks are methods — they have access to `self`.
- The constructor signature (`App(root)`) is testable: you can pass in a mock root.

## 6.3 Pattern 2: Model–View–Controller (MVC)

When logic gets complex, separate it into three layers:

| Layer | Responsibility | Example |
|---|---|---|
| **Model** | Domain data and business rules. Pure Python, no tkinter. | `class ContactBook` with `add`, `remove`, `search`. |
| **View** | Widget construction and pure UI events. Reads from model, calls controller methods. | `class ContactView` builds the form, tree, buttons. |
| **Controller** | Wires View to Model. Handles user actions. | `class ContactController` calls `model.add(...)` then refreshes `view`. |

```
┌──────────┐  calls   ┌─────────────┐  calls   ┌───────┐
│   View   │ ───────► │ Controller  │ ───────► │ Model │
│ (tkinter)│ ◄─────── │             │ ◄─────── │       │
└──────────┘ observes └─────────────┘ returns   └───────┘
```

The model has **no reference** to the view or controller. The view has **no direct reference** to the model — only the controller bridges them. This makes the model unit-testable without a GUI.

See `examples/14_mvc_pattern.py` for a complete working example, and `templates/mvc_template.py` for a copy-paste scaffold.

## 6.4 Pattern 3: Observer / Pub-Sub

When the model changes, the view should update. Instead of the controller calling `view.refresh()` after every change, use the **observer pattern**:

```python
class Observable:
    """Minimal observable. Listeners are called whenever the value changes."""

    def __init__(self, value=None):
        self._value = value
        self._listeners = []

    def get(self):
        return self._value

    def set(self, value):
        if value != self._value:
            self._value = value
            for listener in self._listeners:
                listener(self._value)

    def subscribe(self, fn):
        self._listeners.append(fn)
        fn(self._value)   # fire immediately so the view shows current state
```

Now the model can broadcast changes; the view subscribes; the controller stays thin. This decouples the view from knowing *which* model methods mutate state.

## 6.5 Pattern 4: tk.Variable as a Mini-View-Model

For simple forms, you don't need a full controller. `tk.StringVar` / `IntVar` / `DoubleVar` are themselves **observable** — call `.trace_add("write", callback)` to react whenever the value changes:

```python
self.amount_var = tk.StringVar()
self.amount_var.trace_add("write", self._on_amount_change)

def _on_amount_change(self, *_):
    try:
        amount = float(self.amount_var.get())
        self.tax_label.config(text=f"Tax: ${amount * 0.13:.2f}")
    except ValueError:
        self.tax_label.config(text="—")
```

This is essentially **data binding**: the label updates whenever the input changes, with no explicit "refresh" call.

## 6.6 Pattern 5: Multi-Window Apps

For an app with several screens (login → dashboard → settings), use `ttk.Notebook` if the screens are tabs, or stack `Frame`s and raise/lower them:

```python
class Router:
    """Holds references to all 'screens' and shows the requested one."""

    def __init__(self, container):
        self.container = container
        self.screens = {}

    def register(self, name, frame):
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.screens[name] = frame
        self.show(name)

    def show(self, name):
        for frame in self.screens.values():
            frame.place_forget()
        self.screens[name].place(relx=0, rely=0, relwidth=1, relheight=1)
```

Each "screen" is a `ttk.Frame` populated by its own builder function. The router shows one at a time. This avoids `Toplevel` for in-app navigation, which is jarring.

## 6.7 Pattern 6: Dependency Injection

If your controller needs a database, a config, a logger — pass them in:

```python
class App:
    def __init__(self, root, db, config, logger):
        self.db = db
        self.config = config
        self.logger = logger
        self.controller = ContactController(db, logger)
        self.view = ContactView(root, self.controller)
```

This is what makes the app **testable** — in tests, you pass in a mock DB and a list-capturing logger instead of real ones.

## 6.8 File Layout for a Medium-Sized App

```
myapp/
├── main.py                ← entry point, builds Tk(), starts mainloop
├── app/
│   ├── __init__.py
│   ├── config.py          ← loads settings, defines constants
│   ├── models/
│   │   ├── contact.py     ← pure-Python domain objects
│   │   └── repository.py  ← persistence (DB, file, API)
│   ├── views/
│   │   ├── main_window.py
│   │   ├── contact_form.py
│   │   └── settings_dialog.py
│   ├── controllers/
│   │   └── contact_controller.py
│   └── styles/
│       └── theme.py       ← ttk.Style setup
└── tests/
    └── test_models.py
```

Rules:
- `main.py` is short — just wire dependencies and start the loop.
- `models/` imports **nothing** from `tkinter`.
- `views/` may import ttk but never reach into business logic — they call the controller.
- `controllers/` may import models and views, but it's cleaner if controllers don't import views directly — they should be passed the view via constructor injection.

## 6.9 What's Next

Read `07_best_practices.md` for the small rules that keep even a small app clean.
