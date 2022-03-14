"""Tests for rich_theme_manager"""

import configparser
import os
import tempfile
from textwrap import dedent

import pytest
from rich.style import Style
from rich_theme_manager import Theme, ThemeManager


def test_theme_manager_basic(themes):
    """Basic test of ThemeManager"""

    tm = ThemeManager(themes=themes)
    dark = tm.get("dark")
    assert isinstance(dark, Theme)
    assert dark.name == "dark"


def test_theme_manager_add_remove(themes):
    """Test adding a theme"""

    tm = ThemeManager(themes=themes)
    tm.add(
        Theme(
            name="test", description="Test theme", styles={"test": Style(color="red")}
        )
    )
    test = tm.get("test")
    assert isinstance(test, Theme)
    assert test.name == "test"

    tm.remove(test)
    with pytest.raises(ValueError):
        tm.get("test")


def test_theme_manager_init(themes):
    """Test that ThemeManager creates theme files on init"""

    theme_dir = tempfile.TemporaryDirectory()
    tm = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    for theme in tm.themes:
        assert os.path.exists(theme.path)

    # change file and make sure it doesn't get overwritten on init
    dark = tm.get("dark")
    with open(dark.path, "at") as f:
        f.write("\n[test]\nfoo = bar\n")
    tm2 = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    dark2 = tm2.get("dark")
    parser = configparser.ConfigParser()
    parser.read(dark2.path)
    assert parser["test"]["foo"] == "bar"


def test_theme_manager_write_themes(themes):
    """Test that ThemeManager.write_themes"""

    theme_dir = tempfile.TemporaryDirectory()
    tm = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    for theme in tm.themes:
        assert os.path.exists(theme.path)

    # change the theme and make sure the file is updated
    tm.add(
        Theme(
            name="dark",
            description="Dark is the new black",
            styles={"test": Style(color="red")},
        )
    )
    tm.write_themes()
    tm2 = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    dark2 = tm2.get("dark")
    assert dark2.description != "Dark is the new black"

    # now with overwrite
    tm.write_themes(overwrite=True)
    tm3 = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    dark3 = tm3.get("dark")
    assert dark3.description == "Dark is the new black"


def test_theme_config(themes):
    """Test Theme.config"""

    config_data = dedent(
        """
        [metadata]
        name = dark
        description = Dark mode theme
        tags = dark
        inherit = True

        [styles]
        error = bold rgb(255,85,85)
        filename = bold rgb(189,147,249)
        filepath = bold rgb(80,250,123)
        hidden = dim #383b3d
        highlight = bold #000000 on #d73a49
        num = bold rgb(139,233,253)
        time = bold rgb(139,233,253)
        warning = bold rgb(241,250,140)
    """
    )

    tm = ThemeManager(themes=themes)
    dark = tm.get("dark")
    expected_config = configparser.ConfigParser()
    expected_config.read_string(config_data)
    got_config = configparser.ConfigParser()
    got_config.read_string(dark.config)
    for key in ["name", "description", "tags", "inherit"]:
        assert got_config["metadata"][key] == expected_config["metadata"][key]
    for key in [
        "error",
        "filename",
        "filepath",
        "hidden",
        "highlight",
        "num",
        "time",
        "warning",
    ]:
        assert got_config["styles"][key] == expected_config["styles"][key]
