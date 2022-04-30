"""Tests for rich_theme_manager"""
import configparser
import os
import sys
import tempfile
from io import StringIO
from textwrap import dedent

import pytest
from rich.console import Console
from rich.style import Style
from rich.theme import Theme as RichTheme

from rich_theme_manager import Theme, ThemeManager
from rich_theme_manager.manager import SAMPLE_TEXT


def test_theme_manager_basic(themes):
    """Basic test of ThemeManager"""

    tm = ThemeManager(themes=themes)
    dark = tm.get("dark")
    assert isinstance(dark, Theme)
    assert dark.name == "dark"


def test_theme_manager_themes(themes):
    """Test ThemeManager.themes"""

    tm = ThemeManager(themes=themes)
    theme_names = [t.name for t in themes]
    assert len(tm.themes) == len(themes)
    for theme in tm.themes:
        assert theme.name in theme_names


def test_theme_manager_add_remove(themes):
    """Test adding/removing a theme"""

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


def test_theme_manager_add_remove_theme_dir(themes):
    """Test adding/removing a theme when theme_dir is set"""
    theme_dir = tempfile.TemporaryDirectory()
    tm = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    tm.add(
        Theme(
            name="test", description="Test theme", styles={"test": Style(color="red")}
        )
    )
    test = tm.get("test")
    theme_file = os.path.join(theme_dir.name, "test.theme")
    assert test.path == theme_file
    assert os.path.exists(theme_file)

    tm.remove(test)
    with pytest.raises(ValueError):
        tm.get("test")
    assert not os.path.exists(theme_file)


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

    # change the theme and make sure the file is not updated
    tm.add(
        Theme(
            name="dark",
            description="Dark is the new black",
            styles={"test": Style(color="red")},
        )
    )
    tm.add(
        Theme(
            name="test",
            description="Test theme",
            styles={"test": Style(color="blue")},
        )
    )
    tm.write_themes()

    tm2 = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    dark2 = tm2.get("dark")
    assert dark2.description != "Dark is the new black"
    test = tm2.get("test")
    assert test.description == "Test theme"

    # now with overwrite, file should be updated
    tm.write_themes(overwrite=True)
    tm3 = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    dark3 = tm3.get("dark")
    assert dark3.description == "Dark is the new black"


def test_theme_manager_write_themes_exception(themes):
    """Test that ThemeManager.write_themes raises exception if Theme.path not set"""

    theme_dir = tempfile.TemporaryDirectory()
    tm = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    for theme in tm.themes:
        assert os.path.exists(theme.path)

    # change the theme and make sure the file is not updated
    tm.add(
        Theme(
            name="dark",
            description="Dark is the new black",
            styles={"test": Style(color="red")},
        )
    )
    tm.add(
        Theme(
            name="test",
            description="Test theme",
            styles={"test": Style(color="blue")},
        )
    )
    tm._themes["test"].path = None

    with pytest.raises(ValueError):
        tm.write_themes()


def test_theme_manager_get(themes):
    """Test ThemeManager.get"""

    tm = ThemeManager(themes=themes)
    dark = tm.get("dark")
    assert isinstance(dark, Theme)
    assert dark.name == "dark"

    with pytest.raises(ValueError):
        tm.get("not_a_theme")


def test_theme_manager_load_themes_1(themes):
    """Test ThemeManager.load_themes with no theme_dir"""

    tm = ThemeManager()
    with pytest.raises(ValueError):
        tm.load_themes()

    theme_dir = tempfile.TemporaryDirectory()
    for theme in themes:
        config = theme.config
        name = theme.name
        path = os.path.join(theme_dir.name, f"{name}.theme")
        with open(path, "wt") as f:
            f.write(config)
    tm.load_themes(theme_dir.name)
    assert tm.get("dark") is not None


