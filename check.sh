set -e

PYTHON=python3

# Run static type checker and verify formatting guidelines
$PYTHON -m mypy sphinx_doc
$PYTHON -m flake8 sphinx_doc
