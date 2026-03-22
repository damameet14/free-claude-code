"""Provider configuration page for desktop UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class ProviderConfigPage:
    """Page for configuring API providers (NVIDIA NIM, OpenRouter, etc.)."""

    def __init__(
        self,
        parent: ttk.Frame,
        config: dict[str, str],
        on_config_change: Callable[[str, str], None],
    ) -> None:
        self.parent = parent
        self.config = config
        self.on_config_change = on_config_change
        self._controls: dict[str, tk.Widget] = {}

        self.frame = ttk.Frame(parent)
        self._build()

    def _create_api_key_input(
        self,
        parent: ttk.Frame,
        label: str,
        key: str,
        hint: str | None = None,
    ) -> ttk.Frame:
        """Create an API key input field."""
        value = self.config.get(key, "")

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label, font=("Arial", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 2)
        )

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill=tk.X)

        var = tk.StringVar(value=value)
        entry = ttk.Entry(
            entry_frame, textvariable=var, show="*" if "key" in key.lower() else ""
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def on_change(*args):
            self.on_config_change(key, var.get())

        var.trace_add("write", on_change)
        self._controls[key] = entry

        ttk.Button(
            entry_frame,
            text="Test",
            width=8,
            command=lambda: self._test_connection(key),
        ).pack(side=tk.RIGHT)

        return frame

    def _create_base_url_input(
        self,
        parent: ttk.Frame,
        label: str,
        key: str,
        default: str,
    ) -> ttk.Entry:
        """Create a base URL input field."""
        value = self.config.get(key, default)

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label, font=("Arial", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 2)
        )

        var = tk.StringVar(value=value)
        entry = ttk.Entry(frame, textvariable=var)
        entry.pack(fill=tk.X)

        def on_change(*args):
            self.on_config_change(key, var.get())

        var.trace_add("write", on_change)
        self._controls[key] = entry

        return entry

    def _test_connection(self, key: str) -> None:
        """Test API key connection."""
        value = self.config.get(key, "")
        if value and len(value) > 10:
            tk.messagebox.showinfo("Validation", f"{key} looks valid (verify manually)")
        else:
            tk.messagebox.showwarning("Validation", f"{key} appears invalid")

    def _build(self) -> None:
        """Build the page content."""
        # Title
        ttk.Label(
            self.frame, text="Provider Configuration", font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))

        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Scrollable frame for content
        canvas = tk.Canvas(self.frame, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW, width=700)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # NVIDIA NIM Section
        nim_frame = ttk.LabelFrame(scroll_frame, text="NVIDIA NIM", padding=10)
        nim_frame.pack(fill=tk.X, pady=10, padx=5)

        ttk.Label(
            nim_frame,
            text="40 req/min free tier at build.nvidia.com",
            foreground="gray",
        ).pack(anchor=tk.W, pady=(0, 5))

        self._create_api_key_input(
            nim_frame,
            "NVIDIA NIM API Key",
            "NVIDIA_NIM_API_KEY",
            "nvapi-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        )

        # OpenRouter Section
        or_frame = ttk.LabelFrame(scroll_frame, text="OpenRouter", padding=10)
        or_frame.pack(fill=tk.X, pady=10, padx=5)

        ttk.Label(
            or_frame,
            text="Access hundreds of models at openrouter.ai",
            foreground="gray",
        ).pack(anchor=tk.W, pady=(0, 5))

        self._create_api_key_input(
            or_frame,
            "OpenRouter API Key",
            "OPENROUTER_API_KEY",
            "sk-or-v1-xxxxxxxx",
        )

        # Local Providers Section
        ttk.Label(
            scroll_frame,
            text="Local Providers (No API Key Required)",
            font=("Arial", 12, "bold"),
        ).pack(anchor=tk.W, pady=(20, 10))

        # LM Studio
        lm_frame = ttk.LabelFrame(scroll_frame, text="LM Studio", padding=10)
        lm_frame.pack(fill=tk.X, pady=10, padx=5)

        ttk.Label(
            lm_frame,
            text="Fully local inference with LM Studio",
            foreground="gray",
        ).pack(anchor=tk.W, pady=(0, 5))

        self._create_base_url_input(
            lm_frame,
            "LM Studio URL",
            "LM_STUDIO_BASE_URL",
            "http://localhost:1234/v1",
        )

        # llama.cpp
        llama_frame = ttk.LabelFrame(scroll_frame, text="llama.cpp", padding=10)
        llama_frame.pack(fill=tk.X, pady=10, padx=5)

        ttk.Label(
            llama_frame,
            text="Lightweight local inference with llama-server",
            foreground="gray",
        ).pack(anchor=tk.W, pady=(0, 5))

        self._create_base_url_input(
            llama_frame,
            "llama.cpp URL",
            "LLAMACPP_BASE_URL",
            "http://localhost:8080/v1",
        )

    def refresh(self) -> None:
        """Refresh controls with current config values."""
        for key, control in self._controls.items():
            if isinstance(control, ttk.Entry):
                control.delete(0, tk.END)
                control.insert(0, self.config.get(key, ""))
