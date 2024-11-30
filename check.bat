@echo off
setlocal

set python=python.exe

%python% -m mypy sphinx_doc || exit /b
%python% -m flake8 sphinx_doc || exit /b

:quit
