# Widget Reference

A quick-reference table for every tkinter/ttk widget, with the most
commonly used options, the value type, and how to read/write it.

## Conventions

- **Read** = how to get the current value.
- **Write** = how to set the current value.
- Options marked `(ttk)` only apply to ttk widgets. Options marked `(tk)` only apply to classic widgets. Unmarked apply to both.

---

## Containers

### `Frame` / `ttk.Frame`

A bare container.

| Option | Type | Notes |
|---|---|---|
| `padding` | int or (l, t, r, b) | Internal padding around children. |
| `relief` | str | (tk only) Border style: `flat`, `raised`, `sunken`, `groove`, `ridge`. |
| `borderwidth` | int | (tk only) Border width in pixels. |
| `width`, `height` | int | In pixels; ignored if `pack_propagate(False)` is unset. |
| `background` | str | (tk only) Color. ttk uses `style.configure("TFrame", background=...)`. |

Methods: `pack_propagate(False)`, `grid_propagate(False)`, `columnconfigure`, `rowconfigure`.

### `LabelFrame` / `ttk.LabelFrame`

A `Frame` with a visible border and title.

| Option | Type | Notes |
|---|---|---|
| `text` | str | The title. |
| `labelwidget` | Widget | Use a custom widget (e.g., a Checkbutton) as the label instead of `text=`. |
| `padding` | int or tuple | Internal padding. (ttk) |
| `labelanchor` | str | Position: `nw`, `n`, `ne`, `en`, `e`, `es`, `se`, `s`, `sw`, `ws`, `w`, `wn`. Default `nw`. (ttk) |

### `Notebook` (ttk only)

Tabbed container.

| Method | Purpose |
|---|---|
| `.add(child, text="...", **opts)` | Add a tab. |
| `.select(tab_id)` | Activate a tab. |
| `.forget(tab_id)` | Remove a tab. |
| `.tab(tab_id, option=value)` | Get/set tab options. |
| `.tabs()` | Return list of all tab ids. |
| `.index(tab_id)` | Return integer index of a tab. |
| `.index("end")` | Return count of tabs. |

Virtual event: `<<NotebookTabChanged>>`.

### `PanedWindow` / `ttk.PanedWindow`

A draggable splitter.

| Option | Type | Notes |
|---|---|---|
| `orient` | str | `"horizontal"` or `"vertical"`. |
| `sashwidth` | int | Width of the drag handle. (tk) |

Methods: `.add(child, weight=N)`, `.sashpos(index, newpos=None)`.

---

## Inputs

### `Entry` / `ttk.Entry`

Single-line text input.

| Operation | Code |
|---|---|
| Read | `entry.get()` |
| Set | `entry.delete(0, "end"); entry.insert(0, "value")` |
| With variable | `var = tk.StringVar(); ttk.Entry(parent, textvariable=var)`; then `var.get()` / `var.set(...)` |
| Selection | `entry.select_from(0); entry.select_to("end")` |
| Cursor | `entry.icursor("end")` |
| Validate | `entry.config(validate="key", validatecommand=(registered, "%P"))` |

Common options: `width`, `show` (mask char), `state` (`normal`, `readonly`, `disabled`), `validate`, `validatecommand`, `invalidcommand`.

### `Spinbox` / `ttk.Spinbox`

Numeric entry with up/down buttons.

| Operation | Code |
|---|---|
| Read | `spinbox.get()` (returns string) |
| Set | `spinbox.set("5")` |

Options: `from_`, `to`, `increment`, `values` (list — overrides from_/to), `wrap`, `format` (printf-style).

### `Combobox` (ttk only)

Drop-down with optional editing.

| Operation | Code |
|---|---|
| Read | `cb.get()` |
| Set | `cb.set("value")` |
| List | `cb["values"] = ["a", "b", "c"]` |
| Selection event | `cb.bind("<<ComboboxSelected>>", ...)` |

Options: `values`, `state` (`normal` = editable, `readonly` = pick only, `disabled`), `width`.

### `Checkbutton` / `ttk.Checkbutton`

On/off toggle.

| Operation | Code |
|---|---|
| Read | `var.get()` where `var` is the attached `BooleanVar` / `IntVar` |
| Set | `var.set(True)` |

Options: `variable`, `text`, `command`, `onvalue`, `offvalue` (use 1/0 by default; can be set to any value), `state`.

### `Radiobutton` / `ttk.Radiobutton`

Select one from a group; all members share a `variable`.

```python
var = tk.StringVar(value="b")
ttk.Radiobutton(parent, text="A", value="a", variable=var)
ttk.Radiobutton(parent, text="B", value="b", variable=var)
```

Options: `variable`, `value`, `text`, `command`, `state`.

### `Scale` / `ttk.Scale`

Slider.

