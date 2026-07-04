# ==========================================
# BUILDER
# ==========================================
FROM python:3.14-slim AS builder

# путь должен совпадать с путем рантайма
WORKDIR /app

# установка компиляторов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# копирование конфигурации
COPY pyproject.toml uv.lock ./
COPY libs/ratanpy/pyproject.toml libs/ratanpy/
COPY apps/backend/pyproject.toml apps/backend/

# копирование исходников
COPY libs/ratanpy libs/ratanpy
COPY apps/backend apps/backend

ARG DEV_MODE="false"

# сборка зависимостей (создание /app/.venv)
RUN if [ "$DEV_MODE" = "true" ]; then \
        uv sync --package backend; \
    else \
        uv sync --package backend --no-dev; \
    fi

# ==========================================
# RUNTIME
# ==========================================
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

ENV HOME=/tmp

# путь должен совпадать с билдером
WORKDIR /app

# установка рантайм-зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# создание пользователя
# RUN addgroup --system appgroup && adduser --system --ingroup appgroup --home /home/appuser appuser
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -d /app -s /bin/bash appuser

# копирование собранного проекта из билдера
COPY --from=builder --chown=appuser:appgroup /app /app

USER appuser

# установка рабочей директории
# `gunicorn config.wsgi`, `python manage.py`, `celery -A config`
WORKDIR /app/apps/backend/src

# сбор статики
RUN SECRET_KEY='dummy_key_for_build' python manage.py collectstatic --noinput

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

#FROM python:3.14-slim
#
## системные переменные
#ENV PYTHONDONTWRITEBYTECODE=1 \
#    PYTHONUNBUFFERED=1 \
#    UV_SYSTEM_PYTHON=1 \
#    UV_CACHE_DIR=/tmp/.uv-cache
#
## создание пользователя
#RUN addgroup --system appgroup && \
#    adduser --system --ingroup appgroup --home /home/appuser appuser
#
#WORKDIR /app
#RUN chown appuser:appgroup /app
#
## установка uv
#COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
#
## копирование конфигурации
#COPY --chown=appuser:appgroup pyproject.toml uv.lock ./
#COPY --chown=appuser:appgroup libs/ratanpy/pyproject.toml libs/ratanpy/
#COPY --chown=appuser:appgroup apps/backend/pyproject.toml apps/backend/
#
## установка зависимостей
#RUN uv sync --package backend --no-dev --no-cache
#
#ENV PATH="/app/.venv/bin:$PATH"
#
## установка системных библиотек
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \
#    libpq-dev \
#    && rm -rf /var/lib/apt/lists/*
#
## копирование кода
#COPY --chown=appuser:appgroup libs/ratanpy libs/ratanpy
#COPY --chown=appuser:appgroup apps/backend apps/backend
#
## установка рабочей директории
#WORKDIR /app/apps/backend/src
#
## точка входа
#CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]