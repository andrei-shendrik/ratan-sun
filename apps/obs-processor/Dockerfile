FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

# copy dependencies
COPY apps/data-worker/pyproject.toml /app/

COPY libs/ratanpy /libs/ratanpy

RUN uv pip install --system -e .

# copy source code
COPY apps/data-worker /app

# start app script from pyproject.toml
# CMD ["obs-processor"]