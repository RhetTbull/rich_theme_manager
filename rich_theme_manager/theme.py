"""Managed Theme class for use with ThemeManager; subclass of rich.theme.Theme"""

import configparser
from io import StringIO
from os.path import exists
from typing import IO, Dict, List, Mapping, Optional, cast

import rich.theme
from rich.style import Style, StyleType


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

    def load(self) -> "Theme":
        """Load this theme from its path returning a new Theme object."""
        if not self.path:
            raise ValueError(f"No path for theme {self.name}")
        return self.read(self.path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Theme):
            return NotImplemented
        return (
            self.name == other.name
            and self.description == other.description
            and self.styles == other.styles
            and self.inherit == other.inherit
            and self.tags == other.tags
        )

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
