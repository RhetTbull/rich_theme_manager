"""test config file for rich_theme_manager"""

import pytest
from rich.style import Style
from rich_theme_manager import Theme

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


@pytest.fixture(scope="session")
def themes():
    return THEMES
