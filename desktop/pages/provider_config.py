"""Provider configuration page for desktop UI."""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class ProviderConfigPage:
    """Page for configuring API providers (NVIDIA NIM, OpenRouter, etc.)."""

    def __init__(
        self,
        parent: ctk.CTkFrame,
        config: dict[str, str],
        on_config_change: Callable[[str, str], None],
    ) -> None:
        self.parent = parent
        self.config = config
        self.on_config_change = on_config_change
        self._controls: dict[str, ctk.CTkBaseClass] = {}

        # Create main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10), padx=10)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Provider Configuration",
            font=("Inter", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Configure API keys and URLs for LLM providers",
            font=("Inter", 12),
            text_color="gray",
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.frame, fg_color="transparent", corner_radius=0
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._build()

    def _create_api_key_input(
        self,
        parent: ctk.CTkFrame,
        label: str,
        key: str,
        hint: str | None = None,
    ) -> ctk.CTkFrame:
        """Create an API key input field with test button."""
        value = self.config.get(key, "")

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)

        ctk.CTkLabel(frame, text=label, font=("Inter", 13, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x")
        entry_frame.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            entry_frame,
            show="●",
            font=("Inter", 12),
            height=35,
            corner_radius=8,
        )
        entry.insert(0, value)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        def on_change(event=None):
            self.on_config_change(key, entry.get())

        entry.bind("<FocusOut>", on_change)
        entry.bind("<Return>", on_change)

        test_btn = ctk.CTkButton(
            entry_frame,
            text="Test",
            width=60,
            height=35,
            corner_radius=8,
            font=("Inter", 11),
            command=lambda: self._test_connection(key),
        )
        test_btn.grid(row=0, column=1)

        if hint:
            ctk.CTkLabel(
                entry_frame,
                text=hint,
                font=("Inter", 10),
                text_color="gray",
            ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        self._controls[key] = entry
        return frame

    def _create_base_url_input(
        self, parent: ctk.CTkFrame, label: str, key: str, default: str
    ) -> ctk.CTkEntry:
        """Create a base URL input field."""
        value = self.config.get(key, default)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)

        ctk.CTkLabel(frame, text=label, font=("Inter", 13, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        entry = ctk.CTkEntry(
            frame,
            font=("Inter", 12),
            height=35,
            corner_radius=8,
        )
        entry.insert(0, value)
        entry.pack(fill="x")

        def on_change(event=None):
            self.on_config_change(key, entry.get())

        entry.bind("<FocusOut>", on_change)
        entry.bind("<Return>", on_change)

        self._controls[key] = entry
        return entry

    def _test_connection(self, key: str) -> None:
        """Test API key connection."""
        from tkinter import messagebox

        value = self.config.get(key, "")
        if value and len(value) > 10:
            messagebox.showinfo(
                "Validation",
                f"{key} looks valid (verify manually with provider)",
            )
        else:
            messagebox.showwarning("Validation", f"{key} appears invalid or empty")

    def _create_card(self, title: str) -> ctk.CTkFrame:
        """Create a card-style container."""
        card = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=12,
            border_width=1,
            border_color=["gray80", "gray40"],
        )
        card.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(card, text=title, font=("Inter", 16, "bold")).pack(
            anchor="w", pady=(15, 10), padx=15
        )

        return card

    def _build(self) -> None:
        """Build the page content."""
        # NVIDIA NIM Card
        nim_card = self._create_card("🚀 NVIDIA NIM")

        ctk.CTkLabel(
            nim_card,
            text="40 req/min free tier at build.nvidia.com",
            font=("Inter", 11),
            text_color="gray",
        ).pack(anchor="w", pady=(0, 10), padx=15)

        content_frame = ctk.CTkFrame(nim_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._create_api_key_input(
            content_frame,
            "NVIDIA NIM API Key",
            "NVIDIA_NIM_API_KEY",
            "nvapi-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        )

        # OpenRouter Card
        or_card = self._create_card("🌐 OpenRouter")

        ctk.CTkLabel(
            or_card,
            text="Access hundreds of models at openrouter.ai",
            font=("Inter", 11),
            text_color="gray",
        ).pack(anchor="w", pady=(0, 10), padx=15)

        content_frame = ctk.CTkFrame(or_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._create_api_key_input(
            content_frame,
            "OpenRouter API Key",
            "OPENROUTER_API_KEY",
            "sk-or-v1-xxxxxxxx",
        )

        # Local Providers Section
        ctk.CTkLabel(
            self.scroll_frame,
            text="Local Providers (No API Key Required)",
            font=("Inter", 16, "bold"),
        ).pack(anchor="w", pady=(20, 10), padx=5)

        # LM Studio Card
        lm_card = self._create_card("💻 LM Studio")

        ctk.CTkLabel(
            lm_card,
            text="Fully local inference with LM Studio",
            font=("Inter", 11),
            text_color="gray",
        ).pack(anchor="w", pady=(0, 10), padx=15)

        content_frame = ctk.CTkFrame(lm_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._create_base_url_input(
            content_frame,
            "LM Studio URL",
            "LM_STUDIO_BASE_URL",
            "http://localhost:1234/v1",
        )

        # llama.cpp Card
        llama_card = self._create_card("🦙 llama.cpp")

        ctk.CTkLabel(
            llama_card,
            text="Lightweight local inference with llama-server",
            font=("Inter", 11),
            text_color="gray",
        ).pack(anchor="w", pady=(0, 10), padx=15)

        content_frame = ctk.CTkFrame(llama_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._create_base_url_input(
            content_frame,
            "llama.cpp URL",
            "LLAMACPP_BASE_URL",
            "http://localhost:8080/v1",
        )

    def refresh(self) -> None:
        """Refresh controls with current config values."""
        for key, control in self._controls.items():
            if isinstance(control, ctk.CTkEntry):
                control.delete(0, "end")
                control.insert(0, self.config.get(key, ""))
