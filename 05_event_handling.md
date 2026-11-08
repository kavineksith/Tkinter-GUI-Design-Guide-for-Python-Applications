# 5. Event Handling

Events are how widgets respond to the user. Tkinter exposes them via three mechanisms:

1. **`command=`** — a simple callback for the most common action of a widget.
2. **`bind()`** — fine-grained, low-level event binding to any widget.
3. **Virtual events** (`<<TreeviewSelect>>`, `<<NotebookTabChanged>>`, `<<ComboboxSelected>>`) — semantic events emitted by ttk widgets.

## 5.1 The `command` Option (Simplest)

For buttons, checkboxes, radiobuttons, etc., the simplest way to react is the `command=` option:

```python
def on_click():
    print("Clicked")

ttk.Button(root, text="OK", command=on_click).pack()
```

> **Gotcha:** Pass the *function object* (`on_click`), not a *call* (`on_click()`). Calling it would run the function once at construction time and pass its return value (usually `None`) as the command — your button would do nothing.

To pass arguments, use `lambda`:

```python
for name in ("Alice", "Bob", "Carol"):
    ttk.Button(root, text=name, command=lambda n=name: greet(n)).pack()
```

The `n=name` default-binding trick captures the current value of `name` for each iteration. Without it, every button would print "Carol" (the last value of `name`).

## 5.2 `bind` and the Event Object

`bind` lets you respond to any event Tk knows about. The handler receives a `tkinter.Event` object.

```python
def on_key(event):
    print(f"Key: {event.keysym}, char: {event.char!r}, code: {event.keycode}")

root.bind("<Key>", on_key)

def on_motion(event):
    print(f"Mouse at ({event.x}, {event.y}) relative to widget, "
          f"({event.x_root}, {event.y_root}) on screen")

canvas.bind("<Motion>", on_motion)
```

### Common event specifiers

| Specifier | Fires when |
|---|---|
| `"<Button-1>"` | Left mouse button pressed (down). |
| `"<ButtonRelease-1>"` | Left mouse button released (up). |
| `"<Double-Button-1>"` | Double-click. |
| `"<Motion>"` | Mouse moves. |
| `"<Enter>"` / `"<Leave>"` | Cursor enters / leaves the widget. |
| `"<Key>"` | Any key pressed. |
| `"<Return>"` | Enter key pressed. |
| `"<Escape>"` | Esc key. |
| `"<Control-s>"` | Ctrl+S. |
| `"<Control-Shift-S>"` | Ctrl+Shift+S (case-sensitive modifier name). |
| `"<F1>"` | F1 function key. |
| `"<Configure>"` | Widget resized / moved. |
| `"<FocusIn>"` / `"<FocusOut>"` | Widget gained / lost keyboard focus. |

### The `Event` object attributes

| Attribute | Type | Meaning |
|---|---|---|
| `widget` | Widget | The widget the event was delivered to. |
| `x`, `y` | int | Cursor position relative to the widget. |
| `x_root`, `y_root` | int | Cursor position relative to the screen. |
| `num` | int | Mouse button number (1, 2, 3). |
| `char` | str | Single character produced (empty for special keys). |
| `keysym` | str | Symbolic name: `"Return"`, `"a"`, `"F1"`. |
| `keycode` | int | Numeric keycode (platform-dependent). |
| `state` | int | Bitmask of modifiers (Ctrl, Shift, Alt, mouse buttons). |
| `width`, `height` | int | New size (for `<Configure>`). |
| `delta` | int | Mouse wheel delta (Windows / macOS). |

### Mouse wheel

| Platform | Event | Read |
|---|---|---|
| Windows / macOS | `"<MouseWheel>"` | `event.delta` (positive = up) |
| Linux/X11 | `"<Button-4>"` / `"<Button-5>"` | 4 = up, 5 = down |

To make wheel-scroll cross-platform, bind both — see `examples/07_event_handling.py`.

## 5.3 Bind Scope: Widget vs Class vs Application vs All

`bind` has three siblings — they differ in scope:

