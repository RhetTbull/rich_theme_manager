"""Theme Manager for rich Themes"""
import importlib.metadata

from .manager import ThemeManager
from .theme import Theme

__version__ = importlib.metadata.version("rich_theme_manager")

__all__ = ["Theme", "ThemeManager"]
