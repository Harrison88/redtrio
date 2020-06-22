"""Sphinx configuration."""
project = "redtrio"
author = "Harrison Morgan"
copyright = f"2020, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "autoapi.extension",
]

autoapi_type = "python"
autoapi_dirs = ["../src"]
autoapi_template_dir = "_autoapi_templates"
