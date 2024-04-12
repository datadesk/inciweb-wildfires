"""Configuration file for the Sphinx documentation builder."""
from datetime import datetime
from typing import Any

project = "inciweb-wildfires"
year = datetime.now().year
copyright = f"{year} palewire"
author = "palewire"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "palewire"
pygments_style = "sphinx"

html_sidebars: dict[Any, Any] = {}
html_theme_options: dict[Any, Any] = {
    "canonical_url": "https://palewi.re/docs/inciweb-wildfires/",
    "nosidebar": True,
}

extensions = [
    "myst_parser",
    "sphinx.ext.napoleon",
]