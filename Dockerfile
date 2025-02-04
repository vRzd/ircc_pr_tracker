# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary dependencies for Chrome and Chromedriver
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 \
    libnss3 libxss1 libappindicator3-1 xdg-utils libgbm1 libasound2 \
    google-chrome-stable \
    && apt-get clean

# Install Chromedriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Copy Poetry config files first
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

# Debug: Check if Chrome and Chromedriver are installed
RUN which google-chrome && which chromedriver

# Run the script as a module
CMD ["python", "-m", "src.main"]
