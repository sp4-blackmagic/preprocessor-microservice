FROM python:3.13-slim-bookworm AS base

# Set environment variables for Python

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1  
# Force stdin, stdout, and stderr to be unbuffered
ENV PYTHONUNBUFFERED=1         

# Set working directory
WORKDIR /app

# Some dependencies for ultralytics 
RUN apt-get update && apt-get install libgl1 libglib2.0-0 -y

# Install uv
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
COPY --chown=appuser:appgroup ./app ./app
COPY --chown=appuser:appgroup ./app/example_data ./example_data

# Switch to the non-root user
USER appuser

# Expose the port the app runs on (FastAPI default is 8000)
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
# Don't remember why it has to be hosted on 0.0.0.0 but it breaks if it's on
# localhost so I just left it as is for now