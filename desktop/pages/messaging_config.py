"""Messaging platform configuration page for desktop UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class MessagingConfigPage:
    """Page for configuring Discord and Telegram bot settings."""

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

    def _create_input(
        self,
        parent: ttk.Frame,
        label: str,
        key: str,
        hint: str | None = None,
        password: bool = False,
    ) -> ttk.Entry:
        """Create a text input field."""
        value = self.config.get(key, "")

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label, font=("Arial", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 2)
        )

        var = tk.StringVar(value=value)
        entry = ttk.Entry(frame, textvariable=var, show="*" if password else "")
        entry.pack(fill=tk.X)

        if hint:
            ttk.Label(frame, text=hint, foreground="gray", font=("Arial", 8)).pack(
                anchor=tk.W, pady=(2, 0)
            )

        def on_change(*args):
            self.on_config_change(key, var.get())

        var.trace_add("write", on_change)
        self._controls[key] = entry

        return entry

    def _create_dropdown(
        self,
        parent: ttk.Frame,
        label: str,
        key: str,
        options: list[str],
    ) -> ttk.Combobox:
        """Create a dropdown field."""
        value = self.config.get(key, options[0] if options else "")

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=label, font=("Arial", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 2)
        )

        var = tk.StringVar(value=value)
        combo = ttk.Combobox(frame, textvariable=var, values=options, state="readonly")
        combo.pack(fill=tk.X)

        def on_change(*args):
            self.on_config_change(key, var.get())

        var.trace_add("write", on_change)
        self._controls[key] = combo

        return combo

    def _build(self) -> None:
        """Build the page content."""
        # Title
        ttk.Label(
            self.frame, text="Messaging Platform", font=("Arial", 16, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))

        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(
            self.frame,
            text="Configure Discord or Telegram bot for remote Claude Code control.",
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

        # Platform selection
        platform_frame = ttk.LabelFrame(
            scroll_frame, text="Platform Selection", padding=10
        )
        platform_frame.pack(fill=tk.X, pady=10, padx=5)

        self._create_dropdown(
            platform_frame,
            "Messaging Platform",
            "MESSAGING_PLATFORM",
            ["discord", "telegram"],
        )

        # Discord Section
        discord_frame = ttk.LabelFrame(
            scroll_frame, text="Discord Configuration", padding=10
        )
        discord_frame.pack(fill=tk.X, pady=10, padx=5)

        self._create_input(
            discord_frame,
            "Discord Bot Token",
            "DISCORD_BOT_TOKEN",
            "Get from Discord Developer Portal",
            password=True,
        )

        self._create_input(
            discord_frame,
            "Allowed Discord Channels",
            "ALLOWED_DISCORD_CHANNELS",
            "Comma-separated channel IDs (e.g., 123456789,987654321)",
        )

        # Telegram Section
        telegram_frame = ttk.LabelFrame(
            scroll_frame, text="Telegram Configuration", padding=10
        )
        telegram_frame.pack(fill=tk.X, pady=10, padx=5)

        self._create_input(
            telegram_frame,
            "Telegram Bot Token",
            "TELEGRAM_BOT_TOKEN",
            "Get from @BotFather",
            password=True,
        )

        self._create_input(
            telegram_frame,
            "Allowed Telegram User ID",
            "ALLOWED_TELEGRAM_USER_ID",
            "Your Telegram user ID (from @userinfobot)",
        )

        # Agent Workspace
        workspace_frame = ttk.LabelFrame(
            scroll_frame, text="Agent Settings", padding=10
        )
        workspace_frame.pack(fill=tk.X, pady=10, padx=5)

        self._create_input(
            workspace_frame,
            "Claude Workspace",
            "CLAUDE_WORKSPACE",
            "Directory where the agent operates (e.g., ./agent_workspace)",
        )

        self._create_input(
            workspace_frame,
            "Allowed Directory",
            "ALLOWED_DIR",
            "Restrict CLI file access to this directory (optional)",
        )

        # Help text
        help_frame = ttk.LabelFrame(scroll_frame, text="Setup Instructions", padding=10)
        help_frame.pack(fill=tk.X, pady=20, padx=5)

        help_text = """Discord:
1. Go to Discord Developer Portal (discord.com/developers/applications)
2. Create a new application and add a Bot
3. Copy the Bot Token and paste it above
4. Enable Message Content Intent under Bot settings
5. Invite the bot with OAuth2 URL (scope: bot, permissions: Send Messages)

Telegram:
1. Message @BotFather on Telegram
2. Send /newbot and follow prompts
3. Copy the token provided and paste it above
4. Message @userinfobot to get your User ID"""

        ttk.Label(help_frame, text=help_text, justify=tk.LEFT).pack(anchor=tk.W)

    def refresh(self) -> None:
        """Refresh controls with current config values."""
        for key, control in self._controls.items():
            if isinstance(control, ttk.Entry):
                control.delete(0, tk.END)
                control.insert(0, self.config.get(key, ""))
            elif isinstance(control, ttk.Combobox):
                control.set(self.config.get(key, ""))
