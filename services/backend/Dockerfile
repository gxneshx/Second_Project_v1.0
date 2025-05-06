FROM python:3.12.9

# Python cofig
# Don't write '.pyc' files
# Output logs instantly
# Allow PIP to cache packages

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Install Poetry globally
RUN python -m pip install --upgrade pip && pip install poetry

# Copy dependencies description
COPY poetry.lock pyproject.toml /usr/src/poetry/

# Setting working dir for dependencies to install
WORKDIR /usr/src/poetry

# Install only main dependencies and skip installing project as a package
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Set working directory for the app itself
WORKDIR /usr/src/image-hosting-server

# Copy source code into the container
COPY src .