# 8. Advanced Topics

This section covers the techniques that go beyond the basics: custom widgets, multithreading, drag-and-drop, theming tricks, and platform-specific behavior.

## 8.1 Custom Widgets via Composition

The simplest "custom widget" is just a `Frame` containing other widgets, exposed as a class:

```python
class LabeledEntry(ttk.Frame):
    """A label + entry combo widget.

    Args:
        master: parent widget.
        label: text for the left-hand label.
        **kwargs: forwarded to the internal ttk.Entry.
    """

    def __init__(self, master, label="", **kwargs):
        super().__init__(master)
        self._var = tk.StringVar()
        self.label = ttk.Label(self, text=label)
        self.entry = ttk.Entry(self, textvariable=self._var, **kwargs)
        self.label.grid(row=0, column=0, sticky="e", padx=(0, 4))
        self.entry.grid(row=0, column=1, sticky="ew")
        self.columnconfigure(1, weight=1)

    def get(self):
        return self._var.get()

    def set(self, value):
        self._var.set(value)
```

Use it like any built-in widget:

```python
field = LabeledEntry(form, label="Email:")
field.pack(fill="x")
```

This is the **composition pattern**. It's almost always preferable to subclassing ttk widgets directly, because ttk's internals are not designed for subclassing.

## 8.2 Custom Widgets via `Canvas`

For truly custom drawing (gauges, charts, game boards), subclass `tk.Canvas`:

```python
class Gauge(tk.Canvas):
    """A circular gauge showing a value 0..1.

    Args:
        master: parent widget.
        size: canvas width and height in pixels.
    """

    def __init__(self, master, size=120, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)
        self._value = 0.0
        self._size = size
        self._arc = self.create_arc(
            [10, 10, size - 10, size - 10],
            start=90, extent=0, style="arc",
            width=10, outline="#1565D8",
        )
        self._label = self.create_text(
            size // 2, size // 2, text="0%", font=("TkDefaultFont", 14, "bold"),
        )

    def set_value(self, value: float) -> None:
        """Set the gauge value (0..1) and redraw."""
        self._value = max(0.0, min(1.0, value))
        # Arc draws clockwise from the start angle. 90° start = 12 o'clock.
        self.itemconfig(self._arc, extent=-self._value * 360)
        self.itemconfig(self._label, text=f"{self._value * 100:.0f}%")
```

## 8.3 Multithreading: The Right Way

Tkinter is single-threaded. Only the thread that called `mainloop()` may touch widgets. There are two safe patterns:

### Pattern A: `root.after(0, ...)` for occasional updates

```python
import threading

def worker():
    result = slow_computation()
    root.after(0, lambda: result_label.config(text=str(result)))

threading.Thread(target=worker, daemon=True).start()
```

`root.after(0, fn)` schedules `fn` to run on the GUI thread as soon as the event loop is free. The worker never touches widgets directly.

### Pattern B: `queue.Queue` for continuous streaming

For long-running workers that emit many updates (logs, progress):

```python
import queue, threading

class Worker:
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        for i in range(100):
            self.queue.put(i)
            time.sleep(0.05)
        self.queue.put(None)   # sentinel: done

# On the GUI thread, drain the queue every 100 ms:
def poll():
    try:
        while True:
            msg = worker.queue.get_nowait()
            if msg is None:
                return   # stop polling
            progressbar['value'] = msg
    except queue.Empty:
        pass
    root.after(100, poll)

worker = Worker()
worker.start()
poll()
```

### The `threading.Thread(daemon=True)` rule

Mark worker threads as **daemon** so they don't keep the process alive after the user closes the window. Without `daemon=True`, the process will hang on exit waiting for the thread to finish.

## 8.4 `after` for Periodic Tasks

```python
class Clock:
    def __init__(self, root, label):
        self.label = label
        self.tick()   # start the loop

    def tick(self):
        self.label.config(text=time.strftime("%H:%M:%S"))
        self.label.after(1000, self.tick)   # schedule next tick
```

Important: **always re-schedule the next `after` at the end of the callback**. If you raise an exception, the loop stops — wrap in try/except if the periodic task must keep going.

## 8.5 Drag-and-Drop within the Same App

Implement drag-and-drop manually using mouse events:

```python
class Draggable:
    """Mixin: makes a Canvas item draggable with the mouse."""

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item
        canvas.tag_bind(item, "<Button-1>", self.on_press)
        canvas.tag_bind(item, "<ButtonRelease-1>", self.on_release)
        canvas.tag_bind(item, "<B1-Motion>", self.on_motion)
        self._drag_data = {"x": 0, "y": 0}

    def on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_motion(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(self.item, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_release(self, event):
        pass
```