| Operation | Code |
|---|---|
| Read | `scale.get()` (float) |
| Set | `scale.set(0.5)` |

Options: `from_`, `to`, `orient`, `variable`, `command`, `length`, `tickinterval` (tk only).

### `Text` (tk only — no ttk equivalent)

Multi-line rich text.

| Operation | Code |
|---|---|
| Read all | `text.get("1.0", "end-1c")` (drop trailing newline) |
| Read selection | `text.get("sel.first", "sel.last")` |
| Insert | `text.insert("1.0", "...")` |
| Delete all | `text.delete("1.0", "end")` |
| Cursor | `text.index("insert")` |
| See end | `text.see("end")` |
| Tags | `text.tag_add("bold", "1.0", "1.5"); text.tag_config("bold", font=("TkDefaultFont", 10, "bold"))` |
| Embedded widget | `text.window_create("end", window=ttk.Button(text))` |
| Embedded image | `text.image_create("end", image=img)` |

Index format: `"line.col"` (1-indexed line, 0-indexed column). Special indices: `"1.0"`, `"end"`, `"insert"`, `"current"`, `"sel.first"`, `"sel.last"`.

### `Canvas` (tk only)

2D vector surface.

| Operation | Code |
|---|---|
| Rectangle | `id = canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="black")` |
| Oval / Circle | `canvas.create_oval(x1, y1, x2, y2, fill="blue")` |
| Line | `canvas.create_line(x1, y1, x2, y2, fill="black", width=2)` |
| Polygon | `canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill="green")` |
| Arc | `canvas.create_arc(x1, y1, x2, y2, start=0, extent=180, style="pieslice")` |
| Text | `canvas.create_text(x, y, text="Hi", fill="black")` |
| Image | `canvas.create_image(x, y, image=img, anchor="center")` |
| Embedded widget | `canvas.create_window(x, y, window=btn, anchor="center")` |
| Move | `canvas.move(id, dx, dy)` |
| Delete | `canvas.delete(id)` or `canvas.delete("all")` |
| Get coords | `canvas.coords(id)` |
| Tag bind | `canvas.tag_bind(id, "<Button-1>", handler)` |
| Export PS | `canvas.postscript(colormode="color")` |

---

## Display

### `Label` / `ttk.Label`

Static text or image.

| Option | Type | Notes |
|---|---|---|
| `text` | str | The text to display. |
| `textvariable` | Variable | When set, label auto-updates. |
| `image` | PhotoImage | Image; takes precedence over text unless `compound=` is set. |
| `compound` | str | `none` (default, image only), `text` (text only), `top`/`bottom`/`left`/`right`/`center`. |
| `font` | tuple or Font | `("family", size, "bold italic")`. |
| `foreground`, `fg` | str | Text color. (ttk: configure via style.) |
| `background`, `bg` | str | Background. (ttk: configure via style.) |
| `justify` | str | Multi-line: `left`, `center`, `right`. |
| `wraplength` | int | Pixel width to wrap at. |
| `anchor` | str | Position within the label box: `w`, `e`, `center`, `n`, `s`, etc. |
| `width` | int | In characters (text) or pixels (image). |

### `Treeview` (ttk only)

Tabular list or tree.

| Operation | Code |
|---|---|
| Define columns | `tree = ttk.Treeview(parent, columns=("a", "b"), show="headings")` |
| Heading | `tree.heading("a", text="A", command=lambda: sort_by("a"))` |
| Column width | `tree.column("a", width=120, anchor="w")` |
| Insert row | `tree.insert("", "end", values=("x", "y"))` |
| Insert with id | `tree.insert("", "end", iid="42", values=("x", "y"))` |
| Get values | `tree.item(item_id, "values")` |
| Set cell | `tree.set(item_id, "a", "new")` |
| Selection | `tree.selection()` returns tuple of ids |
| Select | `tree.selection_set(item_id)` |
| Delete | `tree.delete(item_id)` |
| All items | `tree.get_children("")` |

Virtual events: `<<TreeviewSelect>>`, `<<TreeviewOpen>>`, `<<TreeviewClose>>`.

### `Progressbar` (ttk only)

| Option | Type | Notes |
|---|---|---|
| `mode` | str | `"determinate"` (0..maximum) or `"indeterminate"` (bouncing). |
| `maximum` | float | Upper bound. |
| `value` | float | Current value (determinate mode). |
| `orient` | str | `"horizontal"` or `"vertical"`. |
| `variable` | DoubleVar | Two-way binding. |

Methods: `.step(amount)`, `.start(interval_ms)`, `.stop()`.

### `Separator` (ttk only)

Horizontal or vertical divider line.

| Option | Type | Notes |
|---|---|---|
| `orient` | str | `"horizontal"` or `"vertical"`. |

### `Sizegrip` (ttk only)

