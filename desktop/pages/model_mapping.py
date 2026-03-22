"""Model mapping page for desktop UI."""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


# Provider options with descriptions
PROVIDERS = {
    "nvidia_nim": "NVIDIA NIM",
    "open_router": "OpenRouter",
    "lmstudio": "LM Studio",
    "llamacpp": "llama.cpp",
}

POPULAR_MODELS = {
    "nvidia_nim": [
        ("z-ai/glm4.7", "GLM 4.7"),
        ("z-ai/glm5", "GLM 5"),
        ("moonshotai/kimi-k2.5", "Kimi K2.5"),
        ("moonshotai/kimi-k2-thinking", "Kimi K2 Thinking"),
        ("stepfun-ai/step-3.5-flash", "Step 3.5 Flash"),
    ],
    "open_router": [
        ("deepseek/deepseek-r1-0528:free", "DeepSeek R1"),
        ("arcee-ai/trinity-large-preview:free", "Trinity"),
        ("stepfun/step-3.5-flash:free", "Step Flash"),
    ],
}


class ModelMappingPage:
    """Page for configuring model mappings."""

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
            text="Model Mapping",
            font=("Inter", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Configure which models are used for each Claude model type",
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

    def _parse_model(self, model_string: str) -> tuple[str, str]:
        """Parse model string into provider and model name."""
        if not model_string or "/" not in model_string:
            return ("nvidia_nim", "")
        provider, _, model = model_string.partition("/")
        return (provider, model)

    def _create_model_card(
        self,
        title: str,
        emoji: str,
        description: str,
        key: str,
    ) -> None:
        """Create a model selection card."""
        value = self.config.get(key, "")
        provider, model = self._parse_model(value)

        card = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=12,
            border_width=1,
            border_color=["gray80", "gray40"],
        )
        card.pack(fill="x", pady=10, padx=5)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", pady=12, padx=15)

        ctk.CTkLabel(
            header,
            text=f"{emoji} {title}",
            font=("Inter", 16, "bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            card,
            text=description,
            font=("Inter", 11),
            text_color="gray",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))

        # Provider dropdown
        ctk.CTkLabel(content, text="Provider", font=("Inter", 12, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        provider_var = ctk.StringVar(
            value=provider if provider in PROVIDERS else "nvidia_nim"
        )
        provider_dropdown = ctk.CTkOptionMenu(
            content,
            values=list(PROVIDERS.keys()),
            variable=provider_var,
            font=("Inter", 12),
            height=35,
            corner_radius=8,
        )
        provider_dropdown.pack(fill="x", pady=(0, 10))

        # Model path
        ctk.CTkLabel(
            content,
            text="Model Path",
            font=("Inter", 12, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        model_var = ctk.StringVar(value=value)
        model_entry = ctk.CTkEntry(
            content,
            font=("Inter", 12),
            height=35,
            corner_radius=8,
        )
        model_entry.insert(0, value)
        model_entry.pack(fill="x", pady=(0, 10))

        def update_model(*args):
            new_provider = provider_var.get()
            current = model_entry.get()
            if "/" in current:
                _, suffix = current.split("/", 1)
                new_value = f"{new_provider}/{suffix}"
            else:
                new_value = f"{new_provider}/"
            model_entry.delete(0, "end")
            model_entry.insert(0, new_value)
            self.on_config_change(key, new_value)

        def on_model_change(event=None):
            self.on_config_change(key, model_entry.get())

        provider_var.trace_add("write", update_model)
        model_entry.bind("<FocusOut>", on_model_change)
        model_entry.bind("<Return>", on_model_change)

        # Model suggestions
        ctk.CTkLabel(
            content,
            text="Popular models:",
            font=("Inter", 11, "bold"),
        ).pack(anchor="w", pady=(5, 8))

        suggestions_frame = ctk.CTkFrame(content, fg_color="transparent")
        suggestions_frame.pack(fill="x", pady=(0, 5))

        models = POPULAR_MODELS.get(provider, [])
        for model_path, short_name in models[:3]:
            ctk.CTkButton(
                suggestions_frame,
                text=short_name,
                width=100,
                height=30,
                font=("Inter", 10),
                fg_color="transparent",
                border_width=1,
                hover_color=["gray85", "gray45"],
                command=lambda mp=model_path, p=provider: self._set_model(
                    key, model_entry, f"{provider}/{mp}"
                ),
            ).pack(side="left", padx=3)

        self._controls[f"{key}_provider"] = provider_dropdown
        self._controls[key] = model_entry

    def _set_model(self, key: str, entry: ctk.CTkEntry, model: str) -> None:
        """Set model from suggestion."""
        entry.delete(0, "end")
        entry.insert(0, model)
        self.on_config_change(key, model)

    def _build(self) -> None:
        """Build the page content."""
        self._create_model_card(
            "Model OPUS",
            "🧠",
            "Most capable model for complex reasoning and coding",
            "MODEL_OPUS",
        )

        self._create_model_card(
            "Model SONNET",
            "⚡",
            "Balanced model for everyday tasks",
            "MODEL_SONNET",
        )

        self._create_model_card(
            "Model HAIKU",
            "🚀",
            "Fastest model for quick tasks",
            "MODEL_HAIKU",
        )

        self._create_model_card(
            "Default Model",
            "🎯",
            "Fallback model for unrecognized requests",
            "MODEL",
        )

        # Format help card
        help_card = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=12,
            fg_color=["gray90", "gray20"],
        )
        help_card.pack(fill="x", pady=15, padx=5)

        ctk.CTkLabel(
            help_card,
            text="Model Format Guide",
            font=("Inter", 14, "bold"),
        ).pack(anchor="w", pady=(15, 10), padx=15)

        help_text = """Format: provider/model/path

• NVIDIA NIM: nvidia_nim/moonshotai/kimi-k2.5
• OpenRouter: open_router/deepseek/deepseek-r1:free
• LM Studio: lmstudio/unsloth/MiniMax-M2.5-GGUF
• llama.cpp: llamacpp/local-model"""

        ctk.CTkLabel(
            help_card,
            text=help_text,
            font=("Consolas", 11),
            justify="left",
        ).pack(anchor="w", pady=(0, 15), padx=15)

    def refresh(self) -> None:
        """Refresh controls with current config values."""
        for key, control in self._controls.items():
            if isinstance(control, ctk.CTkEntry):
                control.delete(0, "end")
                control.insert(0, self.config.get(key, ""))
            elif isinstance(control, ctk.CTkOptionMenu):
                parent_key = key.replace("_provider", "")
                value = self.config.get(parent_key, "")
                provider, _ = self._parse_model(value)
                control.set(provider)
