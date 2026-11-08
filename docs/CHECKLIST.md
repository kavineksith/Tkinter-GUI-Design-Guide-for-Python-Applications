# Tkinter Development Checklist

Use this as a final review before declaring a feature done, or before shipping.

## Project Setup

- [ ] `tkinter` import works on the target platforms (Windows/macOS/Linux).
- [ ] On Linux, the `python3-tk` package is documented in the README.
- [ ] Python version requirement is declared (`python_requires=">=3.8"` in `pyproject.toml`).
- [ ] All third-party dependencies are listed in `pyproject.toml` or `requirements.txt`.
- [ ] Entry point is a short `main.py` that builds the root window and starts the loop.
- [ ] No `from tkinter import *` anywhere.
- [ ] Code is formatted with `black` and linted with `ruff`.

## Architecture

- [ ] The app is wrapped in a class (or set of classes), not a flat script.
- [ ] Business logic is separated from tkinter (no `import tkinter` in `models/`).
- [ ] Controllers/views/models live in their own subpackages.
- [ ] The model is unit-testable without instantiating any tkinter widget.
- [ ] Settings are loaded once at startup, passed in via dependency injection.
- [ ] No globals except module-level constants.

## Construction

- [ ] Exactly one `tk.Tk()` instance is created.
- [ ] `mainloop()` is called exactly once, at the end of `main()`.
- [ ] Every widget has a parent argument (no implicit root).
- [ ] Every widget that will be referenced later is stored on `self`.
- [ ] Every `PhotoImage` is held by a long-lived attribute.

## Layout

- [ ] Each parent uses exactly one geometry manager (no `pack` + `grid` mix).
- [ ] `Frame`s are used to combine managers across regions.
- [ ] `columnconfigure` / `rowconfigure` are set for resizeable columns/rows.
- [ ] `pack(fill="both", expand=True)` on the main content area.
- [ ] Standard spacing (8 px field gap, 16 px group gap, 12 px margin).
- [ ] Window has a sensible default size via `root.geometry()`.
- [ ] Window has a sensible minimum size via `root.minsize()`.

## Styling

- [ ] `clam` theme is selected for cross-platform consistency.
- [ ] A single `PALETTE` dict defines all colors.
- [ ] Fonts are set globally via `nametofont("TkDefaultFont").configure(...)`.
- [ ] Named styles (`Accent.TButton`, etc.) instead of inline colors.
- [ ] State-dependent styles use `style.map()` (`active`, `disabled`, `pressed`).
- [ ] Keyboard focus visuals are not removed.

## Events

- [ ] `command=` is used for primary widget actions.
- [ ] `bind()` is used only when no `command` equivalent exists.
- [ ] Virtual events (`<<ComboboxSelected>>`, etc.) are preferred over raw `<Button-1>`.
- [ ] Global shortcuts use `bind_all()`.
- [ ] No bare `bind("<Key>", ...)` that returns `None` to suppress defaults — return `"break"` explicitly.
- [ ] Lambda callbacks use the `n=name` default-binding trick to avoid late-binding bugs.

## Long-Running Work

- [ ] No blocking calls on the GUI thread (no `time.sleep`, no `requests.get` without timeout, no long loops).
- [ ] Worker threads are marked `daemon=True`.
- [ ] Worker threads never touch widgets — they push results via `queue.Queue` or `root.after(0, ...)`.
- [ ] A progress indicator is shown for any task > 250 ms.
- [ ] The action button is disabled during the operation.

## Error Handling

- [ ] All file I/O is wrapped in `try/except OSError`.
- [ ] All DB calls are wrapped in `try/except` for the DB driver's error class.
- [ ] Top-level command handlers wrap their body in `try/except`, log, and show a dialog.
- [ ] Validation errors are surfaced inline (next to the field), not only in a popup.
- [ ] The app degrades gracefully when settings are corrupt (load defaults, log a warning).

## Persistence

- [ ] Settings live in an OS-appropriate location (`appdirs` or hand-rolled `user_config_path`).
- [ ] Settings are saved on exit and restored on startup.
- [ ] Window geometry is persisted and restored.
- [ ] Last-used directory for file dialogs is persisted.
- [ ] Settings schema can evolve (unknown keys are ignored, missing keys default).
- [ ] The settings file is human-readable (JSON / TOML / INI), not binary.

## Accessibility

- [ ] Keyboard focus is set to a sensible widget on startup.
- [ ] All interactive widgets are reachable via Tab.
- [ ] Menus have `underline=` mnemonics and accelerator hints.
- [ ] Color is never the only indicator of state.
- [ ] The system font size is respected (use `TkDefaultFont`).
- [ ] High-contrast / dark mode is supported (or at least doesn't break).

## Window Management

- [ ] `WM_DELETE_WINDOW` is bound to a handler that confirms unsaved changes.
- [ ] `Toplevel` dialogs are modal only when they should be (`grab_set()`).
- [ ] Dialogs release their grab and destroy themselves on close.
- [ ] Modal dialogs are centered over their parent.
- [ ] The window title is meaningful and updates with document state.

## File Operations

- [ ] `askopenfilename` and `asksaveasfilename` are used with `filetypes` filters.
- [ ] `defaultextension` is set on save dialogs.
- [ ] Last-used directory is passed as `initialdir`.
- [ ] All paths are resolved relative to `__file__`, never to the CWD.

## Menus & Toolbars

- [ ] Menus are built via `tk.Menu`, not ttk (no ttk.Menu).
- [ ] `tearOff=False` is set globally.
- [ ] Accelerator hints match the actual `bind_all` shortcuts.
- [ ] Toolbars use `pack(side="left")` for left-to-right items, `side="right"` for right-aligned.
- [ ] Context menus appear at `event.x_root, event.y_root`, not `event.x, event.y`.

## Scrollbars

- [ ] Both `yscrollcommand=` (on the widget) and `command=` (on the scrollbar) are set.
- [ ] Mouse wheel works on Windows, macOS, AND Linux (bind both `<MouseWheel>` and `<Button-4>`/`<Button-5>`).

## Performance

- [ ] No thousands of `ttk.Label`s — use `Treeview` or `Canvas` for large lists.
- [ ] No expensive redraw on every keystroke — throttle with `after_idle`.
- [ ] The app starts in under 1 second on a cold launch.
- [ ] The UI remains responsive during long operations (no freezing).

## Packaging

- [ ] `pyinstaller --onefile --windowed main.py` produces a working binary.
- [ ] Assets (icons, default config) are bundled with `--add-data`.
- [ ] Application icon is set with `--icon=`.
- [ ] The packaged binary is tested on a clean machine.

## Documentation

- [ ] Every public class has a docstring.
- [ ] Every public method has a docstring with `Args:` and (if non-void) `Returns:`.
- [ ] The README documents how to run, how to package, and any platform-specific notes.
- [ ] A CHANGELOG tracks version-to-version changes.

## Final Pre-Ship

- [ ] Run the app and resize the window aggressively — nothing breaks.
- [ ] Try every menu item and every button.
- [ ] Trigger every error path (cancel a file dialog, type invalid input, kill the network mid-save).
- [ ] Close the window with unsaved changes — confirmation prompt fires.
- [ ] Test on Windows, macOS, AND Linux if shipping cross-platform.
- [ ] Test with the system font scaling doubled (accessibility check).
