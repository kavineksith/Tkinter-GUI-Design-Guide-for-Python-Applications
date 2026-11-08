# 3. Layout Managers

A layout manager ("geometry manager") decides **where** a widget appears inside its parent. Tkinter gives you three:

| Manager | Mental Model | Best For |
|---|---|---|
| **`pack`** | Stack from one edge — like a vertical or horizontal flow. | Simple top/bottom/left/right stacks, status bars, sidebars. |
| **`grid`** | Spread widgets onto a 2-D table of rows × columns. | Forms, dialogs, anything with alignment. |
| **`place`** | Absolute pixel coordinates or relative fractions. | Drag-and-drop regions, overlays, custom floating UI. |

> **Golden rule:** Never mix managers inside the same parent. Pick one and stick with it. Mixing will cause silent, baffling bugs.

## 3.1 `pack` — Stacking

`pack` arranges widgets in the order you call it, each pushed against one side of the remaining space.

```python
ttk.Button(root, text="Top").pack(side="top", fill="x")
ttk.Button(root, text="Bottom").pack(side="bottom", fill="x")
ttk.Button(root, text="Left").pack(side="left", fill="y")
ttk.Button(root, text="Right").pack(side="right", fill="y")
ttk.Button(root, text="Center").pack(side="top", expand=True, fill="both")
```

### Options

| Option | Values | Effect |
|---|---|---|
| `side` | `top` (default), `bottom`, `left`, `right` | Which edge to glue to. |
| `fill` | `none`, `x`, `y`, `both` | Stretch in this direction. |
| `expand` | `True` / `False` | Take any leftover space (grow). |
| `padx`, `pady` | int or (left, right) | External padding in pixels. |
| `ipadx`, `ipady` | int | Internal padding (grows widget). |
| `anchor` | `n`, `s`, `e`, `w`, `center`, `ne`, `nw`, `se`, `sw` | Where in its slot to anchor. |
| `before`, `after` | another widget | Reorder relative to a sibling. |

### When to use `pack`
- You have a simple top-menu / main / status-bar layout.
- You have a vertical or horizontal strip of equal widgets.

### When NOT to use `pack`
- Anything with multiple columns aligned on labels.
- Anything where you would be squinting and adding extra `Frame`s just to align fields. Use `grid` instead.

## 3.2 `grid` — The Workhorse for Forms

`grid` puts each widget into a row/column cell of an invisible table inside its parent. This is the **most-used manager for real forms**.

```python
fields = [
    ("Name:",    ttk.Entry(form)),
    ("Email:",   ttk.Entry(form)),
    ("Phone:",   ttk.Entry(form)),
]
for row, (label_text, widget) in enumerate(fields):
    ttk.Label(form, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=3)
    widget.grid(row=row, column=1, sticky="ew",  padx=5, pady=3)

form.columnconfigure(1, weight=1)   # let the entries stretch horizontally
```

### Options

| Option | Values | Effect |
|---|---|---|
| `row`, `column` | int | Cell coordinates (0-indexed). |
| `rowspan`, `columnspan` | int | Span multiple rows/columns. |
| `sticky` | combination of `n`, `s`, `e`, `w` | Glue to one or more sides of the cell when the cell is bigger than the widget. |
| `padx`, `pady` | int or (left, right) | External padding. |
| `ipadx`, `ipady` | int | Internal padding. |

### `columnconfigure` and `rowconfigure`

These configure the **columns and rows**, not the widgets. The crucial option is `weight`:

```python
form.columnconfigure(1, weight=1)   # column 1 grows when the window resizes
form.rowconfigure(0, weight=1)      # row 0 grows
```

- `weight=0` (default): column stays at its natural width.
- `weight=1`: column shares leftover space with other weighted columns.
- `weight=2`: column takes twice as much leftover space as a `weight=1` column.

### `sticky` semantics

| `sticky` value | Result |
|---|---|
| (none) | Centered in cell. |
| `"w"` | Left-aligned. |
| `"e"` | Right-aligned. |
| `"ew"` | Stretched horizontally. |
| `"nsew"` | Stretched to fill the entire cell. |
| `"n"` | Top-aligned. |
| `"s"` | Bottom-aligned. |

### When to use `grid`
- Any form with labeled fields.
- Dialogs with multiple inputs.
- Anything that needs alignment across rows or columns.

## 3.3 `place` — Absolute & Relative

`place` lets you position a widget at exact coordinates or relative fractions. Powerful but rigid.

```python
# Absolute: top-left at (50, 30), 120×40 px
btn.place(x=50, y=30, width=120, height=40)

# Relative: centered horizontally, near the top
btn.place(relx=0.5, rely=0.1, anchor="n")

# Relative size: fill 80% of width, 20% of height
banner.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.2)
```

### Options

| Option | Effect |
|---|---|
| `x`, `y` | Absolute position in pixels (top-left corner by default). |
| `relx`, `rely` | Position as a fraction (0.0–1.0) of the parent. |
| `width`, `height` | Absolute size in pixels. |
| `relwidth`, `relheight` | Size as a fraction of the parent. |
| `anchor` | Which point of the widget the (x,y) refers to: `nw` (default), `n`, `ne`, `w`, `center`, `e`, `sw`, `s`, `se`. |

### When to use `place`
- Custom floating or draggable widgets.
- Overlays (badges, tooltips).
- Hard-coded layouts that must not resize.

### When NOT to use `place`
- Any UI that might be displayed at different sizes.
- Anything where the user might change the system font size or DPI scaling — your fixed pixel offsets will break.

## 3.4 The `Frame` Composition Trick

Most real UIs combine `pack` (for top-level regions) and `grid` (inside each region). The trick: use `Frame`s to create regions, each with its own consistent manager.

```python
# Window split into: menu bar (top), main area (center), status bar (bottom).
main_area  = ttk.Frame(root); main_area.pack(side="top", fill="both", expand=True)
status_bar = ttk.Frame(root); status_bar.pack(side="bottom", fill="x")

# Inside main_area, use grid:
ttk.Label(main_area, text="Field:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
ttk.Entry(main_area).grid(row=0, column=1, sticky="ew", padx=4, pady=2)
main_area.columnconfigure(1, weight=1)

# Status bar can use pack:
ttk.Label(status_bar, text="Ready.").pack(side="left", padx=8, pady=3)
ttk.Sizegrip(status_bar).pack(side="right")
```

Each `Frame` is its own coordinate system. Mixing managers across different frames is fine — only mixing them inside the *same* parent is forbidden.

## 3.5 Padding and Spacing Conventions

- Use `padx`/`pady` (external padding) for spacing between widgets.
- Use `ipadx`/`ipady` (internal padding) to make a widget itself larger (e.g., bigger buttons).
- A `ttk.Frame(padding=10)` adds internal padding around all its children uniformly — usually cleaner than per-widget `padx`/`pady`.
- Standard spacing: 8 px between related items, 16 px between groups, 12 px between the window edge and content.

## 3.6 Resize Behavior Checklist

When the window grows, what should grow?

1. The main content area → `expand=True, fill="both"` (pack) or `weight=1` (grid column/row).
2. Inputs that should stretch (text fields, text areas) → `sticky="ew"` or `sticky="nsew"`.
3. Buttons → usually fixed; do NOT let them stretch horizontally.
4. Status bar → fill horizontally, fixed height.

Test your layout by **resizing the window aggressively** during development. Anything that breaks, you find now — not in front of a user.

## 3.7 What's Next

Read `04_styling_and_theming.md` to learn how to make these widgets look good.
