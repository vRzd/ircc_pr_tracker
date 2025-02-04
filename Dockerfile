# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary dependencies for Chrome and Chromedriver
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 \
    libnss3 libxss1 libappindicator3-1 xdg-utils libgbm1 libasound2 \
    && apt-get clean

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee -a /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Extract Chrome version safely
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    echo "Detected Chrome Version: $CHROME_VERSION" && \
    if [ -z "$CHROME_VERSION" ]; then echo "❌ Failed to get Chrome version!" && exit 1; fi && \
    CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    echo "Downloading Chromedriver Version: $CHROMEDRIVER_VERSION" && \
    wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Debug: Verify Chrome & Chromedriver installation
RUN which google-chrome && google-chrome --version
RUN which chromedriver && chromedriver --version

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

# Run the script as a module
CMD ["python", "-m", "src.main"]
