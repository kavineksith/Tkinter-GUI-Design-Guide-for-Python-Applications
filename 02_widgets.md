# 2. The Widget Library

## 2.1 Classic vs Themed Widgets

Tkinter ships two widget sets. Use the **themed (ttk)** set as your default; reach for **classic** widgets only when ttk has no equivalent.

| Classic (`tk.*`) | Themed (`ttk.*`) | Use |
|---|---|---|
| `tk.Button` | `ttk.Button` | Clickable buttons |
| `tk.Label` | `ttk.Label` | Static text / images |
| `tk.Entry` | `ttk.Entry` | Single-line text input |
| `tk.Checkbutton` | `ttk.Checkbutton` | On/off toggle |
| `tk.Radiobutton` | `ttk.Radiobutton` | Choose one from a group |
| `tk.Frame` | `ttk.Frame` | Container with no border |
| `tk.LabelFrame` | `ttk.LabelFrame` | Container with a title border |
| `tk.Menubutton` | `ttk.Menubutton` | Button that opens a menu |
| `tk.Scale` | `ttk.Scale` | Slider for numeric values |
| `tk.Scrollbar` | `ttk.Scrollbar` | Scrollbar |
| `tk.Combobox` (none) | `ttk.Combobox` | Drop-down with edit |
| `tk.Notebook` (none) | `ttk.Notebook` | Tabbed container |
| `tk.Treeview` (none) | `ttk.Treeview` | Tabular list / tree |
| `tk.Progressbar` (none) | `ttk.Progressbar` | Indeterminate / determinate bar |
| `tk.Separator` (none) | `ttk.Separator` | Horizontal / vertical line |
| `tk.Sizegrip` (none) | `ttk.Sizegrip` | Resizable corner handle |
| `tk.PanedWindow` | `ttk.PanedWindow` | Draggable split between widgets |
| `tk.Text` (none) | — | Multi-line rich text |
| `tk.Canvas` (none) | — | 2D drawing surface |
| `tk.Menu` (none) | — | Top-level menu, context menu |
| `tk.Spinbox` | `ttk.Spinbox` | Numeric entry with up/down |
| `tk.Message` (deprecated) | — | Use `ttk.Label` with `wraplength=` |

> **Rule of thumb:** if a ttk version exists, use it. It will look native on every platform.

## 2.2 The Container Widgets

Containers do not display data themselves — they hold other widgets and let you compose complex layouts.

### `Frame`
A bare container. Use it to group related widgets or to carve a window into regions.
```python
panel = ttk.Frame(root, padding=10)
panel.pack(fill="both", expand=True)
```

### `LabelFrame`
A `Frame` with a visible border and a text label.
```python
settings = ttk.LabelFrame(root, text="Settings", padding=10)
settings.pack(fill="x", padx=10, pady=10)
```

### `Notebook`
Tabbed container. Each tab is added with `.add(child, text="Tab name")`.
```python
nb = ttk.Notebook(root)
page1 = ttk.Frame(nb); nb.add(page1, text="General")
page2 = ttk.Frame(nb); nb.add(page2, text="Advanced")
nb.pack(fill="both", expand=True)
```

### `PanedWindow`
A draggable splitter between two widgets.
```python
pw = ttk.PanedWindow(root, orient="horizontal")
pw.add(left_pane, weight=1)
pw.add(right_pane, weight=2)
pw.pack(fill="both", expand=True)
```

## 2.3 Input Widgets

| Widget | Stores | Read value | Set value |
|---|---|---|---|
| `ttk.Entry` | String | `entry.get()` | `entry.insert(0, "x")` / `entry.delete(0, "end"); entry.insert(0, "x")` |
| `ttk.Spinbox` | String | `spinbox.get()` | `spinbox.set("5")` |
| `ttk.Combobox` | String | `cb.get()` | `cb.set("option")` |
| `ttk.Checkbutton` | Int (0/1) via `IntVar` | `var.get()` | `var.set(1)` |
| `ttk.Radiobutton` | Any via `StringVar`/`IntVar` | `var.get()` | `var.set("value")` |
| `tk.Text` | Multi-line | `text.get("1.0", "end-1c")` | `text.insert("1.0", "...")` |
| `ttk.Scale` | Float | `scale.get()` | `scale.set(0.5)` |

> **Pattern:** Always attach a `tk.Variable` (`StringVar`, `IntVar`, `DoubleVar`, `BooleanVar`) to input widgets whose value you want to read elsewhere. Read the variable, not the widget — this decouples your logic from the widget instance.

```python
self.name_var = tk.StringVar()
ttk.Entry(parent, textvariable=self.name_var).pack()
# later, anywhere:
print(self.name_var.get())
```

## 2.4 Display Widgets

- **`ttk.Label`** — text or `PhotoImage`. Wrap text with `wraplength=200` (pixels).
- **`ttk.Treeview`** — the only real "table" widget. Columns, headings, sort, selection, item images, tree-style expand/collapse.
- **`ttk.Progressbar`** — set `maximum`, increment with `.step(amount)`, or run indeterminate with `mode="indeterminate"` and `.start()`.
- **`tk.Canvas`** — vector drawing: lines, rectangles, ovals, polygons, arcs, text, images, embedded widgets. Also the foundation for custom-drawn widgets and games.
- **`tk.Text`** — multi-line, styled (tags), editable, scrollable, can hold embedded images and widgets.

## 2.5 Windows & Dialogs

- **`tk.Toplevel`** — a second top-level window. Useful for modal dialogs, settings windows, "About" boxes.
- **`tkinter.messagebox`** — `showinfo`, `showwarning`, `showerror`, `askquestion`, `askyesno`, `askokcancel`, `askretrycancel`.
- **`tkinter.filedialog`** — `askopenfilename`, `asksaveasfilename`, `askdirectory`.
- **`tkinter.colorchooser`** — `askcolor`.
- **`tkinter.simpledialog`** — `askstring`, `askinteger`, `askfloat`.

## 2.6 Constructing a Widget

Every widget constructor follows the same shape:

```python
Widget(parent, option=value, option=value, ...)
```

- The first positional argument is always the **parent**.
- All other arguments are keyword options. Order does not matter.
- Common options that work across most widgets: `width`, `height`, `padding`, `takefocus`, `state`, `cursor`, `style`.

Configure later:

```python
label.config(text="Updated")      # change an option
label["text"] = "Updated"          # equivalent, terser
label.cget("text")                 # read an option
```

## 2.7 Widget Lifecycle

```python
b = ttk.Button(root, text="Hi")
b.pack()
# ... later ...
b.destroy()        # widget is gone; references become stale
```

- **Creation** allocates a Tk widget object in C.
- **Geometry management** (`pack`/`grid`/`place`) makes it visible and positioned.
- **`.destroy()`** releases the underlying C object and all its children. Python references to it become unusable.

## 2.8 What's Next

Read `03_layout_managers.md` to learn how to put these widgets where you want them.
