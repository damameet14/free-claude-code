"""Build script for creating Free Claude Code executables."""

import argparse
import platform
import subprocess
import sys
from pathlib import Path


def get_platform_name() -> str:
    """Get the current platform name."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def build_windows() -> None:
    """Build Windows executable."""
    print("Building Windows executable...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--name=Free-Claude-Code",
            "--windowed",  # No console
            "--onedir",  # Folder-based (works better for web apps)
            "--add-data=desktop:desktop",
            "--hidden-import=uvicorn",
            "--hidden-import=fastapi",
            "--hidden-import=pydantic",
            "--hidden-import=flet",
            "desktop/app.py",
        ],
        cwd=Path.cwd(),
        check=True,
    )
    print("\nBuilt: dist/Free-Claude-Code/Free-Claude-Code.exe")


def build_macos() -> None:
    """Build macOS .app bundle."""
    print("Building macOS app bundle...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--name=Free-Claude-Code",
            "--windowed",  # .app bundle
            "--onedir",
            "--add-data=desktop:desktop",
            "--hidden-import=uvicorn",
            "--hidden-import=fastapi",
            "--hidden-import=pydantic",
            "--hidden-import=flet",
            "desktop/app.py",
        ],
        cwd=Path.cwd(),
        check=True,
    )
    print("\nBuilt: dist/Free-Claude-Code.app")


def build_linux() -> None:
    """Build Linux executable."""
    print("Building Linux executable...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--name=free-claude-code",
            "--onefile",  # Single file on Linux
            "--add-data=desktop:desktop",
            "--hidden-import=uvicorn",
            "--hidden-import=fastapi",
            "--hidden-import=pydantic",
            "--hidden-import=flet",
            "desktop/app.py",
        ],
        cwd=Path.cwd(),
        check=True,
    )
    print("\nBuilt: dist/free-claude-code")


def install_deps() -> None:
    """Install desktop dependencies."""
    print("Installing desktop dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".[desktop]"],
        cwd=Path.cwd(),
        check=True,
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build Free Claude Code executable")
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux", "auto"],
        default="auto",
        help="Target platform (default: auto-detect)",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies first",
    )

    args = parser.parse_args()

    if args.install:
        install_deps()

    if args.platform == "auto":
        platform_name = get_platform_name()
    else:
        platform_name = args.platform

    build_funcs = {
        "windows": build_windows,
        "macos": build_macos,
        "linux": build_linux,
    }

    if platform_name not in build_funcs:
        print(f"Unsupported platform: {platform_name}")
        return 1

    try:
        build_funcs[platform_name]()
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
