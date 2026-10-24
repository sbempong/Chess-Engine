"""
Chess Engine UI Package

- UI.cli: command-line interface (no extra dependencies)
- UI.gui: Tkinter GUI (requires a Python build with tkinter)
- UI/chesswebapp: Flask web interface, served by app.py at the repo root
"""

from .cli import ChessCLI

try:
    from .gui import ChessGUI
except ImportError:  # tkinter not available in this Python build
    ChessGUI = None

__all__ = ['ChessCLI', 'ChessGUI']
