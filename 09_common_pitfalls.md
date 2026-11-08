# 9. Common Pitfalls

A catalog of the classic mistakes that bite tkinter beginners, with the symptom, cause, and fix for each.

---

## 9.1 "My callback runs once at startup and never again"

**Symptom:** You set `command=callback()`, the function runs during widget construction, and clicking the button does nothing.

**Cause:** Python evaluates `callback()` immediately. The return value (usually `None`) becomes the `command`. Clicks call `None()` — nothing happens.

**Fix:** Pass the function object, not a call.
```python
# Wrong:
ttk.Button(parent, text="OK", command=on_ok())

# Right:
ttk.Button(parent, text="OK", command=on_ok)

# To pass arguments:
ttk.Button(parent, text="OK", command=lambda: on_ok(42))
```

---

## 9.2 "My buttons/images disappear"

**Symptom:** A `PhotoImage` set on a button or label appears briefly or never appears.

**Cause:** `tkinter.PhotoImage` objects are garbage-collected if you don't keep a reference. Tk keeps a *handle*, not a *reference* — Python frees the underlying image.

**Fix:** Store the image as an attribute of something long-lived.
```python
# Wrong (local variable, GC'd):
ttk.Button(parent, image=tk.PhotoImage(file="icon.png")).pack()

# Right:
self.icon = tk.PhotoImage(file="icon.png")
ttk.Button(parent, image=self.icon).pack()
```

---

## 9.3 "Mixing pack and grid freezes the app"

**Symptom:** App hangs on startup. Sometimes prints `"_tkinter.TclError: cannot use geometry manager pack inside .!frame which already has slaves managed by grid"`.

**Cause:** You called `.pack()` and `.grid()` on widgets with the same parent. Tkinter can't decide which wins and the layout manager deadlocks.

**Fix:** Pick one manager per parent. Use `Frame`s to mix managers safely across regions.

---

## 9.4 "Long task freezes the whole window"

**Symptom:** You click "Process" and the window stops responding — can't be moved, can't be resized, "Not Responding" appears on Windows.

**Cause:** Your callback is blocking the event loop. While your code runs, Tkinter cannot paint, cannot process clicks, cannot respond to window manager.

**Fix:** Move slow work to a thread (see `08_advanced_topics.md` § 8.3 and `examples/16_multithreading.py`).
```python
# Wrong:
def on_process():
    result = blocking_network_call()    # freezes UI
    show(result)

# Right:
def on_process():
    self.process_btn.config(state="disabled")
    threading.Thread(target=self._worker, daemon=True).start()

def _worker(self):
    result = blocking_network_call()
    self.root.after(0, lambda: self._on_done(result))

def _on_done(self, result):
    show(result)
    self.process_btn.config(state="normal")
```

---

## 9.5 "Calling time.sleep() freezes the UI"

**Symptom:** You wrote `time.sleep(1)` in a callback hoping for a delay; the entire app freezes for a second.

**Cause:** Same as 9.4 — `time.sleep` blocks the calling thread, which is the GUI thread.

**Fix:** Use `after`:
```python
# Wrong:
def on_flash():
    label.config(text="Hi")
    time.sleep(2)
    label.config(text="")

# Right:
def on_flash():
    label.config(text="Hi")
    root.after(2000, lambda: label.config(text=""))
```

---

## 9.6 "Multithreading crashes with a segfault"

**Symptom:** A worker thread updates a widget directly. Crashes randomly with `X Error of failed request: BadWindow` or a segfault.

**Cause:** Tkinter is not thread-safe. Touching widgets from any thread other than the main one is undefined behavior.

**Fix:** Always marshal back with `root.after(0, fn)` or a `queue.Queue`.

---

## 9.7 "Reading an Entry returns empty"

**Symptom:** `entry.get()` returns `""` even though the user typed text.

**Cause:** You created the entry without `textvariable=` and the entry's text isn't synchronized to the variable you're reading. Or you called `entry.get()` before the user had a chance to type (e.g., during construction).

