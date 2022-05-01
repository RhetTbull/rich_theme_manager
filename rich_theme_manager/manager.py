"""Manage rich themes: implements ThemeManager class"""


import pathlib
from os import unlink
from os.path import exists
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

from .theme import SAMPLE_TEXT, Theme


class ThemeManager:
    """Manage rich themes"""

    def __init__(
        self,
        theme_dir: Optional[str] = None,
        themes: Optional[List[Theme]] = None,
        overwrite: bool = False,
        update: bool = False,
    ):
        """Create ThemeManager instance

        Args:
            theme_dir (Optional[str]): directory containing themes
            themes (Optional[List[Theme]]): list of rich_theme_manager.Theme objects
            overwrite (bool): overwrite existing theme files
            update (bool): update existing theme files with new styles from themes but don't replace existing styles
        """
        self._theme_dir: Optional[pathlib.Path] = (
            pathlib.Path(theme_dir) if theme_dir else None
        )
        self._themes: Dict[str, Theme] = (
            {theme.name: theme for theme in themes} if themes else {}
        )

        if self._theme_dir is not None:
            for theme in self.themes:
                theme.path = str(self._theme_dir / f"{theme.name}.theme")

            # if overwrite, need to write themes first to overwrite existing themes
            # then load themes because there may be theme files not in self._themes
            # if not overwrite, themes will be loaded from self._theme_dir then written in case
            # there are themes in self._themes that are not in self._theme_dir
            if overwrite:
                self.write_themes(overwrite=overwrite)
                self.load_themes(update=update)
            else:
                self.load_themes(update=update)
                self.write_themes(overwrite=update)

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

    def load_themes(
        self, theme_dir: Optional[str] = None, update: bool = False
    ) -> None:
        """Load themes"""
        theme_dir = theme_dir or self._theme_dir
        if theme_dir is None:
            raise ValueError("No theme directory")

        theme_dir = pathlib.Path(theme_dir)
        for path in theme_dir.glob("*.theme"):
            theme = Theme.read(str(path))
            if update and theme.name in self._themes:
                theme.update(self._themes[theme.name], overwrite_existing_styles=False)
            self._themes[theme.name] = theme

    def write_themes(self, overwrite: bool = False) -> None:
        """Write themes"""
        for theme in self.themes:
            if not theme.path:
                raise ValueError(f"Theme {theme.name} has no path")
            if not exists(theme.path) or overwrite:
                theme.save(overwrite=overwrite)

    def list_themes(
        self,
        show_path: bool = True,
        theme_names: Optional[List[str]] = None,
        console: Optional[Console] = None,
    ) -> None:
        """List themes

        Args:
            show_path (bool): show theme file path
            theme_names (Optional[List[str]]): list of theme names to show (default is all themes)
            console: Optional[Console]: rich.console.Console instance to use for printing
        """
        table = Table(show_header=True, show_lines=False, box=None)
        table.add_column("Theme")
        table.add_column("Description")
        table.add_column("Tags")
        if show_path:
            table.add_column("Path")
        for theme in self.themes:
            if theme_names and theme.name not in theme_names:
                continue
            row = [theme.name, theme.description, ", ".join(theme.tags)]
            if show_path:
                row.append(theme.path or "")
            table.add_row(*row)
        console = console or Console()
        console.print(table)

    @classmethod
    def preview_theme(
        cls,
        theme: Theme,
        sample_text: Optional[str] = None,
        show_path: bool = True,
        console: Optional[Console] = None,
    ) -> None:
        """Preview a theme to the console

        Args:
            theme (Theme): theme to preview
            sample_text (Optional[str]): sample text to use for preview (default is rich_theme_manager.theme.SAMPLE_TEXT)
            show_path (bool): show theme file path
            console: Optional[Console]: rich.console.Console instance to use for printing
        """
        console = console or Console()
        console.print(
            *list(
                theme._preview(
                    sample_text=sample_text or SAMPLE_TEXT, show_path=show_path
                )
            )
        )
