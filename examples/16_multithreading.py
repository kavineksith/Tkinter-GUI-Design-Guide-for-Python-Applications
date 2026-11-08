"""Example 16 — Multithreading in Tkinter.

Tkinter is single-threaded — only the thread that called `mainloop()`
may touch widgets. This example shows the correct pattern:

  * Long work runs in a worker thread (marked daemon=True).
  * The worker pushes status messages onto a `queue.Queue`.
  * The GUI thread polls the queue with `root.after(100, poll)` and
    updates widgets safely.

If you run this and click "Block UI (don't!)" you'll see the window
freeze — that's the anti-pattern to avoid.

Run:  python examples/16_multithreading.py

Companion doc: 08_advanced_topics.md (section 8.3) and 09_common_pitfalls.md
"""
from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from tkinter import ttk


class WorkerDemo(ttk.Frame):
    """Compare the threaded and the blocking approaches side by side."""

    def __init__(self, master: tk.Misc) -> None:
        """Build the UI."""
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)

        # Queue used by the worker thread to push status updates.
        # queue.Queue is thread-safe; tkinter widgets are not.
        self.status_queue: queue.Queue[str | None] = queue.Queue()

        # ----- Top: buttons. -----
        buttons = ttk.Frame(self)
        buttons.pack(side="top", fill="x", pady=(0, 8))

        self.btn_run = ttk.Button(buttons, text="Run threaded (good)",
                                  command=self._start_worker)
        self.btn_run.pack(side="left", padx=(0, 6))

        ttk.Button(buttons, text="Block UI (don't!)",
                   command=self._block_ui).pack(side="left", padx=(0, 6))

        # ----- Middle: progress bar. -----
        self.progress = ttk.Progressbar(self, maximum=100, mode="determinate")
        self.progress.pack(side="top", fill="x", pady=(0, 8))

        # ----- Bottom: log text. -----
        log_frame = ttk.LabelFrame(self, text="Log", padding=4)
        log_frame.pack(side="top", fill="both", expand=True)
        self.log = tk.Text(log_frame, height=10, wrap="word", state="disabled")
        self.log.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        vsb.pack(side="right", fill="y")
        self.log.config(yscrollcommand=vsb.set)

        # Start polling the queue every 100 ms.
        # `after` runs the callback on the GUI thread, so we can safely
        # update widgets from inside it.
        self.after(100, self._poll_queue)

    # ----- Worker thread -----

    def _worker(self) -> None:
        """Pretend to do long work, pushing progress to the queue.

        Runs on a worker thread. NEVER touches widgets here.
        """
        for i in range(0, 101, 5):
            # Simulate some work — e.g., fetching a page, processing data.
            time.sleep(0.1)
            # Push a status message — the GUI thread will pick it up.
            self.status_queue.put(f"Progress: {i}%")
        # Sentinel: tells the poller we're done.
        self.status_queue.put(None)

    # ----- Bad pattern: block the GUI thread -----

    def _block_ui(self) -> None:
        """The anti-pattern: blocks the event loop, freezing the window.

        The progress bar won't move and the log won't update until
        the entire loop finishes. Don't do this in real apps.
        """
        self.log_append("[block] starting (UI will freeze)...")
        for i in range(0, 101, 5):
            time.sleep(0.1)             # <-- blocks the GUI thread
            self.progress["value"] = i  # widget updates, but Tk can't paint
        self.log_append("[block] done.")

    # ----- Good pattern: worker thread + queue -----

    def _start_worker(self) -> None:
        """Launch the worker thread and disable the button until done."""
        self.btn_run.config(state="disabled")
        self.log_append("[thread] starting worker...")
        # daemon=True: don't keep the process alive after the window closes.
        threading.Thread(target=self._worker, daemon=True).start()

    def _poll_queue(self) -> None:
        """Drain the status queue on the GUI thread and update widgets."""
        try:
            while True:
                msg = self.status_queue.get_nowait()
                if msg is None:
                    # Worker signaled completion.
                    self.log_append("[thread] worker finished.")
                    self.btn_run.config(state="normal")
                    return
                self.log_append(msg)
                # Parse "Progress: N%" to update the bar.
                if msg.startswith("Progress:"):
                    pct = int(msg.split(":")[1].strip().rstrip("%"))
                    self.progress["value"] = pct
        except queue.Empty:
            pass
        # Always re-schedule; never return early without rescheduling,
        # or polling stops forever.
        self.after(100, self._poll_queue)

    # ----- Helper -----

    def log_append(self, line: str) -> None:
        """Append a timestamped line to the read-only log."""
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


def main() -> None:
    """Entry point."""
    root = tk.Tk()
    root.title("Multithreading Demo")
    root.geometry("560x360")
    WorkerDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