A draggable corner handle for resizing the window. Just `ttk.Sizegrip(parent).pack(side="right")`.

---

## Top-level & Dialogs

### `Toplevel`

A second top-level window.

| Option / Method | Purpose |
|---|---|
| `transient(parent)` | Mark as helper window — usually no taskbar entry. |
| `grab_set()` | Make this window modal — block input to other windows. |
| `grab_release()` | Release the modal grab. |
| `wait_window()` | Block until the window is destroyed. |
| `overrideredirect(True)` | Remove window border (for splash screens, custom title bars). |
| `attributes("-topmost", True)` | Keep above other windows. |
| `geometry("WxH+X+Y")` | Set size and position. |
| `minsize(w, h)` | Minimum size. |
| `maxsize(w, h)` | Maximum size. |
| `resizable(width, height)` | Whether the user can resize. |

### `messagebox`

| Function | Returns |
|---|---|
| `showinfo(title, message)` | `"ok"` |
| `showwarning(title, message)` | `"ok"` |
| `showerror(title, message)` | `"ok"` |
| `askquestion(title, message)` | `"yes"` or `"no"` |
| `askokcancel(title, message)` | `True` / `False` |
| `askyesno(title, message)` | `True` / `False` |
| `askyesnocancel(title, message)` | `True` / `False` / `None` |
| `askretrycancel(title, message)` | `True` / `False` |

Always pass `parent=` so the dialog appears over your window.

### `filedialog`

| Function | Returns |
|---|---|
| `askopenfilename(**opts)` | Path string, or `""` if cancelled. |
| `askopenfilenames(**opts)` | Tuple of path strings. |
| `asksaveasfilename(**opts)` | Path string, or `""` if cancelled. |
| `askdirectory(**opts)` | Path string, or `""` if cancelled. |

Common options: `title`, `initialdir`, `filetypes=[("Label", "*.ext"), ("All", "*.*")]`, `defaultextension`.

### `colorchooser`

| Function | Returns |
|---|---|
| `askcolor(color=None, **opts)` | Tuple `(rgb_tuple, hex_string)` or `(None, None)`. |

### `simpledialog`

| Function | Returns |
|---|---|
| `askstring(title, prompt, **opts)` | String or `None`. |
| `askinteger(title, prompt, **opts)` | Integer or `None`. |
| `askfloat(title, prompt, **opts)` | Float or `None`. |

Options: `initialvalue`, `minvalue`, `maxvalue`, `parent`.

---

## Menu (tk only — no ttk equivalent)

### `Menu`

A menu bar or a popup menu.

| Method | Purpose |
|---|---|
| `parent.config(menu=menubar)` | Install as the window's menu bar. |
| `menubar.add_cascade(label="File", menu=submenu)` | Add a top-level entry that opens a submenu. |
| `submenu.add_command(label="Open", command=fn, accelerator="Ctrl+O", underline=0)` | Add a command. |
| `submenu.add_separator()` | Add a visual divider. |
| `submenu.add_checkbutton(label="...", variable=var)` | Add a checkable item. |
| `submenu.add_radiobutton(label="...", variable=var, value="x")` | Add a radio item. |
| `submenu.add_cascade(label="Sub", menu=sub_submenu)` | Nested submenu. |
| `menu.tk_popup(x_root, y_root)` | Show as a popup menu (context menu). |
| `menu.delete(0, "end")` | Clear all items. |

Options per item: `label`, `command`, `accelerator` (visual hint only), `underline` (int — index of character to underline), `state`, `image`, `compound`.

Disable the old tear-off feature once: `root.option_add("*tearOff", False)`.

---

## Variables (`tk.Variable` family)

| Class | Stores | Use with |
|---|---|---|
| `tk.StringVar` | str | `Entry`, `Label`, `Combobox`, `Radiobutton`, `Checkbutton` |
| `tk.IntVar` | int | `Checkbutton`, `Radiobutton`, `Scale` |
| `tk.DoubleVar` | float | `Scale`, `Progressbar` |
| `tk.BooleanVar` | bool | `Checkbutton` |

Methods: `.get()`, `.set(value)`, `.trace_add("write", callback)`, `.trace_remove(mode, cbname)`.

---

## Fonts (`tkinter.font`)

| Function | Purpose |
|---|---|
| `font.Font(family="Segoe UI", size=10, weight="bold", slant="italic", underline=True, overstrike=True)` | Define a named font. |
| `font.nametofont("TkDefaultFont")` | Get the system default font. Configure it to globally re-theme. |
| `font.families()` | List all installed font families. |
| `font.actual(font)` | Get the actual resolved properties as a dict. |
| `myfont.actual("family")` | Get one resolved property. |
| `myfont.metrics()` | Font metrics (ascent, descent, linespace, fixed). |
| `myfont.measure("text")` | Pixel width of `text` in this font. |
