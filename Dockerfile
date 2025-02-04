# Use an official Python runtime based on Alpine Linux
FROM python:3.8-alpine

# Install system dependencies for Chromium/Chromedriver and building Python packages.
# You might need additional packages (like git, bash, etc.) depending on your project.
RUN apk update && apk add --no-cache \
    chromium \
    chromium-chromedriver \
    build-base \
    libffi-dev \
    openssl-dev

# Set environment variables so that tools like Selenium know where Chromium is.
# On Alpine, the Chromium binary is typically installed as either /usr/bin/chromium or /usr/bin/chromium-browser.
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Install Poetry using pip
RUN pip install --no-cache-dir poetry

# Set the working directory for your application
WORKDIR /app

# Copy Poetry configuration files into the container
COPY pyproject.toml poetry.lock ./

# Configure Poetry to install packages globally rather than creating a virtual environment.
RUN poetry config virtualenvs.create false

# Install Python dependencies as specified in your pyproject.toml/poetry.lock.
# The flags below tell Poetry not to install the current package (if present) and to skip dev dependencies.
RUN poetry install --no-root --no-dev

# Copy the rest of your application code into the container.
# Adjust the paths as necessary for your project structure.
COPY src/ src/

# Optionally set any other environment variables your app may need.
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

# Specify the command to run your application.
CMD ["python", "-m", "src.main"]
