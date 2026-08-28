# Configuration file for the Sphinx documentation builder.
import os
import sys

# Add the backend directory to the Python path so Sphinx can find your modules
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = 'Book Recommender System'
copyright = '2026, Paria Khanjan'
author = 'Your Name'
release = '2.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'Book Recommender System Documentation'