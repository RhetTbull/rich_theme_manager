"""Example CLI usage of rich_theme_manager.  
Uses argparse for no dependencies but should be easily adapatable to click or typer
"""

import argparse


def cli():
    parser = argparse.ArgumentParser(
        description="Example CLI usage of rich_theme_manager"
    )
    parser.add_argument(
        "--theme", metavar="THEME_NAME", type=str, nargs=1, help="Theme name"
    )
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    cli()
