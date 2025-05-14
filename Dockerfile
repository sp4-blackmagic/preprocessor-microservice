# -----------------------------------------------------------------------------
# Base Stage: Use an official Python runtime as a parent image
# -----------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents Python from writing .pyc files
ENV PYTHONUNBUFFERED 1         # Force stdin, stdout, and stderr to be unbuffered

# Set working directory
WORKDIR /app

# Use pip to bootstrap uv itself.
RUN pip install --no-cache-dir uv

# Create a non-root user and group for security
RUN groupadd -r appgroup && useradd -r -g appgroup -m -d /app appuser
# The -m flag creates the home directory (/app in this case)
# The -d /app sets the home directory. WORKDIR /app already exists.

# Copy pyproject.toml first to leverage Docker layer caching for dependencies
COPY --chown=appuser:appgroup pyproject.toml ./

# Create a virtual environment using uv and install dependencies
RUN uv venv .venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache .

# Make the venv's bin directory available on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application code
# Ensure .dockerignore is properly set up to exclude unnecessary files
COPY --chown=appuser:appgroup ./app ./app
COPY --chown=appuser:appgroup ./app/data_mocks ./data_mocks

# Switch to the non-root user
USER appuser

# Expose the port the app runs on (FastAPI default is 8000)
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]