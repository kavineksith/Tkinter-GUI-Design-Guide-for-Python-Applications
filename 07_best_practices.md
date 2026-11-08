# 7. Best Practices

A checklist of small rules that, applied consistently, take tkinter code from "works" to "professional".

## 7.1 Project Hygiene

- **One class per file.** If a file grows past ~400 lines, split it.
- **Use a package layout** (`myapp/__init__.py`, `myapp/views/`, `myapp/models/`) for anything more than a single screen.
- **`main.py` should be short.** Build the root window, instantiate the app, start the loop. Done.
- **No `import *`.** Always `import tkinter as tk` and `from tkinter import ttk`.
- **Don't `import *` from tkinter.messagebox** etc. — those names clash (`filedialog.filedialog`).
- **Type-hint public methods.** Private helpers may skip them.

## 7.2 Widget Construction

- **Prefer `ttk` over classic `tk`** for everything except `Menu`, `Canvas`, `Text`, `BitmapImage`, `PhotoImage`.
- **Pass `textvariable=`** for any entry whose value you'll need to read in a callback.
- **Give widgets meaningful names** when debugging — `widget.configure(name=...)` isn't always honored, but **storing them as named attributes** is: `self.email_entry = ttk.Entry(...)` not just `ttk.Entry(...)`.
- **Hold a reference to every `PhotoImage`**. Otherwise the GC collects them and your buttons / labels go blank.

```python
self.icon = tk.PhotoImage(file="save.png")     # held by self — survives
btn = ttk.Button(self, image=self.icon)
```

- **Don't reuse one PhotoImage across many `Button`s that may need to differ** — create per-button instances if you'll swap icons.

## 7.3 Layout

- **Pick one manager per parent.** Never mix `pack` and `grid` in the same container.
- **Use `Frame`s to compose regions.** Top-level `pack`, region-internal `grid`.
- **Configure `columnconfigure` / `rowconfigure` for resize behavior** — explicit beats implicit.
- **Use `padding=` on `ttk.Frame`** rather than per-widget `padx`/`pady` whenever you want uniform internal spacing.
- **Test resize aggressively** — drag the window edge around during development.

## 7.4 Styling

- **Use `clam` theme** for cross-platform consistency.
- **Define a single `PALETTE` dict** in one module, import everywhere.
- **Use named ttk styles** (`Accent.TButton`, `Danger.TButton`) — don't inline colors in widgets.
- **Set fonts globally** with `tkfont.nametofont("TkDefaultFont").configure(...)`.
- **Don't remove keyboard focus visuals.** Disabled users depend on them.

## 7.5 Event Handling

- **Prefer `command=` over `bind("<Button-1>", ...)`** for buttons — `command` also fires on keyboard activation (Space / Enter).
- **Prefer virtual events** (`<<ComboboxSelected>>`) over raw `"<Button-1>"` for ttk widgets.
- **Use `bind_all` only for true global shortcuts** (Ctrl+S, F1, etc.). Local bindings are safer.
- **Bind modifiers in a consistent order**: `Control-Shift-Key`, not `Shift-Control-Key`.
- **For repeated work, use `root.after(ms, fn)`** — never `time.sleep()` in a callback.

## 7.6 Long-Running Work

- **Never block `mainloop`.** A blocking call freezes the entire UI.
- **Run slow work in a worker thread** and marshal results back with `root.after(0, callback, result)`.
- **Show a progress indicator** for anything > 250 ms.
- **Disable the action button** during the operation, so users can't trigger it twice.
- **Use `queue.Queue`** to pass data from worker thread to GUI thread — it's thread-safe; tkinter widgets are not.

See `examples/16_multithreading.py`.

## 7.7 Error Handling

- **Wrap top-level callbacks in a try/except** that logs and shows a dialog. Otherwise the traceback goes to stderr and the user sees nothing.

```python
def safe_command(self):
    try:
        self.do_the_thing()
    except Exception as e:
        logger.exception("Action failed")
        messagebox.showerror("Error", f"Action failed:\n{e}")
```

- **Validate input on the way in**, not just on submit. Use `validatecommand=` on `Entry` for live validation.
- **Show validation errors inline** next to the field, not just in a popup.
- **Distinguish recoverable errors** (user typo) from fatal errors (corrupt config file) and handle each appropriately.

## 7.8 Persistence & Configuration

- **Persist user settings** in a known location: `appdirs.user_config_dir("MyApp")` (or `pathlib.Path.home() / ".myapp"`) — never in the install directory.
- **Use JSON, TOML, or INI**, not bespoke binary formats.
- **Save on exit, restore on startup.** Don't force users to reposition windows every launch.
- **Save window geometry** with `root.geometry()` → restore with `root.geometry("WxH+X+Y")`.
- **Save the last-used directory** for file dialogs so the next dialog opens in the same place.

See `examples/19_settings_config.py`.

## 7.9 Accessibility

- **Always set keyboard focus** to a sensible widget on startup (e.g., the first input field).
- **Provide mnemonics for menus**: `file_menu.add_command(label="Open...", underline=0, accelerator="Ctrl+O")`.
- **Use a meaningful label/`text=`** — screen readers read it.
- **Don't rely on color alone** to convey state — pair it with an icon or text.
- **Respect the system font scaling**: use `TkDefaultFont`, not hardcoded sizes.

## 7.10 Internationalization (i18n)

If your app might ship in multiple languages:

- **Use `_()` for every user-visible string** and a translation backend like `gettext`:
  ```python
  from gettext import gettext as _
  ttk.Button(parent, text=_("Save"))
  ```
- **Don't concatenate translated fragments** — use format strings: `_("Saved {n} items").format(n=count)`.
- **Test with long German strings** — they often break tight layouts.

## 7.11 Testing

- **Unit-test the model.** The model has no tkinter, so it's just Python.
- **For controllers**, mock the view and assert on the calls made to it.
- **For GUI tests**, use a headless approach: don't call `mainloop()`. Construct the app, set variables programmatically, fire commands, assert on resulting state.
- **Avoid screenshot-diff tests** — too brittle across platforms.

## 7.12 Packaging

- **Use `PyInstaller`** to ship a single `.exe` / `.app` / ELF binary:
  ```bash
  pyinstaller --onefile --windowed main.py
  ```
- **Bundle assets** (icons, default config) with `--add-data`.
- **Set the application icon** with `--icon=app.ico` (Windows), `--icon=app.icns` (macOS).
- **Test the packaged binary on a clean machine** — PyInstaller occasionally misses a hidden import.

## 7.13 Performance

- **Don't construct thousands of widgets.** A `Treeview` with 100k items is fine; 100k `ttk.Label`s are not.
- **Use `Treeview` or `Canvas`** for large lists, not `Frame` + `Label` rows.
- **Avoid `time.sleep`** and any blocking I/O on the GUI thread.
- **Throttle expensive redraws** — coalesce multiple updates with `after_idle`.
- **Profile** with `cProfile` if a UI feels slow; tkinter itself is rarely the bottleneck.

## 7.14 Code Quality

- **Run `ruff check`** or `flake8` on your code.
- **Format with `black`** — consistent style across the project.
- **Lint tkinter-specific issues** manually: e.g., "did you forget to call `.pack()`?"
- **Write docstrings** for every class and every public method.

## 7.15 What's Next

Read `08_advanced_topics.md` for the patterns you need when ordinary `pack` / `grid` no longer suffice.
