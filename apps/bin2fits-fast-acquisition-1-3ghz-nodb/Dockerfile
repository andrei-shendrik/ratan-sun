FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# установка uv
# RUN pip install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY libs/ratanpy libs/ratanpy
COPY apps/bin2fits-fast-acquisition-1-3ghz-nodb apps/bin2fits-fast-acquisition-1-3ghz-nodb

RUN uv sync --no-dev

# add .venv into path
ENV PATH="/app/.venv/bin:$PATH"

# start app script from pyproject.toml
ENTRYPOINT ["bin2fits-fast-1-3-nodb"]

# по дефолту
CMD ["--help"]