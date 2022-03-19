# Rich Theme Manager

## Description

Implements a basic "theme manager" class for managing rich [Themes](https://rich.readthedocs.io/en/stable/style.html#style-themes) in your [rich](https://github.com/Textualize/rich) CLI application.

The rich package provides an easy way to define custom styles and themes for use with rich.  This package provides a simple way to manage the themes: e.g. to list, add, remove themes, for the user to preview themes, and to manage themes on disk.

## What problem does this solve?

Consider this scenario from the rich [documentation](https://rich.readthedocs.io/en/stable/style.html#style-themes):

If you re-use styles it can be a maintenance headache if you ever want to modify an attribute or color – you would have to change every line where the style is used. Rich provides a Theme class which you can use to define custom styles that you can refer to by name. That way you only need to update your styles in one place.

Style themes can make your code more semantic, for instance a style called "warning" better expresses intent that "italic magenta underline".

To use a style theme, construct a Theme instance and pass it to the Console constructor. Here’s an example:

```python
from rich.console import Console
from rich.theme import Theme
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})
console = Console(theme=custom_theme)
console.print("This is information", style="info")
console.print("[warning]The pod bay doors are locked[/warning]")
console.print("Something terrible happened!", style="danger")
```

I highly recommend the use of Themes in your rich application instead of hard-coding colors and styles. However, there's still a problem of managing themes.  For example, letting the user of your application change the default theme styles you've chosen.  What if they are color blind and can't distinguish the colors you've selected? What if they're using a light terminal background and you've selected colors best suited for a dark terminal?  

The rich `Theme` class provides everything you to manage these situations but doing so requires a fair amount of boiler plate code for each application. This package attempts to provide an easy solution for these scenarios with a minimal amount of code.  Instead of having to implement management of theme files and allowing the user to list or preview themes yourself, you can use the `ThemeManager` class to manage themes for you.

## Synopsis

Using `rich_theme_manager` is easy and takes just a few lines of code.  Import `Theme` from `rich_theme_manager` instead of from `rich.theme` (`rich_theme_manager.Theme` subclasses `rich.theme.Theme`) then use `ThemeManager` to manage themes.  `ThemeManager` can be created with or without a `theme_dir` argument. If you don't provide `theme_dir`, `ThemeManager` will not manage themes on disk.  This may still be useful for allowing the user to list and preview themes.  If you do provide `theme_dir`, any default themes passed to `ThemeManager` will be written to `theme_dir` and any theme config files found in `theme_dir` will be loaded.

```python
from rich.console import Console
from rich.style import Style
import pathlib

from rich_theme_manager import Theme, ThemeManager


THEMES = [
    Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "info": "dim cyan",
            "warning": "bold magenta",
            "danger": "bold red",
        },
    ),
    Theme(
        name="light",
        description="Light mode theme",
        styles={
            "info": Style(color="#22863a", bold=True),
            "warning": Style(color="#032f62", bold=True),
            "danger": Style(color="#b31d28", bold=True, underline=True, italic=True),
        },
    ),
    Theme(
        name="mono",
        description="Monochromatic theme",
        tags=["mono", "colorblind"],
        styles={
            "info": "italic",
            "warning": "bold",
            "danger": "reverse bold",
        },
    ),
]

if __name__ == "__main__":
    # you can specify a config directory to save/load themes to/from
    theme_dir = pathlib.Path("~/.rich_theme_manager/themes").expanduser()
    theme_dir.expanduser().mkdir(parents=True, exist_ok=True)

    theme_manager = ThemeManager(theme_dir=theme_dir, themes=THEMES)
    theme_manager.list_themes()
    print("\n")

    dark = theme_manager.get("dark")
    theme_manager.preview_theme(dark)
    console = Console(theme=dark)
    print("\n")

    console.print("This is information", style="info")
    console.print("[warning]The pod bay doors are locked[/warning]")
    console.print("Something terrible happened!", style="danger")
```

![Example output](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/example1.png)

## Example app

A simple example app that demonstrates the ThemeManager class comes with rich_theme_manager in `__main__.py`:

`python -m rich_theme_manager`:

```text
usage: rich_theme_manager [-h] [--example [EXAMPLE]] [--list] [--preview THEME] [--config THEME]

Example CLI usage of rich_theme_manager

optional arguments:
  -h, --help           show this help message and exit
  --example [EXAMPLE]  Show example output for theme.
  --list               List themes.
  --preview THEME      Preview theme.
  --config THEME       Print configuration for theme THEME.
```

`python -m rich_theme_manager --list`:

![Example --list output](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/list.png)

`python -m rich_theme_manager --preview dark`:

![Example --preview output](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/preview_dark.png)

## Documentation

### Theme class

`rich_theme_manager.Theme` is a subclass of `rich.theme.Theme` and provides additional functionality for managing themes.

```python
    Theme(
          name: str,
          description: Optional[str] = None,
          styles: Optional[Mapping[str, StyleType]] = None,
          inherit: bool = True,
          tags: Optional[List[str]] = None,
          path: Optional[str] = None,
    )
```

Arguments

* `name`: The name of the theme; required
* `description`: An optional description of the theme.
* `styles`: An optional mapping of style names to styles.
* `inherit`: Whether the theme inherits from the default theme.
* `tags`: An optional list of tags for the theme; useful for allowing user to filter themes.
* `path`: The path to the theme file; in normal use this is not needed as `ThemeManager` will automatically create the theme file.

Properties

* `Theme().name`: The name of the theme
* `Theme().description`: Description of the theme
* `Theme().tags`: List of tags for the theme
* `Theme().inherit`: bool indicating whether the theme inherits from the default theme
* `Theme().style_names`: List of names for styles in the theme
* `Theme().path`: The path to the theme file; (getter/setter)
* `Theme().config`: Contents of a configuration file for the theme (same format as `rich.theme.Theme().config` but with an additional `[metadata]` section)

Methods

* `Theme().save()`: Save the theme to disk (to `Theme().path`)
* `Theme().load()`: Load the theme from disk (from `Theme().path`)
* `Theme().to_file(path: str)`: Save the theme to disk (to `path`)

Class Methods:

* `Theme.from_file(config_file: IO[str], source: Optional[str] = None, inherit: bool = True)` -> `Theme`: Load a theme from a text mode configuration file (in [configparser](https://docs.python.org/3/library/configparser.html) INI format).
* `Theme.read(path: str, inherit: bool = True) -> Theme`: Load a theme from disk (from `path`)

The `.theme` INI file format looks like this:

```ini
[metadata]
name = dark
description = Dark mode theme
tags = dark
inherit = True

[styles]
danger = bold red
info = dim cyan
warning = bold magenta
```

Here's an real world example of a theme INI file from one of my [apps](https://github.com/RhetTbull/osxphotos):

```INI
[metadata]
name = dark
description = Dark mode theme
tags = dark
inherit = True

[styles]
bar.back = rgb(68,71,90)
bar.complete = rgb(249,38,114)
bar.finished = rgb(80,250,123)
bar.pulse = rgb(98,114,164)
color = rgb(248,248,242)
count = rgb(139,233,253)
error = bold rgb(255,85,85)
filename = bold rgb(189,147,249)
filepath = bold rgb(80,250,123)
highlight = bold #000000 on #d73a49
num = bold rgb(139,233,253)
progress.elapsed = rgb(139,233,253)
progress.percentage = rgb(255,121,198)
progress.remaining = rgb(139,233,253)
time = bold rgb(139,233,253)
uuid = rgb(255,184,108)
warning = bold rgb(241,250,140)
```

`Theme` implements the [rich Console protocol](https://rich.readthedocs.io/en/stable/protocol.html) which means that you use `rich.print()` and `rich.console.Console().print()` to print a theme to the console.  Doing so results in a preview of the theme which visually shows the colors and styles used in the theme.

![Theme preview](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/theme_preview_print.png)

The `Theme` preview will use default sample text for each style. You can change the sample text by setting the `rich_theme_manager.theme.SAMPLE_TEXT` global variable.

![Theme preview with sample text](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/theme_preview_sample_text.png)

`Theme` implements the `__eq__` method so two `Theme` instances can be easily compared for equality. `Theme` instances are considered equal if all properties with exception of `path` are equal.

### ThemeManager class

```python
    ThemeManager(
        theme_dir: Optional[str] = None,
        themes: Optional[List[Theme]] = None,
    )
```

Arguments:

* `theme_dir`: Optional directory to save/load themes to/from.
* `themes`: Optional list of Theme objects

If provided, `theme_dir` must exist.  If `theme_dir` is set (for example, using [click.get_app_dir](https://click.palletsprojects.com/en/8.0.x/api/?highlight=get_app_dir#click.get_app_dir)), upon initialization `ThemeManager` will save any default themes provided via `themes` to `theme_dir` and load any themes from `theme_dir`.  Theme files are standard INI files as created by [configparser](https://docs.python.org/3/library/configparser.html) and are named `<name>.theme` where `<name>` is the name of the Theme (see `Theme.name`).  If a theme file already exists, it will be loaded and `ThemeManager` will not overwrite it.

Properties:

* `ThemeManager().themes`: List of themes

Methods:

* `ThemeManager().add(theme: Theme, overwrite=False) -> None`: Add a theme to the list of managed themes.  If `overwrite` is True, the theme file will be overwritten if it already exists.
* `ThemeManager().remove(theme: Theme) -> None`: Remove a theme from the list of managed themes and delete the theme file if it exists.
* `ThemeManager().get(theme_name: str) -> Theme`: Get a theme by name. Raises 'ValueError` if no theme with the given name is found.
* `ThemeManager().load_themes(theme_dir=None) -> None`: Load themes from `theme_dir` (or `ThemeManager().theme_dir` if not provided).  Any `.theme` files found in `theme_dir` will be loaded and added to the list of managed themes.
* `ThemeManager().write_themes(overwrite=False) -> None`: Write themes to file (as specified in each `Theme().path` which will be set automatically by `ThemeManager`).  If `overwrite` is True, the theme file will be overwritten if it already exists.

* `ThemeManager().list_themes(show_path: bool = True, theme_names: Optional[List[str]] = None, console: Optional[Console] = None) -> None`: Print a list of themes to the console.  If `show_path` is True, the path to the theme file will be printed.  If `theme_names` is provided, only themes with names in the list will be printed. An optional `rich.console.Console()` instance may be provided to print to a specific console.

![ThemeManager list example](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/theme_manager_list.png)

Class Methods:

* `ThemeManager.preview_theme(theme: Theme, sample_text: Optional[str] = None, show_path: bool = True, console: Optional[Console] = None) -> None`: Print a preview of the theme to the console showing the style of each style in the theme.  If `sample_text` is provided, it will be used as the sample text to preview otherwise a default string will be used.  If `show_path` is True, the path to the theme file will be printed.  An optional `rich.console.Console()` instance may be provided to print to a specific console.

![ThemeManager preview example](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/theme_manager_preview.png)

## Test Coverage

100% coverage of all code with exception of the example CLI app.

```text
Name                               Stmts   Miss  Cover
------------------------------------------------------
rich_theme_manager/__init__.py         5      0   100%
rich_theme_manager/manager.py         71      0   100%
rich_theme_manager/theme.py          134      0   100%
tests/__init__.py                      0      0   100%
tests/conftest.py                      7      0   100%
tests/test_rich_theme_manager.py     256      0   100%
------------------------------------------------------
TOTAL                                473      0   100%
```

## License

MIT License

## Contributing

Contributions of all kinds are welcome!  Please submit pull requests, issues, and/or suggestions to the [github repo](https://github.com/RhetTbull/rich_theme_manager).

## Credits

Thank you to [Will McGugan](https://github.com/willmcgugan) for creating [rich](https://github.com/Textualize/rich) and helping to make our command line interfaces more beautiful!

## Projects Using Rich Theme Manager

* [osxphotos](https://github.com/RhetTbull/osxphotos): Python app to export pictures and associated metadata from Apple Photos on macOS. Also includes a package to provide programmatic access to the Photos library, pictures, and metadata.
