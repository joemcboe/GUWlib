# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GUWlib'
copyright = '2024, Jörn Froböse'
author = 'Jörn Froböse'
release = '02/2024'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'python')))
sys.path.insert(0, os.path.abspath('.'))

# extensions = ['sphinx.ext.autodoc']
autoclass_content = 'both'
autoapi_python_class_content = 'both' 
autodoc_member_order = 'groupwise'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx_togglebutton',
              'custom_directives', 'sphinx.ext.autosectionlabel']    #'autoapi.extension']
napoleon_use_ivar = True
autodoc_typehints = "none"

exclude_patterns = []
# autodoc_member_order = 'bysource'

# -- AutoAPI settings --------------------------------------------------------
autoapi_dirs = ['../../python/guwlib/']
autoapi_type = "python"
autoapi_template_dir = "_autoapi_templates"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_add_toctree_entry = False
# autoapi_keep_files = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'piccolo_theme'
# html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# If specified, this will be used in the nav bar instead.
html_short_title = "GUWlib"

html_theme_options = {
    "source_url": 'https://git.rz.tu-bs.de/j.froboese/GUW',
    "source_icon": "gitlab",
}

togglebutton_hint = "Show base class"
togglebutton_hint_hide = "Hide base class"
