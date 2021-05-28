# syntax=docker/dockerfile:1.2


# base image
FROM python:3.7-slim-buster as base

ARG GROUPID=1000
ARG USERID=1000
ARG USERNAME=justsomeuser

## configure python and pip runtime settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PYTHONCOERCECLOCALE=0 \
    PYTHONUTF8=1 \
    PIP_NO_CACHE_DIR=1

## setup user and install system packages
RUN set -ex && \
    groupadd -g $GROUPID $USERNAME && \
    useradd -lmu $USERID -g $USERNAME -s /bin/bash $USERNAME && \
    apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install --no-install-recommends -y neovim curl && \
    apt-get autoremove --purge && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

## set user $HOME and set working directory
ENV HOME=/home/$USERNAME
USER $USERNAME
WORKDIR $HOME/foghorn


# builder image
FROM base as development

## configure poetry settings
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1 \
    PATH="${HOME}/.poetry/bin:${PATH}"

## install poetry
SHELL [ "/bin/bash", "-o", "pipefail", "-c" ]
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

## copy and install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root --remove-untracked

## copy everything else
COPY . ./
RUN poetry install --no-dev && \
    poetry build --format wheel

CMD [ "/bin/bash" ]


# final image
FROM base

## install foghorn
COPY --from=development $HOME/foghorn/dist/foghorn-*.whl ./
RUN pip install --user ./foghorn-*.whl

CMD [ "python", "-c", "'import foghorn; foghorn.hello_world()'" ]