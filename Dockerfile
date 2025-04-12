#FROM python:3.12-slim
#
#WORKDIR /app
#
#RUN pip install poetry
#
#COPY pyproject.toml poetry.lock ./
#RUN poetry config virtualenvs.create false && poetry install --no-root
#
#COPY . /app


FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


RUN pip install poetry


WORKDIR /app


COPY pyproject.toml poetry.lock ./


RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Копируем всё приложение
COPY . /app
