Enrich Sphinx documentation with Python type information
========================================================

This extension to Sphinx `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_ enriches class
member variable and function parameter lists with type information extracted from Python type annotations.

This page is a demonstration of the tool's capabilities; visit the `project page <https://github.com/hunyadi/sphinx_doc>`_
for more information.

Usage
-----

1. Ensure that you have type hints in all your classes, functions and methods.
2. Add description to your classes, functions and methods as a doc-string.
3. Use ``:param name: text`` to assign a description to member variables and function parameters.
4. Register ``Processor`` to the events ``autodoc-process-docstring`` and ``autodoc-before-process-signature`` in Sphinx's ``conf.py``.
5. Enjoy how type information is automatically injected in the doc-string on ``make html``.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   objects
