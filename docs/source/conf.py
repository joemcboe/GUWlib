# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GUWlib'
copyright = '2023, Jörn Froböse'
author = 'Jörn Froböse'
release = '2024'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'python')))

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []
autodoc_member_order = 'bysource'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'piccolo_theme'
html_static_path = ['_static']

# If specified, this will be used in the nav bar instead.
html_short_title = "GUWlib"

html_theme_options = {
    "source_url": 'https://github.com/joemcboe/GUW',
    "source_icon": "github",
}
