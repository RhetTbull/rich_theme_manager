# Rich Theme Manager

## Description
Implements a basic "theme manager" class for managing rich Themes in your [rich](https://github.com/Textualize/rich) CLI application.

The rich package provides an easy way to define custom styles and themes for use with rich.  This package provides a simple way to manage the themes: e.g. to list, add, remove themes, for the user to preview themes, and to manage themes on disk.

## Synopsis

```python
from rich.console import Console
from rich.style import Style

from rich_theme_manager import Theme, ThemeManager

THEMES = [
    Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "error": Style(color="rgb(255,85,85)", bold=True),
            "filepath": Style(color="rgb(80,250,123)", bold=True),
            "time": Style(color="rgb(139,233,253)", bold=True),
        },
    ),
    Theme(
        name="light",
        description="Light mode theme",
        styles={
            "error": Style(color="#b31d28", bold=True, underline=True, italic=True),
            "filepath": Style(color="#22863a", bold=True),
            "time": Style(color="#032f62", bold=True),
        },
    ),
    Theme(
        name="mono",
        description="Monochromatic theme",
        tags=["mono", "colorblind"],
        styles={
            "error": "reverse italic",
            "filepath": "bold underline",
            "time": "bold",
        },
    ),
]

if __name__ == "__main__":
    theme_manager = ThemeManager(themes=THEMES)
    theme_manager.list_themes(show_path=False)
    dark = theme_manager.get("dark")
    theme_manager.preview_theme(dark, show_path=False)
    console = Console(theme=THEMES[0])
    console.print("[error]Oh No![/error]")
```

![Example output](https://github.com/RhetTbull/rich_theme_manager/raw/main/images/example1.png)

## Example app

A simple example app that demonstrates the ThemeManager class comes with rich_theme_manager in `__main__.py`:

`python -m rich_theme_manager`:

```
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

Coming!

In a nutshell, use `from rich_theme_manager import Theme` instead of `from rich.theme import Theme` and use `from rich_theme_manager import ThemeManager` to create a ThemeManager instance.  

`rich_theme_manager.ThemeManager(theme_dir: Optional[str] = None, themes: Optional[List[Theme]] = None)`

If you specify a `theme_dir` (for example, using [click.get_app_dir](https://click.palletsprojects.com/en/8.0.x/api/?highlight=get_app_dir#click.get_app_dir)), ThemeManager will read/write themes from/to that directory.  If you specify a `themes` list, ThemeManager will use that list of themes as the default themes and will write the defaults to the theme directory if not already present.  

This allows you to easily define default "starting" themes for your application but the user can then edit the theme files (which are INI files created by [configparser](https://docs.python.org/3/library/configparser.html)) to customize the CLI.

Theme subclasses `rich.theme.Theme`.  You must specify a name and can optionally specify a description, a list of tags, and a path to save the theme to (via `Theme.save()`).

`Theme(name: str, description: Optional[str] = None, styles: Optional[Mapping[str, StyleType]] = None, inherit: bool = True, tags: Optional[List[str]] = None, path: Optional[str] = None)`

## License

MIT License

## Contributing

Contributions of all kinds are welcome!

## Credits

Thank you to [Will McGugan](https://github.com/willmcgugan) for creating [rich](https://github.com/Textualize/rich) and helping to make our command line interfaces more beautiful!
