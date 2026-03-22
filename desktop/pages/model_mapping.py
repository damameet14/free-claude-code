"""Model mapping page for desktop UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


# Provider options
PROVIDERS = {
    "nvidia_nim": "NVIDIA NIM",
    "open_router": "OpenRouter",
    "lmstudio": "LM Studio",
    "llamacpp": "llama.cpp",
}

POPULAR_MODELS = {
    "nvidia_nim": [
        "z-ai/glm4.7",
        "z-ai/glm5",
        "moonshotai/kimi-k2.5",
        "moonshotai/kimi-k2-thinking",
        "stepfun-ai/step-3.5-flash",
        "qwen/qwen3.5-397b-a17b",
        "minimaxai/minimax-m2.5",
    ],
    "open_router": [
        "deepseek/deepseek-r1-0528:free",
        "arcee-ai/trinity-large-preview:free",
        "stepfun/step-3.5-flash:free",
        "openai/gpt-oss-120b:free",
    ],
}


class ModelMappingPage:
    """Page for configuring model mappings."""

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

    def _parse_model(self, model_string: str) -> tuple[str, str]:
        """Parse model string into provider and model name."""
        if not model_string or "/" not in model_string:
            return ("nvidia_nim", "")
        provider, _, model = model_string.partition("/")
        return (provider, model)

    def _create_model_row(
        self,
        parent: ttk.Frame,
        label: str,
        description: str,
        key: str,
    ) -> ttk.Frame:
        """Create a model selection row."""
        value = self.config.get(key, "")
        provider, model = self._parse_model(value)

        frame = ttk.LabelFrame(parent, text=label, padding=10)
        frame.pack(fill=tk.X, pady=8, padx=5)

        ttk.Label(frame, text=description, foreground="gray").pack(
            anchor=tk.W, pady=(0, 10)
        )

        # Provider dropdown
        provider_frame = ttk.Frame(frame)
        provider_frame.pack(fill=tk.X, pady=5)

        ttk.Label(provider_frame, text="Provider:").pack(side=tk.LEFT, padx=(0, 10))

        provider_var = tk.StringVar(
            value=provider if provider in PROVIDERS else "nvidia_nim"
        )
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=provider_var,
            values=list(PROVIDERS.keys()),
            state="readonly",
            width=20,
        )
        provider_combo.pack(side=tk.LEFT)

        # Model input
        model_frame = ttk.Frame(frame)
        model_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_frame, text="Model Path:").pack(side=tk.LEFT, padx=(0, 10))

        model_var = tk.StringVar(value=value)
        model_entry = ttk.Entry(model_frame, textvariable=model_var)
        model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def on_provider_change(*args):
            new_provider = provider_var.get()
            current = model_var.get()
            if "/" in current:
                _, _, suffix = current.partition("/")
                if suffix:
                    new_value = f"{new_provider}/{suffix}"
                else:
                    new_value = f"{new_provider}/"
            else:
                new_value = f"{new_provider}/"
            model_var.set(new_value)
            self.on_config_change(key, new_value)

        provider_var.trace_add("write", on_provider_change)

        def on_model_change(*args):
            self.on_config_change(key, model_var.get())

        model_var.trace_add("write", on_model_change)

        self._controls[f"{key}_provider"] = provider_combo
        self._controls[key] = model_entry

        # Quick model suggestions
        suggestions_frame = ttk.Frame(frame)
        suggestions_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(suggestions_frame, text="Popular models:", font=("Arial", 9)).pack(
            anchor=tk.W
        )

        models = POPULAR_MODELS.get(provider, [])
        for model in models[:4]:
            short_name = model.split("/")[-1][:20]
            ttk.Button(
                suggestions_frame,
                text=short_name,
                command=lambda p=provider, m=model: (
                    model_var.set(f"{p}/{m}"),
                    self.on_config_change(key, f"{p}/{m}"),
                ),
            ).pack(side=tk.LEFT, padx=2)

        return frame

    def _build(self) -> None:
        """Build the page content."""
        # Title
        ttk.Label(self.frame, text="Model Mapping", font=("Arial", 16, "bold")).pack(
            anchor=tk.W, pady=(0, 10)
        )

        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(
            self.frame,
            text="Configure which provider models are used for each Claude model type. "
            "Format: provider_prefix/model/path",
            foreground="gray",
        ).pack(anchor=tk.W, pady=(0, 15))

        # Scrollable frame
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

        # Model rows
        self._create_model_row(
            scroll_frame,
            "Model OPUS",
            "Most capable model for complex reasoning and coding",
            "MODEL_OPUS",
        )

        self._create_model_row(
            scroll_frame,
            "Model SONNET",
            "Balanced model for everyday tasks",
            "MODEL_SONNET",
        )

        self._create_model_row(
            scroll_frame,
            "Model HAIKU",
            "Fastest model for quick tasks",
            "MODEL_HAIKU",
        )

        self._create_model_row(
            scroll_frame,
            "Default Model",
            "Fallback model for unrecognized Claude model requests",
            "MODEL",
        )

        # Help text
        help_frame = ttk.LabelFrame(scroll_frame, text="Model Format Guide", padding=10)
        help_frame.pack(fill=tk.X, pady=20, padx=5)

        help_text = """Use format: provider/model/name

• NVIDIA NIM: nvidia_nim/moonshotai/kimi-k2.5
• OpenRouter: open_router/deepseek/deepseek-r1:free
• LM Studio: lmstudio/unsloth/MiniMax-M2.5-GGUF
• llama.cpp: llamacpp/local-model"""

        ttk.Label(help_frame, text=help_text, justify=tk.LEFT).pack(anchor=tk.W)

    def refresh(self) -> None:
        """Refresh controls with current config values."""
        for key, control in self._controls.items():
            if isinstance(control, ttk.Entry):
                control.delete(0, tk.END)
                control.insert(0, self.config.get(key, ""))
            elif isinstance(control, ttk.Combobox) and key.endswith("_provider"):
                parent_key = key.replace("_provider", "")
                value = self.config.get(parent_key, "")
                provider, _ = self._parse_model(value)
                control.set(provider)