def test_theme_manager_load_themes_2(themes):
    """Test ThemeManager.load_themes with theme_dir set"""

    theme_dir = tempfile.TemporaryDirectory()
    for theme in themes:
        config = theme.config
        name = theme.name
        path = os.path.join(theme_dir.name, f"{name}.theme")
        with open(path, "wt") as f:
            f.write(config)
    tm = ThemeManager()
    with pytest.raises(ValueError):
        tm.get("dark")
    tm.load_themes(theme_dir.name)
    assert tm.get("dark") is not None


@pytest.mark.skipif(
    "-s" not in sys.argv,
    reason="capsys not compatible with rich.console.Console unless pytest run with -s, see https://github.com/Textualize/rich/issues/317",
)
def test_theme_manager_preview(themes, capsys):
    """Test ThemeManager.preview_theme"""
    tm = ThemeManager(themes=themes)
    theme = tm.get("dark")
    tm.preview_theme(theme)
    captured = capsys.readouterr()
    assert "Theme: dark" in captured.out
    assert SAMPLE_TEXT in captured.out

    tm.preview_theme(theme, sample_text="Join the dark side")
    captured = capsys.readouterr()
    assert "Theme: dark" in captured.out
    assert "Join the dark side" in captured.out


def test_theme_manager_preview_console(themes):
    """Test ThemeManager.preview_theme"""
    tm = ThemeManager(themes=themes)
    theme = tm.get("dark")
    strio = StringIO()
    console = Console(width=200, file=strio)
    tm.preview_theme(theme, console=console)
    captured = strio.getvalue()
    assert "Theme: dark" in captured
    assert SAMPLE_TEXT in captured

    strio = StringIO()
    console = Console(width=200, file=strio)
    tm.preview_theme(theme, sample_text="Join the dark side", console=console)
    captured = strio.getvalue()
    assert "Theme: dark" in captured
    assert "Join the dark side" in captured


@pytest.mark.skipif(
    "-s" not in sys.argv,
    reason="capsys not compatible with rich.console.Console unless pytest run with -s, see https://github.com/Textualize/rich/issues/317",
)
def test_theme_manager_preview_no_style(capsys):
    """Test ThemeManager.preview_theme works even if theme style not set"""

    tm = ThemeManager()
    tm.add(
        Theme(
            name="test",
            description="Test theme",
            styles={"test": Style(color="blue")},
        )
    )
    theme = tm.get("test")
    theme._rtm_styles = ["foo"]
    tm.preview_theme(theme, sample_text="Join the dark side")
    captured = capsys.readouterr()
    assert "Theme: test" in captured.out


@pytest.mark.skipif(
    "-s" not in sys.argv,
    reason="capsys not compatible with rich.console.Console unless pytest run with -s, see https://github.com/Textualize/rich/issues/317",
)
def test_theme_manager_list_themes(themes, capsys):
    """Test ThemeManager.list_themes"""
    tm = ThemeManager(themes=themes)
    tm.list_themes()
    captured = capsys.readouterr()
    assert "dark" in captured.out
    assert "light" in captured.out
    assert "Monochromatic theme" in captured.out

    tm.list_themes(theme_names=["foo"])
    captured = capsys.readouterr()
    assert "dark" not in captured.out


def test_theme_manager_list_themes_console(themes):
    """Test ThemeManager.list_themes with custom Console object"""
    tm = ThemeManager(themes=themes)
    from io import StringIO

    strio = StringIO()
    console = Console(width=100, file=strio)
    tm.list_themes(console=console)
    captured = strio.getvalue()
    assert "dark" in captured
    assert "light" in captured
    assert "Monochromatic theme" in captured

    strio = StringIO()
    console = Console(width=100, file=strio)
    tm.list_themes(theme_names=["foo"], console=console)
    captured = strio.getvalue()
    assert "dark" not in captured


