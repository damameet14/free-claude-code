"""Messaging platform configuration page for desktop UI."""

from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


class MessagingConfigPage:
    """Page for configuring Discord and Telegram bot settings."""

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
            text="Messaging Platform",
            font=("Inter", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Configure Discord or Telegram bot for remote Claude Code control",
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

    def _create_input(
        self,
        parent: ctk.CTkFrame,
        label: str,
        key: str,
        hint: str | None = None,
        password: bool = False,
    ) -> ctk.CTkEntry:
        """Create a text input field."""
        value = self.config.get(key, "")

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)

        ctk.CTkLabel(frame, text=label, font=("Inter", 13, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        entry = ctk.CTkEntry(
            frame,
            show="●" if password else "",
            font=("Inter", 12),
            height=35,
            corner_radius=8,
        )
        entry.insert(0, value)
        entry.pack(fill="x")

        if hint:
            ctk.CTkLabel(frame, text=hint, font=("Inter", 10), text_color="gray").pack(
                anchor="w", pady=(3, 0)
            )

        def on_change(event=None):
            self.on_config_change(key, entry.get())

        entry.bind("<FocusOut>", on_change)
        entry.bind("<Return>", on_change)

        self._controls[key] = entry
        return entry

    def _create_dropdown(
        self,
        parent: ctk.CTkFrame,
        label: str,
        key: str,
        options: list[str],
    ) -> ctk.CTkOptionMenu:
        """Create a dropdown field."""
        value = self.config.get(key, options[0] if options else "")

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)

        ctk.CTkLabel(frame, text=label, font=("Inter", 13, "bold")).pack(
            anchor="w", pady=(0, 5)
        )

        dropdown = ctk.CTkOptionMenu(
            frame,
            values=options,
            font=("Inter", 12),
            height=35,
            corner_radius=8,
            command=lambda choice: self.on_config_change(key, choice),
        )
        dropdown.set(value)
        dropdown.pack(fill="x")

        self._controls[key] = dropdown
        return dropdown

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
        # Platform Selection Card
        platform_card = self._create_card("Platform Selection")

        content = ctk.CTkFrame(platform_card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            content,
            text="Choose your messaging platform",
            font=("Inter", 11),
            text_color="gray",
        ).pack(anchor="w", pady=(0, 10))

        self._create_dropdown(
            content,
            "Messaging Platform",
            "MESSAGING_PLATFORM",
            ["discord", "telegram"],
        )

        # Discord Card
        discord_card = self._create_card("💬 Discord Configuration")

        discord_content = ctk.CTkFrame(discord_card, fg_color="transparent")
        discord_content.pack(fill="x", padx=15, pady=(0, 15))

        self._create_input(
            discord_content,
            "Discord Bot Token",
            "DISCORD_BOT_TOKEN",
            "Get from Discord Developer Portal",
            password=True,
        )

        self._create_input(
            discord_content,
            "Allowed Discord Channels",
            "ALLOWED_DISCORD_CHANNELS",
            "Comma-separated channel IDs (e.g., 123456789,987654321)",
        )

        # Telegram Card
        telegram_card = self._create_card("✈️ Telegram Configuration")

        telegram_content = ctk.CTkFrame(telegram_card, fg_color="transparent")
        telegram_content.pack(fill="x", padx=15, pady=(0, 15))

        self._create_input(
            telegram_content,
            "Telegram Bot Token",
            "TELEGRAM_BOT_TOKEN",
            "Get from @BotFather",
            password=True,
        )

        self._create_input(
            telegram_content,
            "Allowed Telegram User ID",
            "ALLOWED_TELEGRAM_USER_ID",
            "Your Telegram user ID (from @userinfobot)",
        )

        # Agent Settings Card
        agent_card = self._create_card("🤖 Agent Settings")

        agent_content = ctk.CTkFrame(agent_card, fg_color="transparent")
        agent_content.pack(fill="x", padx=15, pady=(0, 15))

        self._create_input(
            agent_content,
            "Claude Workspace",
            "CLAUDE_WORKSPACE",
            "Directory where the agent operates (e.g., ./agent_workspace)",
        )

        self._create_input(
            agent_content,
            "Allowed Directory",
            "ALLOWED_DIR",
            "Restrict CLI file access to this directory (optional)",
        )

        # Help Card
        help_card = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=12,
            fg_color=["gray90", "gray20"],
        )
        help_card.pack(fill="x", pady=15, padx=5)

        ctk.CTkLabel(
            help_card,
            text="📖 Setup Instructions",
            font=("Inter", 16, "bold"),
        ).pack(anchor="w", pady=(15, 10), padx=15)

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

        ctk.CTkLabel(
            help_card,
            text=help_text,
            font=("Inter", 11),
            justify="left",
        ).pack(anchor="w", pady=(0, 15), padx=15)

    def refresh(self) -> None:
        """Refresh controls with current config values."""
        for key, control in self._controls.items():
            if isinstance(control, ctk.CTkEntry):
                control.delete(0, "end")
                control.insert(0, self.config.get(key, ""))
            elif isinstance(control, ctk.CTkOptionMenu):
                control.set(self.config.get(key, ""))
