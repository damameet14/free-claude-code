"""Server control page for desktop UI."""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class ServerControlPage:
    """Page for controlling the server - start/stop and view status."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
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

        # Create main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        self._build()

    def _on_start(self) -> None:
        """Start the server."""
        if self._is_running:
            return

        self._update_status("Starting server...")
        success = self.on_start_server()
        if success:
            self._is_running = True
            self._update_ui_state()
            self._add_log("✅ Server started successfully")
        else:
            self._update_status("Failed to start server")
            self._add_log("❌ ERROR: Server failed to start")

    def _on_stop(self) -> None:
        """Stop the server."""
        if not self._is_running:
            return

        self._update_status("Stopping server...")
        self.on_stop_server()
        self._is_running = False
        self._update_ui_state()
        self._add_log("⏹️ Server stopped")

    def _on_open(self) -> None:
        """Open in browser."""
        if not self._is_running:
            ctk.CTkLabel(
                self.status_frame,
                text="Server is not running!",
                text_color="#f44336",
            ).pack_forget()
            return
        self.on_open_browser()

    def _update_status(self, message: str) -> None:
        """Update status text."""
        if hasattr(self, "_status_label"):
            self._status_label.configure(text=message)

    def _update_ui_state(self) -> None:
        """Update button states based on server status."""
        if self._start_btn and self._stop_btn:
            if self._is_running:
                self._start_btn.configure(
                    state="disabled",
                    fg_color="#45a049",
                )
                self._stop_btn.configure(
                    state="normal",
                    fg_color="#f44336",
                )
            else:
                self._start_btn.configure(
                    state="normal",
                    fg_color="#4caf50",
                )
                self._stop_btn.configure(
                    state="disabled",
                    fg_color="#666666",
                )

    def _add_log(self, message: str) -> None:
        """Add entry to log display."""
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self._log_entries.append(f"[{timestamp}] {message}")
        if len(self._log_entries) > 100:
            self._log_entries = self._log_entries[-100:]

        if hasattr(self, "_log_text"):
            self._log_text.configure(state="normal")
            self._log_text.delete(1.0, "end")
            for line in self._log_entries:
                self._log_text.insert("end", line + "\n")
            self._log_text.configure(state="disabled")
            self._log_text.see("end")

    def _build(self) -> None:
        """Build the page content."""
        # Header
        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10), padx=10)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Server Control",
            font=("Inter", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Start/stop the proxy server and monitor activity",
            font=("Inter", 12),
            text_color="gray",
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            self.frame, fg_color="transparent", corner_radius=0
        )
        scroll_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Server Settings Card
        settings_card = ctk.CTkFrame(
            scroll_frame,
            corner_radius=12,
            border_width=1,
            border_color=["gray80", "gray40"],
        )
        settings_card.pack(fill="x", pady=10, padx=5)
        settings_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            settings_card,
            text="⚙️ Server Settings",
            font=("Inter", 16, "bold"),
        ).pack(anchor="w", pady=(15, 10), padx=15)

        settings_row = ctk.CTkFrame(settings_card, fg_color="transparent")
        settings_row.pack(fill="x", padx=15, pady=(0, 15))
        settings_row.grid_columnconfigure((0, 1), weight=1)

        # Port
        port_frame = ctk.CTkFrame(settings_row, fg_color="transparent")
        port_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(port_frame, text="Port", font=("Inter", 12, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        self._port_var = ctk.StringVar(value=self.config.get("PORT", "8082"))
        port_entry = ctk.CTkEntry(
            port_frame,
            font=("Inter", 12),
            height=35,
            corner_radius=8,
        )
        port_entry.insert(0, self.config.get("PORT", "8082"))
        port_entry.pack(fill="x")

        def on_port_change(event=None):
            if self.on_config_change:
                self.on_config_change("PORT", port_entry.get())

        port_entry.bind("<FocusOut>", on_port_change)
        port_entry.bind("<Return>", on_port_change)

        self._port_var.trace_add("write", lambda *args: self._update_connection_info())
        self._port_entry = port_entry

        # Host
        host_frame = ctk.CTkFrame(settings_row, fg_color="transparent")
        host_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        ctk.CTkLabel(host_frame, text="Host", font=("Inter", 12, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        self._host_var = ctk.StringVar(value=self.config.get("host", "0.0.0.0"))
        host_entry = ctk.CTkEntry(
            host_frame,
            font=("Inter", 12),
            height=35,
            corner_radius=8,
        )
        host_entry.insert(0, self.config.get("host", "0.0.0.0"))
        host_entry.pack(fill="x")

        def on_host_change(event=None):
            if self.on_config_change:
                self.on_config_change("host", host_entry.get())

        host_entry.bind("<FocusOut>", on_host_change)
        host_entry.bind("<Return>", on_host_change)

        # Control Card
        control_card = ctk.CTkFrame(
            scroll_frame,
            corner_radius=12,
            border_width=1,
            border_color=["gray80", "gray40"],
        )
        control_card.pack(fill="x", pady=10, padx=5)

        self.status_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=15, pady=(15, 10))

        self._status_label = ctk.CTkLabel(
            self.status_frame,
            text="⏹️ Server is stopped",
            font=("Inter", 16, "bold"),
            text_color="#f44336",
        )
        self._status_label.pack(side="left")

        btn_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._start_btn = ctk.CTkButton(
            btn_frame,
            text="▶️  Start Server",
            font=("Inter", 14, "bold"),
            height=45,
            corner_radius=10,
            fg_color="#4caf50",
            hover_color="#45a049",
            command=self._on_start,
        )
        self._start_btn.pack(side="left", padx=(0, 10))

        self._stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹️  Stop Server",
            font=("Inter", 14, "bold"),
            height=45,
            corner_radius=10,
            fg_color="#666666",
            state="disabled",
            command=self._on_stop,
        )
        self._stop_btn.pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🌐 Open Browser",
            font=("Inter", 14, "bold"),
            height=45,
            corner_radius=10,
            command=self._on_open,
        ).pack(side="left", padx=5)

        # Connection Info Card
        self.info_card = ctk.CTkFrame(
            scroll_frame,
            corner_radius=12,
            border_width=1,
            border_color=["gray80", "gray40"],
        )
        self.info_card.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            self.info_card,
            text="ℹ️ Connection Info",
            font=("Inter", 16, "bold"),
        ).pack(anchor="w", pady=(15, 10), padx=15)

        self._info_text_label = ctk.CTkLabel(
            self.info_card,
            text="",
            font=("Consolas", 12),
            justify="left",
        )
        self._info_text_label.pack(anchor="w", padx=15, pady=(0, 15))

        self._update_connection_info()

        # Logs Card
        log_card = ctk.CTkFrame(
            scroll_frame,
            corner_radius=12,
            border_width=1,
            border_color=["gray80", "gray40"],
        )
        log_card.pack(fill="both", expand=True, pady=10, padx=5)

        ctk.CTkLabel(
            log_card,
            text="📋 Server Logs",
            font=("Inter", 16, "bold"),
        ).pack(anchor="w", pady=(15, 10), padx=15)

        self._log_text = ctk.CTkTextbox(
            log_card,
            font=("Consolas", 11),
            corner_radius=8,
            fg_color=["gray85", "gray20"],
            text_color=["gray20", "gray90"],
            state="disabled",
        )
        self._log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _update_connection_info(self) -> None:
        """Update connection info text."""
        port = self.config.get("PORT", "8082")
        info_text = f"""Will run at: http://0.0.0.0:{port}

Environment variables:
  ANTHROPIC_BASE_URL=http://localhost:{port}
  ANTHROPIC_AUTH_TOKEN=freecc"""
        self._info_text_label.configure(text=info_text)

    def set_running(self, running: bool) -> None:
        """Update running state from external source."""
        self._is_running = running
        self._update_ui_state()
        if running:
            self._update_status("🟢 Server is running")
            self._status_label.configure(text_color="#4caf50")
        else:
            self._update_status("⏹️ Server is stopped")
            self._status_label.configure(text_color="#f44336")
