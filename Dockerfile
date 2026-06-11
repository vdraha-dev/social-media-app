FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
