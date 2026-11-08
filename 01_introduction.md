# 1. Introduction to Tkinter

## 1.1 What Is Tkinter?

`tkinter` is Python's standard interface to the **Tk GUI toolkit**. Tk was originally written for the Tcl language in 1991; Python wraps it with a thin, stable, object-oriented layer. Because Tk ships with Python, `tkinter` is the only GUI library that requires **zero dependencies** — `import tkinter` just works on Windows, macOS, and most Linux installs.

Key facts:

- **Cross-platform**: same code runs on Windows, macOS, and Linux/X11.
- **Built-in**: included with the official CPython installer since Python 1.5.
- **Stable API**: a script written in 2005 still runs today.
- **Single-threaded**: the GUI loop owns the main thread. Long-running work must be offloaded (see `08_advanced_topics.md`).
- **Not the prettiest by default**: modern styling requires `ttk` and careful theming (see `04_styling_and_theming.md`).

## 1.2 When to Use Tkinter (and When Not To)

**Use tkinter when:**

- You need a desktop tool, not a web app.
- Your users run Windows, macOS, or Linux desktops.
- You want to ship a single `.py` file or a small `.exe` with no heavy dependencies.
- Your UI is forms, tables, lists, canvases — standard business-UI territory.
- You are prototyping an internal tool.

**Consider alternatives when:**

- You need GPU-accelerated 3D rendering → use `pyopengl` or `pygame`.
- You need a web-native interface → use `Streamlit`, `Gradio`, or a web framework.
- You want pixel-perfect modern animations and a designer-driven workflow → use `PyQt6`/`PySide6` (Qt) or `PyGObject` (GTK).
- You are targeting mobile → tkinter does not run on iOS/Android.

## 1.3 The Mental Model

Every tkinter program has three layers:

```
┌──────────────────────────────────────────────┐
│  1. Tk root window      (the application)    │
│   └─ 2. Widgets         (buttons, entries…)  │
│        └─ 3. Layout     (where they sit)     │
└──────────────────────────────────────────────┘
            ▲
            │  events: clicks, key presses, resizes
            ▼
   4. mainloop()    (the event pump that drives it all)
```

1. **`Tk()`** — the application root window. There is exactly one per process.
2. **Widgets** — instances of `Button`, `Entry`, `Frame`, etc. Widgets form a tree: every widget except the root has a parent.
3. **Layout managers** — `pack`, `grid`, or `place`. They decide where each widget appears within its parent.
4. **`mainloop()`** — the event loop. It blocks forever, dispatching events to widgets, until the root window is destroyed.

## 1.4 Hello, World — Annotated

The smallest meaningful tkinter program:

```python
"""Hello, World — the smallest meaningful tkinter program."""
import tkinter as tk

# 1. Create the application root window.
root = tk.Tk()
root.title("Hello")
root.geometry("300x150")

# 2. Create a label widget whose parent is `root`.
label = tk.Label(root, text="Hello, World!")
label.pack(padx=20, pady=20)  # 3. Place it inside the window with pack().

# 4. Start the event loop. This call BLOCKS until the window is closed.
root.mainloop()
```

Run it:

```bash
python examples/01_hello_world.py
```

What happens when you run it:

1. `tk.Tk()` contacts the window manager and creates a real OS window.
2. `tk.Label(...)` creates a label *object* in Python but does not yet paint anything.
3. `label.pack(...)` tells tkinter "put this label inside its parent, give it 20px padding on each side". Only now is it laid out and painted.
4. `root.mainloop()` enters the event loop. The script "freezes" here, but the window is alive and responsive.
5. When you close the window, `mainloop()` returns and the script ends.

## 1.5 The Widget Tree

Every widget has a **parent** (the widget it lives inside) and zero or more **children**. The root window (`tk.Tk()`) is the ultimate parent.

```python
root = tk.Tk()
frame = tk.Frame(root)          # frame's parent is root
button = tk.Button(frame)       # button's parent is frame
```

- Destroying a parent automatically destroys all its children.
- Hiding a parent hides all its children.
- The tree is what lets `grid` and `pack` work locally — each parent arranges only its direct children.

## 1.6 Synchronous, Single-Threaded

Tkinter is **not thread-safe**. Only the thread that called `mainloop()` may touch widgets. If you do background work in another thread, you must marshal updates back to the GUI thread with `root.after(0, callback)`. See `examples/16_multithreading.py` and `08_advanced_topics.md` § 4.

## 1.7 Key Terms Glossary

| Term | Meaning |
|---|---|
| **root** | The single `Tk()` instance; the application's main window. |
| **widget** | A UI element — a button, label, entry, frame, etc. |
| **parent / child** | The container / contained relationship between widgets. |
| **geometry manager** | `pack`, `grid`, or `place`; positions widgets inside their parent. |
| **event** | A user action (click, key press, resize) delivered as a `tkinter.Event` object. |
| **binding** | Connecting an event to a callable via `widget.bind("<Button-1>", handler)`. |
| **callback** | A function invoked when an event or command fires. |
| **mainloop** | The never-return-until-quit event pump. |
| **ttk** | The "themed" widget set, introduced in Tk 8.5, recommended for new code. |

## 1.8 What's Next

Read `02_widgets.md` for a tour of the available widgets, then `03_layout_managers.md` for how to position them.
