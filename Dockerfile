FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    xvfb \
    wget \
    curl \
    unzip \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry selenium webdriver_manager

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev
COPY src/ src/

CMD ["python", "-m", "src.main"]
