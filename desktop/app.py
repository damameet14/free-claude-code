"""Main CustomTkinter desktop application for Free Claude Code configuration."""

from __future__ import annotations

import threading
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

import customtkinter as ctk
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

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.settings = get_settings()
        self.config_data = load_config()

        self._setup_window()
        self._create_ui()
        self._create_pages()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("Free Claude Code")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _create_ui(self) -> None:
        """Create the main UI components."""
        # Main container with grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Left sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=180, corner_radius=10)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.sidebar.grid_rowconfigure(5, weight=1)

        # App title
        ctk.CTkLabel(
            self.sidebar,
            text="Free Claude Code",
            font=("Inter", 20, "bold"),
        ).grid(row=0, column=0, pady=(15, 5), padx=15)

        ctk.CTkLabel(
            self.sidebar,
            text="Configuration",
            font=("Inter", 12),
            text_color="gray",
        ).grid(row=1, column=0, pady=(0, 15), padx=15)

        # Navigation buttons
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self.btn_providers = ctk.CTkButton(
            self.sidebar,
            text="🔑  Providers",
            font=("Inter", 13),
            height=40,
            corner_radius=8,
            command=lambda: self._show_page("providers"),
        )
        self.btn_providers.grid(row=2, column=0, pady=5, padx=15, sticky="ew")
        self.nav_buttons["providers"] = self.btn_providers

        self.btn_models = ctk.CTkButton(
            self.sidebar,
            text="🤖  Models",
            font=("Inter", 13),
            height=40,
            corner_radius=8,
            command=lambda: self._show_page("models"),
        )
        self.btn_models.grid(row=3, column=0, pady=5, padx=15, sticky="ew")
        self.nav_buttons["models"] = self.btn_models

        self.btn_messaging = ctk.CTkButton(
            self.sidebar,
            text="💬  Messaging",
            font=("Inter", 13),
            height=40,
            corner_radius=8,
            command=lambda: self._show_page("messaging"),
        )
        self.btn_messaging.grid(row=4, column=0, pady=5, padx=15, sticky="ew")
        self.nav_buttons["messaging"] = self.btn_messaging

        self.btn_server = ctk.CTkButton(
            self.sidebar,
            text="🖥️  Server",
            font=("Inter", 13),
            height=40,
            corner_radius=8,
            command=lambda: self._show_page("server"),
        )
        self.btn_server.grid(row=5, column=0, pady=5, padx=15, sticky="ew")
        self.nav_buttons["server"] = self.btn_server

        # Bottom section with status and save
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, sticky="sew", padx=15, pady=15)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # Status indicator
        status_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        status_frame.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        self.status_indicator = ctk.CTkFrame(
            status_frame, width=12, height=12, fg_color="#666666", corner_radius=6
        )
        self.status_indicator.pack(side="left", padx=(0, 10))
        self.status_indicator.pack_propagate(False)

        self.status_text = ctk.CTkLabel(
            status_frame, text="Ready", font=("Inter", 11), text_color="gray"
        )
        self.status_text.pack(side="left")

        # Theme toggle
        self.theme_btn = ctk.CTkButton(
            bottom_frame,
            text="🌙 Dark Mode",
            font=("Inter", 11),
            height=32,
            command=self._toggle_theme,
        )
        self.theme_btn.grid(row=1, column=0, pady=(0, 10), sticky="ew")

        # Save button
        ctk.CTkButton(
            bottom_frame,
            text="💾 Save Config",
            font=("Inter", 13, "bold"),
            height=45,
            fg_color="#4caf50",
            hover_color="#45a049",
            command=self._on_save,
        ).grid(row=2, column=0, sticky="ew")

        # Content area
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _update_status_indicator(self, running: bool) -> None:
        """Update the status indicator color."""
        color = "#4caf50" if running else "#666666"
        self.status_indicator.configure(fg_color=color)

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

        self.pages: dict[str, ctk.CTkFrame] = {
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
            page.grid_forget()

        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Update button states
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=("gray70", "gray30"), state="disabled")
            else:
                btn.configure(state="normal")

    def _toggle_theme(self) -> None:
        """Toggle between dark and light mode."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.theme_btn.configure(
            text="☀️ Light Mode" if new_mode == "light" else "🌙 Dark Mode"
        )

    def _on_config_change(self, key: str, value: str) -> None:
        """Handle config change from a page."""
        self.config_data[key] = value
        self._update_status("Configuration modified - Save to apply")

    def _on_save(self) -> None:
        """Save configuration to .env file."""
        from tkinter import messagebox

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

            # Custom success message
            ctk.CTkLabel(
                self.content_frame,
                text="Configuration saved!",
                font=("Inter", 14),
                text_color="#4caf50",
                fg_color="transparent",
            ).grid(row=1, column=0, pady=10)
            self.root.after(3000, lambda: self._show_page("providers"))

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
    """Main entry point for CustomTkinter application."""
    # Suppress loguru output to console when running as GUI
    logger.remove()
    logger.add(lambda msg: None, level="WARNING")

    root = ctk.CTk()
    app = ConfigApp(root)
    root.mainloop()


def run_desktop() -> None:
    """Run the desktop application."""
    main()


if __name__ == "__main__":
    run_desktop()
