ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-alpine
RUN apk add --no-cache make
RUN python3 -m pip install --disable-pip-version-check --upgrade pip
COPY dist/*.whl dist/
RUN python3 -m pip install --disable-pip-version-check `ls -1 dist/*.whl`
COPY doc/ doc/
RUN python3 -m pip install --disable-pip-version-check sphinx_rtd_theme
RUN cd doc && make html
