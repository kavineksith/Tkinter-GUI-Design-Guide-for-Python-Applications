# 4. Styling & Theming

A well-styled tkinter app looks native on Windows, macOS, and Linux. A poorly-styled one looks like a 1995 Windows control panel. The difference comes down to three things: using **ttk**, picking the right **theme**, and applying **fonts and padding** consistently.

## 4.1 The ttk Style System

Classic widgets (`tk.Button`) take styling options directly (`bg`, `fg`, `font`). ttk widgets do not — they take a **`style=` name**, and that style is configured centrally via `ttk.Style`.

```python
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
style = ttk.Style(root)

# Define a custom style called "Accent.TButton" derived from "TButton".
style.configure("Accent.TButton",
                font=("Segoe UI", 11, "bold"),
                padding=(12, 8))
style.map("Accent.TButton",
          background=[("active", "#0a6cf1"), ("!disabled", "#1565d8")],
          foreground=[("!disabled", "white")])

btn = ttk.Button(root, text="Save", style="Accent.TButton")
btn.pack(padx=20, pady=20)
```

### The style name convention

`<CustomName>.<WidgetClass>` — e.g., `Accent.TButton`, `Danger.TButton`, `Heading.TLabel`.

- `<WidgetClass>` (`TButton`, `TLabel`, `TEntry`, …) tells ttk which widget type the style applies to.
- The prefix is your own name. It lets you have several variations of the same widget.

### `configure` vs `map`

| Method | Purpose |
|---|---|
| `style.configure(name, option=value, ...)` | Sets the **static** appearance (font, padding, border, background). |
| `style.map(name, option=[(state, value), ...])` | Sets appearance **per state**. States include `active`, `pressed`, `disabled`, `selected`, `focus`, `readonly`, `hover`. |

## 4.2 Built-in Themes

Each platform ships its own ttk themes. List available themes:

```python
print(style.theme_names())
# Windows 11: ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
# macOS:      ('aqua', 'clam', 'alt', 'default', 'classic')
# Linux:      ('clam', 'alt', 'default', 'classic')
```

Pick one:

```python
style.theme_use("clam")      # cross-platform, looks consistent everywhere
```

| Theme | Where it's good | Notes |
|---|---|---|
| `clam` | Everywhere — the safe default | Looks identical on all OSes; recommended for cross-platform apps. |
| `vista` (Windows) | Windows-only apps | Native Windows look. |
| `aqua` (macOS) | macOS-only apps | Native macOS look. |
| `winnative` / `xpnative` | Legacy Windows | Pre-Vista look. |
| `default`, `alt`, `classic` | Nowhere modern | Available for fallback only. |

> **Recommendation:** use `clam` for cross-platform consistency. Then customize it. This is the only way to ship a UI that looks the same on every OS without rewriting styling for each one.

## 4.3 Customizing Fonts

```python
default_font = ("Segoe UI", 10)             # Windows
default_font = ("Helvetica Neue", 13)        # macOS
default_font = ("DejaVu Sans", 10)          # Linux
default_font = ("TkDefaultFont",)           # let the OS decide — recommended
```

Apply globally with `tkinter.font`:

```python
from tkinter import font as tkfont
tkfont.nametofont("TkDefaultFont").configure(family="Segoe UI", size=10)
tkfont.nametofont("TkTextFont").configure(family="Segoe UI", size=10)
tkfont.nametofont("TkHeadingFont").configure(family="Segoe UI", size=11, weight="bold")
tkfont.nametofont("TkMenuFont").configure(family="Segoe UI", size=10)
```

> Calling `nametofont("TkDefaultFont").configure(...)` updates **every widget** that uses the default font, retroactively. This is the easiest way to globally change the app's typography.

## 4.4 Color Palette

Define your palette once, reuse everywhere:

```python
PALETTE = {
    "bg":           "#FFFFFF",
    "surface":      "#F4F4F5",
    "primary":      "#1565D8",
    "primary_hover":"#0F4C9E",
    "accent":       "#10B981",
    "danger":       "#DC2626",
    "warning":      "#F59E0B",
    "text":         "#1F2937",
    "muted":        "#6B7280",
    "border":       "#D1D5DB",
}
```

Use named ttk styles tied to these colors:

```python
style.configure("Card.TFrame", background=PALETTE["surface"], relief="solid", borderwidth=1)
style.configure("Title.TLabel", font=("TkDefaultFont", 16, "bold"),
                foreground=PALETTE["text"], background=PALETTE["surface"])
style.configure("Danger.TButton", font=("TkDefaultFont", 10, "bold"),
                foreground="white", background=PALETTE["danger"])
style.map("Danger.TButton",
          background=[("active", "#B91C1C")])
```

## 4.5 Spacing & Visual Hierarchy

Three rules that make 90% of UIs look good:

1. **Padding around everything.** Use 8–16 px between elements. Never butt widgets against each other or against the window edge.
2. **One primary action per screen.** Style it with `Accent.TButton`; style everything else with the default `TButton` (lower visual weight).
3. **Group with `LabelFrame` or `Frame` backgrounds.** Don't rely on whitespace alone — visible grouping helps users scan.

A reference spacing scale:

| Use case | Padding |
|---|---|
| Window margin (frame edge to first widget) | 12 px |
| Gap between two adjacent fields in a form | 8 px |
| Gap between two distinct groups | 16 px |
| Button internal padding (height) | 6–8 px |
| Button internal padding (width) | 12–16 px |

## 4.6 The `clam` Theme — Recommended Starting Point

```python
style = ttk.Style(root)
style.theme_use("clam")

# Re-skin clam from a neutral palette
style.configure(".", background=PALETTE["bg"], foreground=PALETTE["text"],
                bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                darkcolor=PALETTE["border"], troughcolor=PALETTE["surface"],
                focuscolor=PALETTE["primary"])
```

The `"."` style is the **root style** — every widget inherits from it. This is the cleanest way to globally re-theme ttk.

## 4.7 State, Focus, and Disabled Widgets

Test all four states for every interactive widget:

1. **Normal** — what most apps look like in screenshots.
2. **Hover / Active** — `style.map("…", background=[("active", …)])`
3. **Focus** — keyboard focus ring. Don't remove it — keyboard users depend on it.
4. **Disabled** — `state=["disabled"]`. Should look clearly less prominent than enabled widgets.

```python
style.map("Accent.TButton",
          background=[("active", "#0F4C9E"),
                      ("disabled", "#9CA3AF")],
          foreground=[("disabled", "#F3F4F6")])
```

## 4.8 High-DPI Support

Tkinter does not auto-scale on high-DPI displays on Linux. On Windows and macOS, it usually does, but check.

```python
try:
    # Tk 8.6 / Python 3.8+ on Windows
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass  # not on Windows, or Tk already aware
```

Combine this with `root.tk.call('tk', 'scaling', factor)` only if you really need to override the OS scaling factor — usually you don't.

## 4.9 Icons

`ttk.Button` accepts an `image=` option (a `tk.PhotoImage` or `tk.BitmapImage`). Use PNG (`PhotoImage(file="icon.png")`) for icons. Always hold a reference to the image object or it gets garbage-collected and the button goes blank:

```python
self.save_icon = tk.PhotoImage(file="assets/save.png")
btn = ttk.Button(self, text="Save", image=self.save_icon, compound="left")
```

For SVG icons, install `Pillow` and load via `PIL.Image` + `ImageTk.PhotoImage`, or use a `.png`/`.gif`.

## 4.10 What's Next

Read `05_event_handling.md` to make these styled widgets actually do something.
