# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Free Claude Code desktop app."""

import sys
from pathlib import Path

block_cipher = None

# Project root
project_root = Path.cwd()

# Files to include
added_files = [
    # Flet assets
    ("desktop", "desktop"),
]

# Hidden imports required for FastAPI and providers
hidden_imports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "fastapi",
    "fastapi.dependencies",
    "fastapi.concurrency",
    "starlette",
    "pydantic",
    "pydantic._internal",
    "pydantic.fields",
    "pydantic.Json",
    "pydantic_settings",
    "dotenv",
    "tiktoken",
    "tiktoken_ext.openai_public",
    "loguru",
    "httpx",
    "email_validator",
    "openai",
    # Provider modules
    "providers.base",
    "providers.openai_compat",
    "providers.nvidia_nim.client",
    "providers.open_router.client",
    "providers.lmstudio.client",
    "providers.llamacpp.client",
    "providers.common.sse_builder",
    "providers.common.message_converter",
    "providers.common.think_parser",
    "providers.common.heuristic_tool_parser",
    "providers.common.error_mapping",
    "providers.common.text",
    "providers.common.utils",
    # API modules
    "api.app",
    "api.routes",
    "api.dependencies",
    "api.models",
    "api.models.anthropic",
    "api.models.responses",
    "api.detection",
    "api.optimization_handlers",
    "api.request_utils",
    # Config modules
    "config.settings",
    "config.nim",
    "config.logging_config",
    # CLI modules
    "cli.entrypoints",
    "cli.manager",
    "cli.process_registry",
    "cli.session",
    # Messaging modules
    "messaging.platforms.base",
    "messaging.platforms.factory",
    "messaging.platforms.discord",
    "messaging.platforms.telegram",
    "messaging.handler",
    "messaging.events",
    "messaging.models",
    "messaging.session",
    "messaging.trees",
    # Desktop modules
    "desktop.app",
    "desktop.pages.provider_config",
    "desktop.pages.model_mapping",
    "desktop.pages.server_control",
    "desktop.utils",
    # Flet dependencies
    "flet",
    "flet.core",
]

a = Analysis(
    ["desktop/app.py"],  # Entry point
    pathex=[str(project_root)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "_pytest",
        "pytest",
        "py",
        "unittest",
        "pydoc",
        "pdb",
        "doctest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Free-Claude-Code",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icon.ico" if Path("icon.ico").exists() else None,
)

# macOS .app bundle (only included when building on macOS)
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="Free Claude Code.app",
        icon="icon.icns" if Path("icon.icns").exists() else None,
        bundle_identifier="com.fcc.desktop",
        info_plist={
            "CFBundleShortVersionString": "2.0.0",
            "CFBundleVersion": "2.0.0",
            "NSHighResolutionCapable": True,
        },
    )
