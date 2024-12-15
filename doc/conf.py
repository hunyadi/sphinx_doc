import datetime
import os
import sys

import sphinx.ext.autodoc
from sphinx.application import Sphinx
from strong_typing.core import JsonType

from sphinx_doc.autodoc import MockedClassDocumenter, Processor, include_special

sys.path.insert(0, os.path.abspath("."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Enrich Sphinx documentation with Python type information"
copyright = f"{datetime.datetime.now().year}, Levente Hunyadi"
author = "Levente Hunyadi"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_design",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".mypy_cache", ".pytest_cache"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 3,
    "collapse_navigation": True,
    "sticky_navigation": True,
}
html_static_path = ["_static"]
html_css_files = [
    "css/properties.css",
]
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True

# -- Options including documentation from Python doc-strings -----------------

add_module_names = False
autoclass_content = "class"
autodoc_class_signature = "separated"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "exclude-members": "__init__",
    "member-order": "bysource",
    "show-inheritance": True,
}
autodoc_typehints = "signature"


sphinx.ext.autodoc.ClassDocumenter = MockedClassDocumenter  # type: ignore


class json:
    "A string in JSON notation."


def setup(app: Sphinx) -> None:
    processor = Processor(type_transform={JsonType: json})
    app.connect("autodoc-process-docstring", processor.process_docstring)
    app.connect("autodoc-before-process-signature", processor.process_signature)
    app.connect("autodoc-skip-member", include_special)
