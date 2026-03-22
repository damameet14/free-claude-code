"""Main tkinter desktop application for Free Claude Code configuration."""

from __future__ import annotations

import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    pass

from config.settings import get_settings
from desktop.pages.messaging_config import MessagingConfigPage
from desktop.pages.model_mapping import ModelMappingPage
from desktop.pages.provider_config import ProviderConfigPage
from desktop.pages.server_control import ServerControlPage
from desktop.utils import load_config, save_config, validate_config

# Server thread globals
_server_thread: threading.Thread | None = None
_server_running = False
_server_shutdown_event = threading.Event()


def run_fastapi_server(host: str, port: int, shutdown_event: threading.Event) -> None:
    """Run FastAPI server in a separate thread."""
    import asyncio
    import uvicorn

    from api.app import app

    global _server_running
    _server_running = True

    async def serve() -> None:
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=False,
            lifespan="on",
        )
        server = uvicorn.Server(config)

        # Start server in background task
        task = asyncio.create_task(server.serve())

        # Wait for shutdown signal
        while not shutdown_event.is_set():
            await asyncio.sleep(0.1)

        # Graceful shutdown
        server.should_exit = True
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    try:
        asyncio.run(serve())
    finally:
        _server_running = False


def start_server(host: str, port: int) -> bool:
    """Start the FastAPI server in a background thread."""
    global _server_thread, _server_running, _server_shutdown_event

    if _server_running and _server_thread and _server_thread.is_alive():
        return True

    _server_shutdown_event.clear()
    _server_thread = threading.Thread(
        target=run_fastapi_server,
        args=(host, port, _server_shutdown_event),
        daemon=True,
    )
    _server_thread.start()

    # Wait a moment to verify server started
    import time

    time.sleep(1.5)
    return _server_thread.is_alive()


def stop_server() -> None:
    """Signal the server to stop."""
    global _server_shutdown_event, _server_thread
    _server_shutdown_event.set()

    if _server_thread and _server_thread.is_alive():
        _server_thread.join(timeout=5)


