"""Server control page for desktop UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class ServerControlPage:
    """Page for controlling the server - start/stop and view status."""

    def __init__(
        self,
        parent: ttk.Frame,
        config: dict[str, str],
        on_start_server: Callable[[], bool],
        on_stop_server: Callable[[], None],
        on_open_browser: Callable[[], None],
        on_config_change: Callable[[str, str], None] | None = None,
    ) -> None:
        self.parent = parent
        self.config = config
        self.on_start_server = on_start_server
        self.on_stop_server = on_stop_server
        self.on_open_browser = on_open_browser
        self.on_config_change = on_config_change

        self._is_running = False
        self._log_entries: list[str] = []

        self.frame = ttk.Frame(parent)
        self._build()

    def _create_numeric_input(
        self,
        parent: ttk.Frame,
        label: str,
        key: str,
        default: str,
    ) -> ttk.Entry:
        """Create a numeric input field."""
        value = self.config.get(key, default)

        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(frame, text=label).pack(anchor=tk.W)

        var = tk.StringVar(value=value)
        entry = ttk.Entry(frame, textvariable=var, width=15)
        entry.pack(fill=tk.X)

        def on_change(*args):
            key_mapping = {
                "port": "PORT",
                "rate_limit": "PROVIDER_RATE_LIMIT",
                "rate_window": "PROVIDER_RATE_WINDOW",
                "max_concurrency": "PROVIDER_MAX_CONCURRENCY",
                "read_timeout": "HTTP_READ_TIMEOUT",
                "write_timeout": "HTTP_WRITE_TIMEOUT",
                "connect_timeout": "HTTP_CONNECT_TIMEOUT",
            }
            setting_key = key_mapping.get(key, key.upper())
            self.parent.master.winfo_toplevel().event_generate(
                "<<ConfigChange>>",
                when="tail",
                x=hash(setting_key),
                y=hash(var.get()),
            )

        var.trace_add("write", on_change)

        # Store reference
        setattr(self, f"_{key}_var", var)

        return entry

    def _on_start(self) -> None:
        """Start the server."""
        if self._is_running:
            return

        self._update_status("Starting server...")
        success = self.on_start_server()
        if success:
            self._is_running = True
            self._update_ui_state()
            self._add_log("Server started successfully")
        else:
            self._update_status("Failed to start server")
            self._add_log("ERROR: Server failed to start")

    def _on_stop(self) -> None:
        """Stop the server."""
        if not self._is_running:
            return

        self._update_status("Stopping server...")
        self.on_stop_server()
        self._is_running = False
        self._update_ui_state()
        self._add_log("Server stopped")

    def _on_open(self) -> None:
        """Open in browser."""
        if not self._is_running:
            tk.messagebox.showwarning("Server Not Running", "Server is not running")
            return
        self.on_open_browser()

    def _update_status(self, message: str) -> None:
        """Update status text."""
        if hasattr(self, "_status_label"):
            self._status_label.config(text=message)

    def _update_ui_state(self) -> None:
        """Update button states based on server status."""
        if self._start_btn and self._stop_btn:
            self._start_btn.config(state="disabled" if self._is_running else "normal")
            self._stop_btn.config(state="normal" if self._is_running else "disabled")

    def _add_log(self, message: str) -> None:
        """Add entry to log display."""
        self._log_entries.append(message)
        if len(self._log_entries) > 100:
            self._log_entries = self._log_entries[-100:]

        if hasattr(self, "_log_text"):
            self._log_text.config(state="normal")
            self._log_text.delete(1.0, tk.END)
            for line in self._log_entries:
                self._log_text.insert(tk.END, line + "\n")
            self._log_text.config(state="disabled")
            self._log_text.see(tk.END)

    def _build(self) -> None:
        """Build the page content."""
        # Title
        ttk.Label(self.frame, text="Server Control", font=("Arial", 16, "bold")).pack(
            anchor=tk.W, pady=(0, 10)
        )

        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Server settings
        settings_frame = ttk.LabelFrame(self.frame, text="Server Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=10)

        settings_row = ttk.Frame(settings_frame)
        settings_row.pack(fill=tk.X, pady=5)

        # Port
        port_frame = ttk.Frame(settings_row)
        port_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(port_frame, text="Port").pack(anchor=tk.W)
        self._port_var = tk.StringVar(value=self.config.get("PORT", "8082"))
        port_entry = ttk.Entry(port_frame, textvariable=self._port_var, width=15)
        port_entry.pack(fill=tk.X)

        def on_port_change(*args):
            if self.on_config_change:
                self.on_config_change("PORT", self._port_var.get())

        self._port_var.trace_add("write", on_port_change)

        # Host
        host_frame = ttk.Frame(settings_row)
        host_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(host_frame, text="Host").pack(anchor=tk.W)
        self._host_var = tk.StringVar(value=self.config.get("host", "0.0.0.0"))
        host_entry = ttk.Entry(host_frame, textvariable=self._host_var, width=20)
        host_entry.pack(fill=tk.X)

        def on_host_change(*args):
            if self.on_config_change:
                self.on_config_change("host", self._host_var.get())

        self._host_var.trace_add("write", on_host_change)

        # Control buttons
        control_frame = ttk.LabelFrame(self.frame, text="Server Control", padding=15)
        control_frame.pack(fill=tk.X, pady=10)

        self._status_label = ttk.Label(
            control_frame, text="Server is stopped", font=("Arial", 11)
        )
        self._status_label.pack(pady=(0, 15))

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack()

        self._start_btn = ttk.Button(
            btn_frame,
            text="Start Server",
            command=self._on_start,
            width=15,
        )
        self._start_btn.pack(side=tk.LEFT, padx=5)

        self._stop_btn = ttk.Button(
            btn_frame,
            text="Stop Server",
            command=self._on_stop,
            width=15,
            state="disabled",
        )
        self._stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Open in Browser",
            command=self._on_open,
            width=15,
        ).pack(side=tk.LEFT, padx=5)

        # Connection info
        info_frame = ttk.LabelFrame(self.frame, text="Connection Info", padding=10)
        info_frame.pack(fill=tk.X, pady=10)

        port_val = self.config.get("PORT", "8082")
        info_text = f"""Server will run at: http://0.0.0.0:{port_val}

Claude Code environment variables:
ANTHROPIC_BASE_URL=http://localhost:{port_val}
ANTHROPIC_AUTH_TOKEN=freecc

Run 'claude' in your terminal after starting the server."""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=5)

        # Logs
        ttk.Label(self.frame, text="Server Logs", font=("Arial", 12, "bold")).pack(
            anchor=tk.W, pady=(20, 5)
        )

        log_frame = ttk.Frame(self.frame)
        log_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._log_text = tk.Text(
            log_frame,
            height=10,
            state="disabled",
            bg="#2d2d2d",
            fg="#ffffff",
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set,
        )
        self._log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._log_text.yview)

    def set_running(self, running: bool) -> None:
        """Update running state from external source."""
        self._is_running = running
        self._update_ui_state()
        if running:
            self._update_status("Server is running")
        else:
            self._update_status("Server is stopped")
