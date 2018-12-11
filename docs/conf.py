# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
#
# faucet documentation build configuration file, created by
# sphinx-quickstart on Thu Oct 26 13:48:25 2017.
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
import os
import sys

from docutils.parsers.rst.directives import tables
from docutils.statemachine import StringList

sys.path.insert(0, os.path.abspath('../'))

autodoc_default_flags = ["members", "undoc-members", "show-inheritance"]

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
needs_sphinx = '1.7'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.coverage',
              'sphinx.ext.doctest',
              'sphinx.ext.githubpages',
              'sphinx.ext.napoleon',
              'sphinx.ext.viewcode'
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
copyright = u'2018, Faucet Developers' # pylint: disable=redefined-builtin
author = u'Faucet Developers'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'README.rst', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

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
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'faucetdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'faucet.tex', u'Faucet Documentation',
     u'Faucet Developers', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'faucet', u'Faucet Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'faucet', u'Faucet Documentation',
     author, 'faucet', '',
     'Miscellaneous'),
]

# -- Magic to run sphinx-apidoc automatically -----------------------------

# See https://github.com/rtfd/readthedocs.org/issues/1139
# on which this is based.

def run_apidoc(_):
    """Call sphinx-apidoc on faucet module"""
    from sphinx.ext.apidoc import main as apidoc_main
    apidoc_main(['-e', '-o', 'source/apidoc', '../faucet'])

class FaucetPromMetricsTable(tables.ListTable):
    """Autogen prometheus metrics documentation"""

    options = {'header-rows': 1, 'widths': [31, 15, 15, 60]}

    def run(self):
        import faucet.faucet_metrics
        from prometheus_client import CollectorRegistry

        self.block_text = """\
* - Metric
  - Type
  - Description
"""

        faucet_metrics = faucet.faucet_metrics.FaucetMetrics(reg=CollectorRegistry())
        for metric in faucet_metrics._reg.collect():
            if metric.type == "counter":
                metric_name = "{}_total".format(metric.name)
            else:
                metric_name = metric.name

            self.block_text += """\
* - {}
  - {}
  - {}
""".format(metric_name, metric.type, metric.documentation)

        self.content = StringList()
        for lineno, line in enumerate(self.block_text.split('\n')):
            self.content.append(line, __file__, lineno)

        return super(FaucetPromMetricsTable, self).run()

class GaugePromMetricsTable(tables.ListTable):
    """Autogen prometheus metrics documentation"""

    options = {'header-rows': 1, 'widths': [31, 15, 15, 60]}

    def run(self):
        import faucet.gauge_prom
        from prometheus_client import CollectorRegistry

        self.block_text = """\
* - Metric
  - Type
  - Description
"""

        gauge_metrics = faucet.gauge_prom.GaugePrometheusClient(reg=CollectorRegistry())
        for metric in gauge_metrics._reg.collect():
            if metric.type == "counter":
                metric_name = "{}_total".format(metric.name)
            else:
                metric_name = metric.name

            self.block_text += """\
* - {}
  - {}
  - {}
""".format(metric_name, metric.type, metric.documentation)

        self.content = StringList()
        for lineno, line in enumerate(self.block_text.split('\n')):
            self.content.append(line, __file__, lineno)

        return super(GaugePromMetricsTable, self).run()

def setup(app):
    # Add custom css
    app.add_css_file("css/responsive-tables.css")
    """Over-ride Sphinx setup to trigger sphinx-apidoc."""
    app.connect('builder-inited', run_apidoc)
    app.add_directive('faucet-prom-metrics-table', FaucetPromMetricsTable)
    app.add_directive('gauge-prom-metrics-table', GaugePromMetricsTable)
