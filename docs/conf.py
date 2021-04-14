#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ligodtt documentation build configuration file, created by
# sphinx-quickstart on Sat Jul 15 21:40:50 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    #'sphinx.ext.todo',
    #'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    #'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'ligodtt'
copyright = '2021, Lee McCuller'
author = 'McCuller'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.1.0'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', ]

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'sphinx'
#pygments_style = 'colorful'
pygments_style = 'default'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for sourcelinks

srclink_project = 'https://github.com/mccullerlp/ligodtt'
srclink_src_path = 'ligodtt'
srclink_branch = 'master'

# -- Options for HTML output ----------------------------------------------

#useful for downloading the ipynb files
html_sourcelink_suffix = ''

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#import sphinx_rtd_theme
#html_theme = "sphinx_rtd_theme"
#html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

#import jupyter_sphinx_theme
#html_theme = "jupyter_sphinx_theme"
#html_theme_path = [jupyter_sphinx_theme.get_html_theme_path()]

html_theme = "alabaster"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

#html_sidebars = {
#    '**': [
#        'localtoc.html',
#        'navigation.html',
#        'relations.html',
#        'searchbox.html',
#        'srclinks.html',
#        ],
#    'index': [
#        'globaltoc.html',
#        'navigation.html',
#        'relations.html',
#        'searchbox.html',
#        'srclinks.html',
#        ],
#}

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'ligodtt'

#html_logo = 'logo/'

def setup(app):
    app.add_stylesheet('my_theme.css')
    app.add_stylesheet('pygments_adjust.css')