| Method | Scope |
|---|---|
| `widget.bind(seq, handler)` | Just this widget. |
| `widget.bind_class("Entry", seq, handler)` | All instances of the class. |
| `widget.bind_all(seq, handler)` | The whole application — every widget receives it. |

`bind_all` is the right tool for **global shortcuts** like Ctrl+S to save:

```python
root.bind_all("<Control-s>", lambda e: self.save_document())
```

## 5.4 Modifiers and Chords

| Modifier | Syntax |
|---|---|
| Shift | `Shift-` |
| Ctrl | `Control-` (also `Ctrl-` on some platforms) |
| Alt | `Alt-` |
| Cmd (macOS) | `Command-` |
| Mouse button | `B1-`, `B2-`, `B3-` (held while moving) |
| Double-click | `Double-` |
| Triple-click | `Triple-` |

Order matters: modifiers go first, then the key. `"<Control-Shift-A>"` not `"<Shift-Control-A>"` — actually both work, but stick to a consistent order.

## 5.5 Returning `"break"` to Suppress Default Behavior

By default, Tkinter does its built-in action **after** your handler runs. For example, typing in an `Entry` both fires your `"<Key>"` handler *and* inserts the character.

Returning the string `"break"` from your handler stops the default behavior:

```python
def block_digits(event):
    if event.char.isdigit():
        return "break"   # don't let digits into the entry
entry.bind("<Key>", block_digits)
```

Use this for things like:
- Custom autocomplete (you handle the key, suppress default insertion).
- Preventing paste of certain content.
- Implementing modal shortcuts.

## 5.6 Virtual Events (ttk widgets)

ttk widgets emit **semantic** events you can bind to:

| Widget | Virtual Event |
|---|---|
| `ttk.Combobox` | `<<ComboboxSelected>>` |
| `ttk.Notebook` | `<<NotebookTabChanged>>` |
| `ttk.Treeview` | `<<TreeviewSelect>>`, `<<TreeviewOpen>>`, `<<TreeviewClose>>` |
| `ttk.Entry` | `<<Paste>>`, `<<Copy>>`, `<<Cut>>` |
| Any widget | `<<Invoke>>` (custom; you can `event_generate`) |

```python
combo.bind("<<ComboboxSelected>>", lambda e: print(combo.get()))
```

These are better than binding raw `"<Button-1>"` because they fire for *all* selection mechanisms (mouse, keyboard, programmatic).

## 5.7 `after`, `after_idle`, and `after_cancel`

`after` schedules a callback to run on the GUI thread after N milliseconds. This is the **only** correct way to do timers, polling, or to push work back from another thread.

```python
def poll_status():
    label.config(text=f"Status: {read_sensor()}")
    root.after(1000, poll_status)    # re-schedule self

root.after(1000, poll_status)
```

- `root.after(0, fn)` runs `fn` ASAP on the GUI thread — use this to marshal from a worker thread.
- `root.after_idle(fn)` runs `fn` when the GUI is next idle (after pending events).
- `after_id = root.after(ms, fn); root.after_cancel(after_id)` cancels a pending callback.

## 5.8 `wait_variable`, `wait_window`, `wait_visibility`

These block until a condition is met, while still pumping events:

```python
top = tk.Toplevel(root)
# ... build the dialog ...
self.result = tk.StringVar()
btn = ttk.Button(top, text="OK", command=lambda: self.result.set("ok"))
btn.pack()
top.wait_variable(self.result)   # blocks here, but UI stays responsive
top.destroy()
```

`wait_window(top)` is what makes a dialog **modal**: the call blocks until `top` is destroyed.

## 5.9 A Pattern: Command Object / Method Binding

For non-trivial apps, prefer methods to lambdas:

```python
class App:
    def __init__(self, root):
        ttk.Button(root, text="Save", command=self.on_save).pack()

    def on_save(self):
        path = filedialog.asksaveasfilename()
        if path:
            self.save_to(path)
```

Methods get access to `self`, so they can read/write the app state. Lambdas are fine for tiny one-offs.

## 5.10 What's Next

Read `06_architecture_patterns.md` for how to structure an app larger than a single file.