def test_theme_properties():
    """Test basic theme properties"""
    theme_dir = tempfile.TemporaryDirectory()
    theme_path = os.path.join(theme_dir.name, "test.theme")
    theme = Theme(
        name="test",
        description="Test theme",
        tags=["test", "dark"],
        styles={"test": Style(color="red"), "warning": Style(color="yellow")},
        path=theme_path,
        inherit=True,
    )
    assert theme.name == "test"
    assert theme.description == "Test theme"
    assert sorted(theme.tags) == ["dark", "test"]
    assert theme.path == theme_path
    assert theme.inherit
    assert sorted(theme.style_names) == ["test", "warning"]

    theme.path = None
    tm = ThemeManager(theme_dir=theme_dir.name)
    tm.add(theme)
    assert theme.path == theme_path


def test_theme_save():
    """Test Theme.save"""

    theme_dir = tempfile.TemporaryDirectory()
    tm = ThemeManager(theme_dir=theme_dir.name)
    tm.add(
        Theme(
            name="test", description="Test theme", styles={"test": Style(color="red")}
        )
    )
    theme1 = tm.get("test")

    # directly manipulate the theme data then call save
    tm._themes["test"] = Theme(
        "test",
        description="New description",
        styles={"test": Style(color="blue")},
        path=theme1.path,
    )
    theme2 = tm.get("test")

    # should raise error if file exists (which it does)
    with pytest.raises(FileExistsError):
        theme2.save()
    theme2.save(overwrite=True)
    parser = configparser.ConfigParser()
    parser.read(theme2.path)
    assert parser["metadata"]["description"] == "New description"


def test_theme_save_no_path():
    """Test Theme.save when there's no path (raises exception)"""

    tm = ThemeManager()
    tm.add(
        Theme(
            name="test", description="Test theme", styles={"test": Style(color="red")}
        )
    )
    theme = tm.get("test")

    # should raise error
    with pytest.raises(ValueError):
        theme.save()


def test_theme_load(themes):
    """Test Theme.load"""

    theme_dir = tempfile.TemporaryDirectory()
    theme_path = os.path.join(theme_dir.name, "test.theme")
    theme = Theme(
        name="test",
        description="Test theme",
        styles={"test": Style(color="red")},
        path=theme_path,
    )
    assert theme.description == "Test theme"

    # create a new theme with same path and write it to file
    theme2 = Theme(
        name="test2",
        description="Test 2 theme",
        styles={"test": Style(color="red")},
        path=theme_path,
    )
    theme2.save()

    # load the theme from file and check that metadata is updated
    theme.load()
    assert theme.name == "test2"
    assert theme.description == "Test 2 theme"


def test_theme_load_no_path(themes):
    """Test Theme.load when theme has no path"""

    theme = Theme(
        name="test",
        description="Test theme",
        styles={"test": Style(color="red")},
    )

    with pytest.raises(FileNotFoundError):
        theme.load()


def test_theme_load_bad_path(themes):
    """Test Theme.load when theme path doesn't exist"""

    with tempfile.TemporaryDirectory() as theme_dir:
        pass

    # theme_dir won't exist outside the context manager

    theme = Theme(
        name="test",
        description="Test theme",
        styles={"test": Style(color="red")},
        path=theme_dir,
    )

    with pytest.raises(FileNotFoundError):
        theme.load()


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


def test_theme_eq():
    """Test Theme.__eq__"""
    theme1 = Theme(
        name="test", description="Test theme", styles={"test": Style(color="red")}
    )
    theme2 = Theme(
        name="test", description="Test theme", styles={"test": Style(color="red")}
    )
    assert theme1 == theme2
    theme3 = Theme(
        name="test", description="Test theme", styles={"test": Style(color="blue")}
    )
    assert theme1 != theme3

    assert theme1 != "foo"


def test_rich_console():
    """Test Theme().__rich_console__"""
    theme = Theme(
        name="test", description="Test theme", styles={"test": Style(color="red")}
    )

    strio = StringIO()
    console = Console(file=strio)
    console.print(theme)
    assert "Theme: test" in strio.getvalue()