For OS-level drag-and-drop of files from the desktop, use the third-party `tkinterdnd2` library — tkinter has no built-in support.

## 8.6 Clipboard

```python
root.clipboard_clear()
root.clipboard_append("Copied text")
root.update()   # required to flush to the OS clipboard

text = root.clipboard_get()
```

Always call `update()` after `clipboard_append` — without it, the OS may never see the new content (the clipboard is held only while the app is alive, and `update()` forces the IPC).

## 8.7 Printing / Logging to the UI

For an app with a log panel:

```python
import logging

class TextHandler(logging.Handler):
    """A logging.Handler that writes to a tk.Text widget, thread-safe."""

    def __init__(self, text_widget):
        super().__init__()
        self.text = text_widget

    def emit(self, record):
        msg = self.format(record) + "\n"
        # Marshal to the GUI thread.
        self.text.after(0, lambda m=msg: self._append(m))

    def _append(self, msg):
        self.text.configure(state="normal")
        self.text.insert("end", msg)
        self.text.see("end")
        self.text.configure(state="disabled")
```

Tag the lines by severity for color coding — see `examples/16_multithreading.py`.

## 8.8 Treeview as a Table

`ttk.Treeview` is tkinter's only real table. Common operations:

```python
tree = ttk.Treeview(root, columns=("name", "email"), show="headings")
tree.heading("name",  text="Name",  command=lambda: sort_by(tree, "name",  False))
tree.heading("email", text="Email")
tree.column("name",  width=200, anchor="w")
tree.column("email", width=300, anchor="w")

# Insert rows:
tree.insert("", "end", values=("Alice", "alice@example.com"))

# Read selected:
for item_id in tree.selection():
    values = tree.item(item_id, "values")
    print(values)

# Delete:
for item_id in tree.selection():
    tree.delete(item_id)
```

Use `show="headings"` for a flat list; `show="tree"` for a tree; `show="tree headings"` for a tree with columns.

## 8.9 Theming Tricks

### Dynamically switch themes (light/dark)

```python
def set_theme(style, mode):    # mode in {"light", "dark"}
    if mode == "dark":
        style.configure(".", background="#1F2937", foreground="#F9FAFB",
                        fieldbackground="#374151", bordercolor="#4B5563")
        style.configure("TLabel", background="#1F2937", foreground="#F9FAFB")
        style.configure("TButton", background="#374151", foreground="#F9FAFB")
    else:
        style.configure(".", background="#FFFFFF", foreground="#1F2937",
                        fieldbackground="#FFFFFF", bordercolor="#D1D5DB")
        style.configure("TLabel", background="#FFFFFF", foreground="#1F2937")
        style.configure("TButton", background="#E5E7EB", foreground="#1F2937")
```

After updating the root style `"."`, you may need to call `style.configure("TFrame", ...)` etc. — `clam` does not always cascade.

### Custom drawn scrollbar-less scroll area

Replace the default scrollbar with a thin custom-drawn one — but this is rarely worth the maintenance burden. Prefer the default scrollbar with the `clam` theme.

## 8.10 Platform-Specific Behavior

| Concern | Windows | macOS | Linux/X11 |
|---|---|---|---|
| Default theme | `vista` | `aqua` | `clam` |
| Menu bar location | Inside window | Top of screen (system-wide) | Inside window |
| Mouse wheel event | `<MouseWheel>` | `<MouseWheel>` | `<Button-4>` / `<Button-5>` |
| Hi-DPI | Auto with `SetProcessDpiAwareness` | Auto | Needs `GDK_SCALE` env var |
| Window border | `overrideredirect` clean | Quirky — leaves shadow | Clean |
| Right-click | `<Button-3>` | `<Button-2>` (with one-button mice) | `<Button-3>` |

For macOS menubar at the top of the screen, use the standard `root.option_add("*tearOff", False)` and add menus normally — Tk handles placement.

## 8.11 Embedding matplotlib Charts

Use `matplotlib.backends.backend_tkagg.FigureCanvasTkAgg`:

```python
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fig = Figure(figsize=(5, 3), dpi=100)
ax = fig.add_subplot(111)
ax.plot([0, 1, 2, 3], [0, 1, 4, 9])

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)
```

The matplotlib canvas is a real tkinter widget — `pack` / `grid` it like anything else.

## 8.12 What's Next

Read `09_common_pitfalls.md` so you recognize the famous "why doesn't this work?" symptoms when you hit them.