**Fix:** Either read from the widget (`entry.get()`) directly, **or** attach a `tk.StringVar` and read from the variable. Don't mix the two.
```python
self.name_var = tk.StringVar()
ttk.Entry(form, textvariable=self.name_var).pack()
# later:
print(self.name_var.get())
```

---

## 9.8 "Window opens tiny / off-screen / hidden"

**Symptom:** Window appears at 1×1 pixel size, or off-screen, or behind other windows.

**Cause:** You forgot to set `geometry` and `minsize`, or your saved geometry is corrupt.

**Fix:**
```python
root.geometry("800x600")          # initial size
root.minsize(400, 300)             # user can't shrink below this
root.deiconify()                   # un-iconify if it was hidden
root.lift()                        # bring to front
root.attributes("-topmost", True)
root.after_idle(lambda: root.attributes("-topmost", False))   # then release
```

---

## 9.9 "tk.Tk() called twice creates two icons"

**Symptom:** On Windows, two taskbar icons appear for your app — one is a phantom.

**Cause:** You called `tk.Tk()` more than once, or you created `Toplevel` windows and Tkinter's window class isn't set.

**Fix:** Always have exactly one `Tk()` instance. For taskbar grouping on Windows, set the window class via a `.bat`/`.exe` wrapper or `app_id` setting via `ctypes`.

---

## 9.10 "Window close doesn't terminate the app"

**Symptom:** User clicks the X button; the window closes but Python keeps running. Or: a `Toplevel` close quits the whole app.

**Cause:** `Toplevel` close doesn't quit the app by default — only closing `Tk()` does. If you bound `WM_DELETE_WINDOW` to `root.destroy` on a Toplevel, that's the bug.

**Fix:** Use `protocol("WM_DELETE_WINDOW", handler)` carefully. For the root window:
```python
def on_close():
    if messagebox.askokcancel("Quit", "Really quit?"):
        root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)
```

For a Toplevel:
```python
def on_close_dialog(dialog):
    dialog.grab_release()   # release modal grab if any
    dialog.destroy()
top.protocol("WM_DELETE_WINDOW", lambda: on_close_dialog(top))
```

---

## 9.11 "Layout doesn't resize when window grows"

**Symptom:** Window grows; widgets stay crowded in the top-left.

**Cause:** You used `pack()` without `expand=True, fill="both"`, or `grid()` without `columnconfigure(weight=1)` / `rowconfigure(weight=1)`.

**Fix:**
```python
# pack:
content.pack(fill="both", expand=True)

# grid:
parent.columnconfigure(0, weight=1)
parent.rowconfigure(0, weight=1)
widget.grid(row=0, column=0, sticky="nsew")
```

---

## 9.12 "Validatecommand isn't firing"

**Symptom:** You set `validatecommand=` on an `Entry` but it doesn't trigger.

**Cause:** Two common causes — (1) you returned the wrong value and Tk disabled the validator, (2) you called `entry.set()` programmatically and Tk disabled the validator after.

**Fix:** Always use `validatecommand` with a registered function returning `"yes"`/`True`, and set `validate="key"` explicitly. Re-enable after programmatic updates:
```python
vcmd = (entry.register(self._validate), "%P")
entry.config(validate="key", validatecommand=vcmd)

# After programmatic update:
entry.config(validate="none")
entry.delete(0, "end"); entry.insert(0, "value")
entry.config(validate="key")
```

---

## 9.13 "Treeview selection is empty"

**Symptom:** `tree.selection()` returns `()` even though you can see a selected row.

**Cause:** The selection is cleared by the time your callback runs because the Treeview internally processes events after yours, or you selected an item programmatically before it had focus.

**Fix:** Bind `<<TreeviewSelect>>`, not `<Button-1>`, and check `tree.selection()` inside the handler.

---

## 9.14 "Fonts look different on every machine"

**Symptom:** Your UI looks great on Windows, ugly on Linux.

**Cause:** Hardcoded font names like `("Arial", 10)` — Arial isn't installed on Linux.

**Fix:** Use `TkDefaultFont` everywhere. Override globally with `nametofont` to apply your own font consistently. Never hardcode a font in a widget.

---

## 9.15 "Scrolling doesn't work with Text / Treeview / Canvas"

