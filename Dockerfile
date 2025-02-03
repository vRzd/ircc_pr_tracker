# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy Poetry config files first to leverage Docker caching
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Disable virtual environments in Poetry
RUN poetry config virtualenvs.create false

# Install dependencies inside the container
RUN poetry install --no-root --no-dev

# Set Python path to include /app (ensures src is recognized as a package)
ENV PYTHONPATH="/app"

# Copy the source code
COPY src/ src/
COPY src/config.yaml src/config.yaml

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

# Run the script as a module
CMD ["python", "-m", "src.main"]
