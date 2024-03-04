# Use the official Python 3.11 slim image as a base
FROM python:3.11-slim

# Install curl
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

# Set the working directory in the container
WORKDIR /app

# Copy the Python dependencies file to the container
COPY README.md pyproject.toml poetry.lock* /app/