def test_theme_manager_overwrite(themes):
    """Test that ThemeManager overwrites themes with overwrite=True"""

    themes = themes.copy()
    theme_dir = tempfile.TemporaryDirectory()
    tm = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    for theme in tm.themes:
        assert os.path.exists(theme.path)

    # change file and verify it gets overwritten when overwrite=True
    new_themes = [
        Theme(
            name="dark",
            description="Dark mode theme",
            tags=["dark"],
            styles={
                "hidden": Style(color="rgb(50,50,50)", bold=True),
            },
        ),
    ]

    tm2 = ThemeManager(theme_dir=theme_dir.name, themes=new_themes, overwrite=True)
    dark2 = tm2.get("dark")
    assert dark2.name == "dark"
    assert dark2.styles["hidden"] == new_themes[0].styles["hidden"]


def test_theme_manager_update(themes):
    """Test that ThemeManager updates themes with update=True and does not with update=False"""

    theme_dir = tempfile.TemporaryDirectory()
    tm = ThemeManager(theme_dir=theme_dir.name, themes=themes)
    for theme in tm.themes:
        assert os.path.exists(theme.path)

    # change file and verify it gets overwritten when overwrite=True
    new_themes = [
        Theme(
            name="dark",
            description="Dark mode theme 2",
            tags=["dark", "new"],
            styles={
                "hidden": Style(color="rgb(50,50,50)", bold=True),
                "new_style": Style(color="rgb(42,42,42)", dim=True),
            },
        ),
    ]

    # verify update works
    tm2 = ThemeManager(theme_dir=theme_dir.name, themes=new_themes, update=True)
    dark2 = tm2.get("dark")
    assert dark2.name == "dark"
    assert dark2.tags == ["dark", "new"]
    assert dark2.description == "Dark mode theme 2"
    assert dark2.styles["hidden"] == themes[0].styles["hidden"]
    assert dark2.styles["new_style"] == new_themes[0].styles["new_style"]


def test_theme_union_operators():
    """Test union of Theme objects"""
    theme1 = Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(color="rgb(255,85,85)", bold=True),
            "style3": Style(color="rgb(241,250,140)", bold=True),
        },
    )

    theme2 = Theme(
        name="dark",
        description="Dark mode theme 2",
        tags=["dark", "new"],
        styles={
            "new_style": Style(color="rgb(42,42,42)", dim=True),  # this is new
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(
                color="rgb(1,1,1)", bold=True
            ),  # this is changed, also #style3 is missing
        },
    )

    theme3 = theme1 | theme2
    assert theme3.name == "dark"
    assert theme3.description == "Dark mode theme 2"
    assert theme3.tags == ["dark", "new"]
    assert theme3.styles["style1"] == theme1.styles["style1"]  # no change
    assert theme3.styles["style2"] == theme2.styles["style2"]  # changed
    assert theme3.styles["style3"] == theme1.styles["style3"]  # missing in theme2
    assert theme3.styles["new_style"] == theme2.styles["new_style"]  # new

    theme4 = theme2 | theme1
    assert theme4.name == "dark"
    assert theme4.description == "Dark mode theme"
    assert theme4.tags == ["dark", "new"]
    assert theme4.styles["style1"] == theme2.styles["style1"]  # no change
    assert theme4.styles["style2"] == theme1.styles["style2"]  # changed
    assert theme4.styles["style3"] == theme1.styles["style3"]  # missing in theme2
    assert theme4.styles["new_style"] == theme2.styles["new_style"]  # new

    theme5 = theme1 | theme1
    assert theme5.name == "dark"
    assert theme5.description == "Dark mode theme"
    assert theme5.tags == ["dark"]
    assert theme5.styles == theme1.styles

    theme1 |= theme2
    assert theme1.name == "dark"
    assert theme1.description == "Dark mode theme 2"
    assert theme1.tags == ["dark", "new"]
    assert theme1.styles["style1"] == theme1.styles["style1"]  # no change
    assert theme1.styles["style2"] == theme2.styles["style2"]  # changed
    assert theme1.styles["style3"] == theme1.styles["style3"]  # missing in theme2
    assert theme1.styles["new_style"] == theme2.styles["new_style"]  # new


