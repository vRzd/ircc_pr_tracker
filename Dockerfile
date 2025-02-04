FROM python:3.8-slim

# Install dependencies needed for our app and to install Google Chrome
RUN apt-get update && apt-get install -y \
    xvfb \
    wget \
    curl \
    unzip \
    gnupg \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Add the Google Chrome repository and install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages including poetry, selenium, and webdriver_manager
RUN pip install --no-cache-dir poetry selenium webdriver_manager

WORKDIR /app

# Copy Poetry configuration files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

# Copy the application source code
COPY src/ src/

CMD ["python", "-m", "src.main"]
