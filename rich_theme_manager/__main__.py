"""Example CLI usage of rich_theme_manager.
Uses argparse for no dependencies but should be easily adapatable to click or typer
"""

import argparse
import os
import sys
import tempfile
from textwrap import dedent

from rich.console import Console
from rich.style import Style

# import Theme from rich_theme_manager
from rich_theme_manager import Theme, ThemeManager

# Sample themes for use in the CLI
THEMES = [
    Theme(
        name="dark",
        description="Dark mode theme",
        tags=["dark"],
        styles={
            "hidden": Style(color="#383b3d", dim=True),
            "error": Style(color="rgb(255,85,85)", bold=True),
            "filename": Style(color="rgb(189,147,249)", bold=True),
            "filepath": Style(color="rgb(80,250,123)", bold=True),
            "highlight": Style(color="#000000", bgcolor="#d73a49", bold=True),
            "num": Style(color="rgb(139,233,253)", bold=True),
            "time": Style(color="rgb(139,233,253)", bold=True),
            "warning": Style(color="rgb(241,250,140)", bold=True),
        },
    ),
    Theme(
        name="light",
        description="Light mode theme",
        styles={
            "hidden": Style(color="#383b3d", dim=True),
            "error": Style(color="#b31d28", bold=True, underline=True, italic=True),
            "filename": Style(color="#6f42c1", bold=True),
            "filepath": Style(color="#22863a", bold=True),
            "highlight": Style(color="#ffffff", bgcolor="#d73a49", bold=True),
            "num": Style(color="#005cc5", bold=True),
            "time": Style(color="#032f62", bold=True),
            "warning": Style(color="#e36209", bold=True, underline=True, italic=True),
        },
    ),
    Theme(
        name="mono",
        description="Monochromatic theme",
        tags=["mono", "colorblind"],
        styles={
            "hidden": "dim",
            "error": "reverse italic",
            "filename": "bold",
            "filepath": "bold underline",
            "highlight": "reverse italic",
            "num": "bold",
            "time": "bold",
            "warning": "bold italic",
        },
    ),
    Theme(
        name="plain",
        description="Plain theme with no colors",
        tags=["colorblind"],
        styles={
            "hidden": "",
            "error": "",
            "filename": "",
            "filepath": "",
            "highlight": "",
            "num": "",
            "time": "",
            "warning": "",
        },
    ),
]


def get_theme_dir() -> str:
    """Get the theme directory"""
    # with click, this would be a good place to use get_app_dir
    theme_dir = os.path.join(tempfile.gettempdir(), ".rich_theme_manager")
    if not os.path.exists(theme_dir):
        os.mkdir(theme_dir)
    return theme_dir


def validate_theme_name(name: str) -> None:
    """Check if name is a valid theme name"""
    valid_themes = [theme.name for theme in THEMES]
    if name not in valid_themes:
        print(
            f"'{name}' is not a valid theme name. Valid themes are: {valid_themes}",
            file=sys.stderr,
        )
        sys.exit(1)


def print_example_output(theme: Theme) -> None:
    """Print example output using theme"""
    example_text = f"""
    The following shows examples of how to use custom rich styles with your text.

    This is an example filepath: [filepath]{sys.argv[0]}[/]
    This is an example filename: [filename]{os.path.split(sys.argv[0])[1]}[/]
    This is an example of hidden filename: [hidden].zshrc[/]
    This is an example of a warning: [warning]I've giv'n her all she's got captain, an' I canna give her no more.[/]
    This is an example of an error: [error]I'm sorry, Dave. I'm afraid I can't do that.[/]
    This is an example of a highlight: [highlight]foo[/]
    This is an example of a number: [num]42[/]
    This is an example of a time: [time]12:34[/]
    """
    console = Console(theme=theme, highlight=False)
    console.print(dedent(example_text))


def cli():
    """Example CLI for use of rich_theme_manager"""
    # using argparse so there are no dependencies but dang,
    # does this make me appreciate click and typer better!
    parser = argparse.ArgumentParser(
        prog="rich_theme_manager", description="Example CLI usage of rich_theme_manager"
    )
    parser.add_argument(
        "--example",
        nargs="?",
        const="dark",
        help="Show example output for theme.",
    )
    parser.add_argument(
        "--list",
        help="List themes.",
        action="store_true",
    )
    parser.add_argument(
        "--preview",
        metavar="THEME",
        nargs=1,
        help="Preview theme.",
    )
    parser.add_argument(
        "--config",
        metavar="THEME",
        nargs=1,
        help="Print configuration for theme THEME.",
    )
    args = parser.parse_args()
    theme_manager = ThemeManager(theme_dir=get_theme_dir(), themes=THEMES)

    if not any([args.example, args.list, args.preview, args.config]):
        parser.print_help()
        return

    if args.example:
        validate_theme_name(args.example)
        theme = theme_manager.get(args.example)
        print_example_output(theme)
        return

    if args.list:
        theme_manager.list_themes()
        return

    if args.preview:
        validate_theme_name(args.preview[0])
        theme = theme_manager.get(args.preview[0])
        theme_manager.preview_theme(theme)
        return

    if args.config:
        theme = theme_manager.get(args.config[0])
        print(theme.config)
        return


if __name__ == "__main__":
    cli()
