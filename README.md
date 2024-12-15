# Enrich Sphinx documentation with Python type information

This extension to Sphinx [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) enriches class member variable and function parameter lists with type information extracted from Python type annotations.

Refer to the [Sphinx HTML output](https://hunyadi.github.io/sphinx_doc/) for a live demonstration.

## Usage

1. Ensure that you have type hints in all your classes, functions and methods.
2. Add description to your classes, functions and methods as a doc-string.
3. Use `:param name: text` to assign a description to member variables and function parameters.
4. Register `Processor` to the events `autodoc-process-docstring` and `autodoc-before-process-signature`.
5. Enjoy how type information is automatically injected in the doc-string on `make html`.

## Minimalistic example

The following code shows how to hook `Processor` to the events `autodoc-process-docstring` and `autodoc-before-process-signature` in Sphinx's `conf.py`:

```python
from sphinx.application import Sphinx
from sphinx_doc.autodoc import Processor, include_special

def setup(app: Sphinx) -> None:
    processor = Processor()
    app.connect("autodoc-process-docstring", processor.process_docstring)
    app.connect("autodoc-before-process-signature", processor.process_signature)
    app.connect("autodoc-skip-member", include_special)
```

Refer to the [published sample](https://github.com/hunyadi/sphinx_doc/blob/master/doc/conf.py) for a more detailed example how to use this extension with Sphinx.

## Motivation

To pass type information to `autodoc`, you would normally be required to use the [info field list](https://www.sphinx-doc.org/en/master/usage/domains/python.html#info-field-lists) items `:param:` and/or `:type:` with explicit type specification:

```python
def send_message(
    sender: str,
    recipient: str,
    message_body: str,
    priority: int = 1,
) -> int:
    """
    :param str sender: The person sending the message.
    :param str recipient: The recipient of the message.
    :param str message_body: The body of the message.
    :param priority: The priority of the message, can be a number 1-5.
    :type priority: integer or None
    :return: The message identifier.
    :rtype: int
    """
```

However, a great deal of information is already present in the Python type signature. This extension promotes a more compact parameter definition whereby type information is injected automatically in documentation strings, and you only need to provide description text:

```python
def send_message(
    sender: str,
    recipient: str,
    message_body: str,
    priority: int = 1,
) -> int:
    """
    :param sender: The person sending the message.
    :param recipient: The recipient of the message.
    :param message_body: The body of the message.
    :param priority: The priority of the message, can be a number 1-5.
    :returns: The message identifier.
    """
```

## Features

* Data-class member variables are published if they have a corresponding `:param ...:` in the class-level doc-string.
* All enumeration members are published, even if they lack a description.
* Magic methods (e.g. `__eq__`) are published if they have a doc-string.
* Multi-line code blocks in doc-strings are converted to syntax-highlighted monospace text.
* Primary keys in entity classes have extra visuals (e.g. with a symbol 🔑). See [pysqlsync](https://github.com/hunyadi/pysqlsync) for how to define an entity class (using the `@dataclass` syntax) with a primary key (with the type hint `PrimaryKey[T]`).
* Type aliases are substituted even if [Postponed Evaluation of Annotations (PEP 563)](https://peps.python.org/pep-0563/) is turned off.
