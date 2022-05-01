"""Managed Theme class for use with ThemeManager; subclass of rich.theme.Theme"""

import configparser
from io import StringIO
from os.path import exists
from typing import IO, Dict, List, Mapping, Optional, Any

import rich.theme
from rich.color import Color
from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.style import Style, StyleType
from rich.table import Table, box
from rich.text import Text

SAMPLE_TEXT = "The quick brown fox..."


class Theme(rich.theme.Theme):
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        styles: Optional[Mapping[str, StyleType]] = None,
        inherit: bool = True,
        tags: Optional[List[str]] = None,
        path: Optional[str] = None,
    ):
        """Create a Theme instance

        Args:
            name (str): Name of the theme
            description (Optional[str]): Description of the theme
            styles (Optional[Mapping[str, StyleType]]): Styles to use in the theme
            inherit (bool): Whether or not to inherit from the default theme
            tags (Optional[List[str]]): Tags to use for filtering themes
            path (Optional[str]): Path to save the theme to
        """
        self._rtm_name: str = name
        self._rtm_description: str = description or ""
        self._rtm_styles: List[str] = list(styles.keys() if styles else [])
        self._rtm_inherit: bool = inherit
        self._rtm_tags: List[str] = tags or []
        self._rtm_path: Optional[str] = path
        super().__init__(styles=styles, inherit=inherit)

    @property
    def name(self) -> str:
        return self._rtm_name

    @property
    def description(self) -> str:
        return self._rtm_description

    @property
    def tags(self) -> List[str]:
        return self._rtm_tags

    @property
    def inherit(self) -> bool:
        return self._rtm_inherit

    @property
    def style_names(self) -> List[str]:
        return self._rtm_styles

    @property
    def path(self) -> Optional[str]:
        return self._rtm_path

    @path.setter
    def path(self, path: str):
        self._rtm_path = path

    @property
    def config(self) -> str:
        """Get contents of a config file for this theme."""
        metadata: Dict = {
            "name": self.name,
            "description": self.description,
            "tags": ", ".join(self.tags) if self.tags else "",
            "inherit": self.inherit,
        }
        config = configparser.ConfigParser()
        config.add_section("metadata")
        for key, value in metadata.items():
            config.set("metadata", key, str(value))
        strio = StringIO()
        config.write(strio)

        styles: str = "[styles]\n" + "\n".join(
            f"{name} = {style}"
            for name, style in sorted(self.styles.items())
            if name in self.style_names
        )

        return strio.getvalue() + styles + "\n"

    def to_file(self, path: str) -> None:
        """Write this theme to a config file."""
        with open(path, "w") as f:
            f.write(self.config)

    def save(self, overwrite=False) -> None:
        """Save this theme to its path."""
        if not self.path:
            raise ValueError(f"No path for theme {self.name}")
        if not overwrite and exists(self.path):
            raise FileExistsError(f"Theme {self.name} already exists at {self.path}")
        self.to_file(self.path)

    def load(self) -> None:
        """Load this theme from its path overwriting any theme data in memory."""
        if not self.path:
            raise FileNotFoundError(f"No path for theme {self.name}")
        if not exists(self.path):
            raise FileNotFoundError(f"Theme {self.name} does not exist at {self.path}")
        new_theme = Theme.read(self.path)
        self._rtm_name = new_theme.name
        self._rtm_description = new_theme.description
        self._rtm_styles = new_theme.style_names.copy()
        self._rtm_inherit = new_theme.inherit
        self._rtm_tags = new_theme.tags.copy()
        self._rtm_path = new_theme.path

    def update(self, other: "Theme", overwrite_existing_styles: bool = True) -> None:
        """Update self with data from another theme; updates only the styles, tags, and description.

        Args:
            other (Theme): Theme to update from
            overwrite_existing_styles (bool): Whether or not to overwrite styles that already exist in self

        Returns:
            None
        """
        for style in other._rtm_styles:
            if overwrite_existing_styles or style not in self._rtm_styles:
                self.styles[style] = other.styles[style]
        self._rtm_tags = list_union(self._rtm_tags, other._rtm_tags)
        self._rtm_styles = list_union(self._rtm_styles, other._rtm_styles)
        self._rtm_description = other._rtm_description

    def _preview(
        self, sample_text: Optional[str] = None, show_path: bool = True
    ) -> RenderResult:
        """Preview a theme for printing to console"""
        title: str = f"Theme: {self.name}"
        if show_path and self.path:
            title += f" - {self.path}"

        table = Table(
            title=title,
            title_justify="center",
            show_header=True,
            show_lines=True,
            header_style="bold",
            box=box.SQUARE,
        )

        sample_text = sample_text or SAMPLE_TEXT

        for column in [
            "style",
            "color",
            "color",
            "bgcolor",
            "bgcolor",
            "attributes",
            "example",
        ]:
            table.add_column(column)

        for style_name in self.style_names:
            style = self.styles.get(style_name)
            if not style:
                continue
            color = (style.color.name or style.color.rgb) if style.color else "None"
            bgcolor = (
                (style.bgcolor.name or style.bgcolor.rgb) if style.bgcolor else "None"
            )

            attributes = attribute_str(style)

            table.add_row(
                style_name,
                str(color),
                color_bar(5, style.color) if style.color else " " * 5,
                str(bgcolor),
                color_bar(5, style.bgcolor) if style.bgcolor else " " * 5,
                attributes,
                Text(sample_text, style=style),
            )

        yield table

        legend_table = Table(
            show_header=False,
            show_lines=False,
            box=None,
        )
        legend_table.add_row(
            (
                f"{_bold('b')}: bold, "
                f"{_bold('d')}: dim, "
                f"{_bold('i')}: italic, "
                f"{_bold('u')}: underline, "
                f"{_bold('U')}: double underline, "
                f"{_bold('B')}: blink, "
                f"{_bold('2')}: blink2"
            )
        )
        legend_table.add_row(
            (
                f"{_bold('r')}: reverse, "
                f"{_bold('c')}: conceal, "
                f"{_bold('s')}: strike, "
                f"{_bold('f')}: frame, "
                f"{_bold('e')}: encircle, "
                f"{_bold('o')}: overline, "
                f"{_bold('L')}: Link"
            )
        )

        yield Panel(
            legend_table,
            box=box.SQUARE,
            title="attributes legend",
            title_align="left",
            expand=False,
        )

    def __eq__(self, other: object) -> bool:
        return (
            (
                self.name == other.name
                and self.description == other.description
                and self.styles == other.styles
                and self.inherit == other.inherit
                and self.tags == other.tags
            )
            if isinstance(other, Theme)
            else NotImplemented
        )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from self._preview()

    def __or__(self, other: object) -> "Theme":
        """Combine two themes into a new theme via union; updates only the styles, tags, and description."""
        if not isinstance(other, Theme):
            return NotImplemented
        new_styles = {style: self.styles[style] for style in self._rtm_styles}
        for style in other._rtm_styles:
            new_styles[style] = other.styles[style]
        new_tags = list_union(self.tags, other.tags)
        return Theme(
            name=self.name,
            description=other.description,
            styles=new_styles,
            inherit=self.inherit,
            tags=new_tags,
            path=self.path,
        )

    def __ior__(self, other: object) -> "Theme":
        """Combine two themes into a new theme via union; updates only the styles and tags, not other theme data."""
        if not isinstance(other, Theme):
            return NotImplemented
        self.update(other)
        return self

    @classmethod
    def from_file(
        cls, config_file: IO[str], source: Optional[str] = None, inherit: bool = True
    ) -> "Theme":
        """Load a theme from a text mode file.
        Args:
            config_file (IO[str]): An open conf file.
            source (str, optional): The filename of the open file. Defaults to None.
            inherit (bool, optional): Inherit default styles. Defaults to True.
        Returns:
            Theme: A New theme instance.
        """
        config = configparser.ConfigParser()
        config.read_file(config_file, source=source)
        styles: Dict = {
            name: Style.parse(value) for name, value in config.items("styles")
        }
        metadata: Dict = dict(config.items("metadata"))
        inherit = inherit or metadata.get("inherit", False)
        tags: List[str] = (
            metadata.get("tags", "").split(",") if metadata.get("tags") else []
        )
        tags = [tag.strip() for tag in tags]
        return Theme(
            name=metadata["name"],
            description=metadata.get("description") or "",
            tags=tags,
            styles=styles,
            inherit=inherit,
            path=source,
        )

    @classmethod
    def read(cls, path: str, inherit: bool = True) -> "Theme":
        """Read a theme from a path.
        Args:
            path (str): Path to a config file readable by Python configparser module.
            inherit (bool, optional): Inherit default styles. Defaults to True.
        Returns:
            Theme: A new theme instance.
        """
        with open(path, "rt") as config_file:
            return cls.from_file(config_file, source=path, inherit=inherit)


def _bold(text: str) -> str:
    return f"[bold]{text}[/]"


def attribute_str(style: Style) -> str:
    """Return a string representing all attributes of a style"""
    attributes = "" + (_bold("b") if style.bold else "-")
    attributes += _bold("d") if style.dim else "-"
    attributes += _bold("i") if style.italic else "-"
    attributes += _bold("u") if style.underline else "-"
    attributes += _bold("U") if style.underline2 else "-"
    attributes += _bold("B") if style.blink else "-"
    attributes += _bold("2") if style.blink2 else "-"
    attributes += _bold("r") if style.reverse else "-"
    attributes += _bold("c") if style.conceal else "-"
    attributes += _bold("s") if style.strike else "-"
    attributes += _bold("f") if style.frame else "-"
    attributes += _bold("e") if style.encircle else "-"
    attributes += _bold("o") if style.overline else "-"
    attributes += _bold("L") if style.link else "-"
    return attributes


def color_bar(length: int, color: Color) -> str:
    """Create a color bar."""
    bar = "█" * length
    return Text(bar, style=Style(color=color))


def list_union(a: List[Any], b: List[Any]) -> List[Any]:
    """Return union of two lists maintaining order of the first list."""
    return a + [x for x in b if x not in a]
