#!/usr/bin/env python3
from importlib.metadata import version

from packaging.version import parse

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "asphalt-exceptions"
author = "Alex Grönholm"
copyright = "2017, " + author

v = parse(version(project))
version = v.base_version
release = v.public

language = "en"

exclude_patterns = ["_build"]
pygments_style = "sphinx"
highlight_language = "python3"
todo_include_todos = False

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
htmlhelp_basename = project.replace("-", "") + "doc"

extlinks = {
    "github": (
        f"https://github.com/asphalt-framework/{project}/tree/{version}/%s",
        None,
    )
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "asphalt": ("https://asphalt.readthedocs.io/en/latest/", None),
}
