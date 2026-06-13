FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev 

WORKDIR /app

RUN pip install uv

ARG UV_GROUPS
COPY pyproject.toml uv.lock ./
RUN echo "GROUPS=$UV_GROUPS"
RUN uv sync --frozen --no-dev $UV_GROUPS

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
