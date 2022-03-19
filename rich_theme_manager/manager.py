"""Manage rich themes: implements ThemeManager class"""


import pathlib
from os import unlink
from os.path import exists
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

from .theme import Theme

SAMPLE_TEXT = "The quick brown fox..."


class ThemeManager:
    """Manage rich themes"""

    def __init__(
        self,
        theme_dir: Optional[str] = None,
        themes: Optional[List[Theme]] = None,
    ):
        self._theme_dir: Optional[pathlib.Path] = (
            pathlib.Path(theme_dir) if theme_dir else None
        )
        self._themes: Dict[str, Theme] = (
            {theme.name: theme for theme in themes} if themes else {}
        )

        if self._theme_dir is not None:
            for theme in self.themes:
                theme.path = str(self._theme_dir / f"{theme.name}.theme")
            self.load_themes()
            self.write_themes()

    @property
    def themes(self) -> List[Theme]:
        """Themes"""
        return list(self._themes.values())

    def add(self, theme: Theme, overwrite=False) -> None:
        """Add theme; if theme file doesn't exist, it will be written"""
        if self._theme_dir and not theme.path:
            theme.path = str(self._theme_dir / f"{theme.name}.theme")
        if self._theme_dir and overwrite or (theme.path and not exists(theme.path)):
            theme.save(overwrite=overwrite)
        self._themes[theme.name] = theme

    def remove(self, theme: Theme) -> None:
        """Remove theme; if theme file exists, it will be deleted"""
        if theme.path and exists(theme.path):
            unlink(theme.path)
        del self._themes[theme.name]

    def get(self, theme_name: str) -> Theme:
        """Get theme by name"""
        for theme in self.themes:
            if theme.name == theme_name:
                return theme
        raise ValueError(f"Theme {theme_name} not found")

    def load_themes(self, theme_dir: Optional[str] = None) -> None:
        """Load themes"""
        if theme_dir:
            # load themes from user specified theme directory instead of self._theme_dir
            _theme_dir = pathlib.Path(theme_dir)
            for path in _theme_dir.glob("*.theme"):
                theme = Theme.read(str(path))
                self._themes[theme.name] = theme
        elif self._theme_dir:
            for path in self._theme_dir.glob("*.theme"):
                theme = Theme.read(str(path))
                self._themes[theme.name] = theme
        else:
            raise ValueError("No theme directory specified")

    def write_themes(self, overwrite: bool = False) -> None:
        """Write themes"""
        for theme in self.themes:
            if not theme.path:
                raise ValueError(f"Theme {theme.name} has no path")
            if not exists(theme.path) or overwrite:
                theme.save(overwrite=overwrite)

    def list_themes(
        self, show_path: bool = True, theme_names: Optional[List[str]] = None
    ) -> None:
        """List themes"""
        table = Table(show_header=True, show_lines=False, box=None)
        table.add_column("Theme")
        table.add_column("Description")
        table.add_column("Tags")
        if show_path:
            table.add_column("Path")
        for theme in self.themes:
            if theme_names and theme.name not in theme_names:
                continue
            row = [
                theme.name,
                theme.description,
                str(", ".join(theme.tags)),
            ]
            if show_path:
                row.append(theme.path or "")
            table.add_row(*row)
        console = Console()
        console.print(table)

    @classmethod
    def preview_theme(
        self, theme: Theme, sample_text: Optional[str] = None, show_path: bool = True
    ) -> None:
        """Preview a theme to the console"""
        Console().print(
            *list(
                theme._preview(
                    sample_text=sample_text or SAMPLE_TEXT, show_path=show_path
                )
            )
        )
