# Enrich Sphinx documentation with Python type information

This extension to Sphinx [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) enriches class member variable and function parameter lists with type information extracted from Python type annotations.

## Usage

1. Ensure that you have type hints in all your classes, functions and methods.
2. Add description to your classes, functions and methods as a doc-string.
3. Use `:param name: text` to assign a description to member variables and function parameters.
4. Register `DocstringProcessor` to the event `autodoc-process-docstring` in Sphinx's `conf.py`.
5. Enjoy how type information is automatically injected in the doc-string on `make html`.

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