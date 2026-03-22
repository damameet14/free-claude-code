# Free Claude Code - Desktop GUI Fork

This is a fork of the original [Free Claude Code](https://github.com/Alishahryar1/free-claude-code) project that adds a modern desktop GUI for easy configuration and server management.

## Fork Changes

### New Feature: Desktop GUI

A beautiful **CustomTkinter**-based desktop application that eliminates the need to manually edit `.env` files or use the command line.

#### What's Added

- **🖥️ Desktop Application** (`desktop/`)
  - Modern Material Design UI with dark/light theme support
  - 4 configuration tabs: Providers, Models, Messaging, Server
  - Start/stop the server directly from the GUI
  - Live server logs with timestamps
  - Save configuration to `~/.config/free-claude-code/.env`

- **🔑 Providers Tab**
  - Configure NVIDIA NIM, OpenRouter API keys
  - Set LM Studio and llama.cpp base URLs
  - Test connection buttons for validation

- **🤖 Models Tab**
  - Map OPUS, SONNET, and HAIKU to provider models
  - Quick-select popular models
  - Visual provider dropdowns

- **💬 Messaging Tab**
  - Configure Discord bot (token, allowed channels)
  - Configure Telegram bot (token, user ID)
  - Set agent workspace and allowed directories

- **🖥️ Server Tab**
  - Start/Stop server with visual status indicators
  - Port and host configuration
  - Connection info display
  - Live log viewer

#### How to Run the GUI

```bash
# Install with desktop dependencies
uv pip install -e ".[desktop]"

# Run the GUI
uv run python -m desktop.app
# or
uv run fcc-gui
```

#### Building Executable

```bash
# Build for current platform
uv run python build/build.py

# Output locations:
# Windows: dist/Free-Claude-Code.exe
# macOS: dist/Free-Claude-Code.app
# Linux: dist/free-claude-code
```

### Technical Changes

- **Added `desktop/` module**: Complete GUI implementation with 4 page classes
- **Updated `config/settings.py`**: Added `save_to_file()` method for persistence
- **Updated `pyproject.toml`**: Added `customtkinter` dependency and `fcc-gui` entry point
- **Added `build/`**: PyInstaller build scripts for cross-platform executables

## Original Project

This fork maintains full compatibility with the upstream project. All original features work identically:

- NVIDIA NIM, OpenRouter, LM Studio, llama.cpp providers
- Discord/Telegram bot functionality
- Request optimization
- Rate limiting
- Message threading

See [README.md](README.md) for full documentation on the original features.

## Contributing

This fork welcomes contributions to the desktop GUI. Please open issues or PRs specific to the GUI functionality.

For upstream features (providers, bot functionality), please contribute to the [original repository](https://github.com/Alishahryar1/free-claude-code).

## License

Same MIT License as the original project.