**Symptom:** You added a `Scrollbar` and wired up `yscrollcommand=` but the scrollbar doesn't move when content scrolls.

**Cause:** You forgot to also wire `command=` on the scrollbar, OR you forgot to also call `xview`/`yview` on the widget.

**Fix:**
```python
scrollbar = ttk.Scrollbar(parent, orient="vertical")
text = tk.Text(parent, yscrollcommand=scrollbar.set)
scrollbar.config(command=text.yview)

# Critical: both directions are needed. .set updates the scrollbar thumb;
# .yview tells the scrollbar what to scroll.
```

Use a helper to wire both at once:
```python
def attach_scrollbar(widget, scrollbar, orient="vertical"):
    if orient == "vertical":
        widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=widget.yview)
    else:
        widget.config(xscrollcommand=scrollbar.set)
        scrollbar.config(command=widget.xview)
```

---

## 9.16 "TclError: image doesn't exist"

**Symptom:** `tk.PhotoImage(file="x.png")` raises `TclError: couldn't open "x.png": no such file or directory`.

**Cause:** Tkinter looks for the file in the **current working directory**, not next to your script. If you ran `python myapp/main.py` from `/home/user`, it looks in `/home/user/`.

**Fix:** Resolve paths against `__file__`:
```python
from pathlib import Path
ASSET_DIR = Path(__file__).parent / "assets"
icon = tk.PhotoImage(file=ASSET_DIR / "logo.png")
```

---

## 9.17 "Application is stuck after messagebox"

**Symptom:** You show `messagebox.showerror(...)`, click OK, and the app hangs.

**Cause:** The messagebox was created in a worker thread, or the parent window passed to it was already destroyed.

**Fix:** Always show messageboxes from the GUI thread, and pass a live parent:
```python
root.after(0, lambda: messagebox.showerror("Error", "Something failed", parent=root))
```

---

## 9.18 "Mouse wheel doesn't scroll on Linux"

**Symptom:** Mouse wheel scrolling works on Windows/macOS but not on Linux.

**Cause:** Linux/X11 uses `<Button-4>` and `<Button-5>` instead of `<MouseWheel>`.

**Fix:** Bind both, and use a helper to read either:
```python
def on_wheel(event):
    delta = event.delta if hasattr(event, "delta") and event.delta else (
        120 if event.num == 4 else -120
    )
    canvas.yview_scroll(int(-delta / 120), "units")

# Windows / macOS
canvas.bind("<MouseWheel>", on_wheel)
# Linux
canvas.bind("<Button-4>", on_wheel)
canvas.bind("<Button-5>", on_wheel)
```

---

## 9.19 "Modifying a window from another thread 'sometimes' works"

**Symptom:** Your multi-threaded code works on your machine, crashes on a user's.

**Cause:** Race condition. Sometimes Tkinter survives a cross-thread call. Sometimes it doesn't.

**Fix:** See 9.6 — never call widgets from another thread. Always `root.after(0, ...)`.

---

## 9.20 "I used `entry.delete(0, END)` and got a NameError"

**Symptom:** `NameError: name 'END' is not defined`.

**Cause:** `END`, `INSERT`, `CURRENT`, etc., are attributes of `tkinter` (the module), not builtins.

**Fix:** Either `from tkinter import *` (discouraged) or use `"end"`, `"insert"`, `"current"` as string literals — Tkinter accepts both the constant and the string.

---

## 9.21 Closing Checklist

When something doesn't work, run through this checklist before searching Stack Overflow:

1. Did you call `.pack()` / `.grid()` / `.place()` on the widget?
2. Did you pass the function (not a call) to `command=`?
3. Did you keep a reference to every `PhotoImage`?
4. Are you mixing geometry managers in the same parent?
5. Are you doing any blocking work on the GUI thread?
6. Are you touching widgets from another thread?
7. Did you set `validate=` correctly on validated entries?
8. Did you wire both `yscrollcommand=` and `command=` on scrollbars?
9. Are you hardcoding fonts instead of using `TkDefaultFont`?
10. Are you using `tk.Tk()` only once?
