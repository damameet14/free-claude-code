# Changelog

All notable changes to this fork will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Desktop GUI application using CustomTkinter
  - Modern Material Design interface
  - Dark/Light theme toggle
  - Four configuration pages: Providers, Models, Messaging, Server
  - Live server log viewer
  - Visual server start/stop controls
  - Configuration persistence to ~/.config/free-claude-code/.env

- New CLI entry point: `fcc-gui` for launching the desktop application

- Build scripts for creating standalone executables
  - Windows: `Free-Claude-Code.exe`
  - macOS: `Free-Claude-Code.app`
  - Linux: `free-claude-code` binary

### Changed

- Migrated from tkinter to CustomTkinter for modern UI
- Updated Settings class with `save_to_file()` method
- Added desktop dependencies to pyproject.toml
- Improved .gitignore for better cleanup

## [Original Project]

See the [upstream repository](https://github.com/Alishahryar1/free-claude-code) for the full history of the original project.