def test_theme_union_operators_not_implemented():
    """Test union of Theme objects with non Theme objects"""
    theme1 = Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(color="rgb(255,85,85)", bold=True),
            "style3": Style(color="rgb(241,250,140)", bold=True),
        },
    )

    theme2 = RichTheme(
        styles={
            "new_style": Style(color="rgb(42,42,42)", dim=True),  # this is new
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(
                color="rgb(1,1,1)", bold=True
            ),  # this is changed, also #style3 is missing
        },
    )

    with pytest.raises(TypeError):
        theme1 | theme2

    with pytest.raises(TypeError):
        theme2 | theme1

    with pytest.raises(TypeError):
        theme1 |= theme2

    with pytest.raises(TypeError):
        theme2 |= theme1


def test_theme_update():
    """Test union of Theme objects via Theme.update()"""
    theme1 = Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(color="rgb(255,85,85)", bold=True),
            "style3": Style(color="rgb(241,250,140)", bold=True),
        },
    )

    theme2 = Theme(
        name="dark",
        description="Dark mode theme 2",
        tags=["dark", "new"],
        styles={
            "new_style": Style(color="rgb(42,42,42)", dim=True),  # this is new
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(
                color="rgb(1,1,1)", bold=True
            ),  # this is changed, also #style3 is missing
        },
    )

    theme1.update(theme2)

    assert theme1.name == "dark"
    assert theme1.description == "Dark mode theme 2"
    assert theme1.tags == ["dark", "new"]
    assert theme1.styles["style1"] == theme1.styles["style1"]  # no change
    assert theme1.styles["style2"] == theme2.styles["style2"]  # changed
    assert theme1.styles["style3"] == theme1.styles["style3"]  # missing in theme2
    assert theme1.styles["new_style"] == theme2.styles["new_style"]  # new


def test_theme_update():
    """Test union of Theme objects via Theme.update()"""
    theme1 = Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(color="rgb(255,85,85)", bold=True),
            "style3": Style(color="rgb(241,250,140)", bold=True),
        },
    )

    theme2 = Theme(
        name="dark",
        description="Dark mode theme 2",
        tags=["dark", "new"],
        styles={
            "new_style": Style(color="rgb(42,42,42)", dim=True),  # this is new
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(
                color="rgb(1,1,1)", bold=True
            ),  # this is changed, also #style3 is missing
        },
    )

    theme1.update(theme2)

    assert theme1.name == "dark"
    assert theme1.description == "Dark mode theme 2"
    assert theme1.tags == ["dark", "new"]
    assert theme1.styles["style1"] == theme1.styles["style1"]  # no change
    assert theme1.styles["style2"] == theme2.styles["style2"]  # changed
    assert theme1.styles["style3"] == theme1.styles["style3"]  # missing in theme2
    assert theme1.styles["new_style"] == theme2.styles["new_style"]  # new


def test_theme_update_no_overwrite_existing_styles():
    """Test union of Theme objects via Theme.update() with overwite_existing_styles=False"""
    theme1 = Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(color="rgb(255,85,85)", bold=True),
            "style3": Style(color="rgb(241,250,140)", bold=True),
        },
    )

    theme2 = Theme(
        name="dark",
        description="Dark mode theme 2",
        tags=["dark", "new"],
        styles={
            "new_style": Style(color="rgb(42,42,42)", dim=True),  # this is new
            "style1": Style(color="#383b3d", dim=True),
            "style2": Style(
                color="rgb(1,1,1)", bold=True
            ),  # this is changed, also #style3 is missing
        },
    )

    theme1.update(theme2, overwrite_existing_styles=False)

    assert theme1.name == "dark"
    assert theme1.description == "Dark mode theme 2"
    assert theme1.tags == ["dark", "new"]
    assert theme1.styles["style1"] == theme1.styles["style1"]  # no change
    assert theme1.styles["style2"] == theme1.styles["style2"]  # changed
    assert theme1.styles["style3"] == theme1.styles["style3"]  # missing in theme2
    assert theme1.styles["new_style"] == theme2.styles["new_style"]  # new
