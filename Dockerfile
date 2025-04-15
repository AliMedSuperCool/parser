FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


RUN pip install poetry


WORKDIR /app


COPY pyproject.toml ./


RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Копируем всё приложение
COPY . /app