class ConfigApp:
    """Main application controller for the desktop UI."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.settings = get_settings()
        self.config_data = load_config()

        self._setup_window()
        self._create_ui()
        self._create_pages()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("Free Claude Code")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)

        # Set theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure colors
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        self.style.configure("TButton", padding=5)

        self.root.configure(bg="#1e1e1e")

    def _create_ui(self) -> None:
        """Create the main UI components."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left sidebar with navigation
        self.sidebar = ttk.Frame(self.main_frame, width=150)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar.pack_propagate(False)

        # Navigation buttons
        ttk.Label(self.sidebar, text="Navigation", font=("Arial", 12, "bold")).pack(
            pady=10
        )

        self.nav_buttons: dict[str, ttk.Button] = {}

        self.btn_providers = ttk.Button(
            self.sidebar,
            text="Providers",
            command=lambda: self._show_page("providers"),
        )
        self.btn_providers.pack(fill=tk.X, pady=5)
        self.nav_buttons["providers"] = self.btn_providers

        self.btn_models = ttk.Button(
            self.sidebar,
            text="Models",
            command=lambda: self._show_page("models"),
        )
        self.btn_models.pack(fill=tk.X, pady=5)
        self.nav_buttons["models"] = self.btn_models

        self.btn_messaging = ttk.Button(
            self.sidebar,
            text="Messaging",
            command=lambda: self._show_page("messaging"),
        )
        self.btn_messaging.pack(fill=tk.X, pady=5)
        self.nav_buttons["messaging"] = self.btn_messaging

        self.btn_server = ttk.Button(
            self.sidebar,
            text="Server",
            command=lambda: self._show_page("server"),
        )
        self.btn_server.pack(fill=tk.X, pady=5)
        self.nav_buttons["server"] = self.btn_server

        # Separator
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        # Save button
        ttk.Button(
            self.sidebar,
            text="Save Config",
            command=self._on_save,
        ).pack(fill=tk.X, pady=5)

        # Status section
        self.status_frame = ttk.Frame(self.sidebar)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        self.status_indicator = tk.Canvas(
            self.status_frame, width=12, height=12, bg="#1e1e1e", highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self._update_status_indicator(False)

        self.status_text = ttk.Label(self.status_frame, text="Ready")
        self.status_text.pack(side=tk.LEFT)

        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _update_status_indicator(self, running: bool) -> None:
        """Update the status indicator color."""
        color = "#4caf50" if running else "#9e9e9e"
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline="")

    def _create_pages(self) -> None:
        """Create the page instances."""
        self.provider_page = ProviderConfigPage(
            self.content_frame,
            self.config_data,
            on_config_change=self._on_config_change,
        )
        self.model_page = ModelMappingPage(
            self.content_frame,
            self.config_data,
            on_config_change=self._on_config_change,
        )
        self.messaging_page = MessagingConfigPage(
            self.content_frame,
            self.config_data,
            on_config_change=self._on_config_change,
        )
        self.server_page = ServerControlPage(
            self.content_frame,
            self.config_data,
            on_start_server=self._on_start_server,
            on_stop_server=self._on_stop_server,
            on_open_browser=self._on_open_browser,
            on_config_change=self._on_config_change,
        )

        self.pages: dict[str, ttk.Frame] = {
            "providers": self.provider_page.frame,
            "models": self.model_page.frame,
            "messaging": self.messaging_page.frame,
            "server": self.server_page.frame,
        }

        # Show first page
        self._show_page("providers")

        # Start status updater
        self._start_status_updater()

    def _show_page(self, page_name: str) -> None:
        """Show the selected page."""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()

        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)

        # Update button states
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(state="disabled")
            else:
                btn.configure(state="normal")

    def _on_config_change(self, key: str, value: str) -> None:
        """Handle config change from a page."""
        self.config_data[key] = value
        self._update_status("Configuration modified - Save to apply")

    def _on_save(self) -> None:
        """Save configuration to .env file."""
        try:
            # Validate before saving
            errors = validate_config(self.config_data)
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return

            # Save configuration
            save_config(self.config_data)

            # Refresh settings cache
            from config.settings import get_settings

            if hasattr(get_settings, "cache_clear"):
                get_settings.cache_clear()  # type: ignore[attr-defined]

            self._update_status("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as ex:
            messagebox.showerror("Save Error", str(ex))

    def _on_start_server(self) -> bool:
        """Start the FastAPI server."""
        host = self.config_data.get("host", "0.0.0.0")
        port = int(self.config_data.get("port", 8082))

        self._update_status("Starting server...")
        success = start_server(host, port)
        if success:
            self._update_status(f"Server running on {host}:{port}")
            self._update_status_indicator(True)
            self.server_page.set_running(True)
        else:
            self._update_status("Failed to start server")
        return success

    def _on_stop_server(self) -> None:
        """Stop the FastAPI server."""
        stop_server()
        self._update_status("Server stopped")
        self._update_status_indicator(False)
        self.server_page.set_running(False)

    def _on_open_browser(self) -> None:
        """Open the proxy in browser."""
        port = self.config_data.get("port", 8082)
        webbrowser.open(f"http://localhost:{port}")

    def _update_status(self, message: str) -> None:
        """Update the status text."""
        self.status_text.configure(text=message)

    def _start_status_updater(self) -> None:
        """Start background status updates."""

        def check_status():
            running = _server_thread is not None and _server_thread.is_alive()
            self._update_status_indicator(running)
            self.server_page.set_running(running)
            self.root.after(2000, check_status)

        self.root.after(2000, check_status)


def main() -> None:
    """Main entry point for tkinter application."""
    # Suppress loguru output to console when running as GUI
    logger.remove()
    logger.add(lambda msg: None, level="WARNING")

    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()


def run_desktop() -> None:
    """Run the desktop application."""
    main()


if __name__ == "__main__":
    run_desktop()
