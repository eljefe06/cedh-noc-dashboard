# Stage 1 — build / install deps
FROM python:3.11.10-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install .


# Stage 2 — runtime
FROM python:3.11.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Non-root user
RUN useradd -r -u 1001 -s /sbin/nologin nocapi

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ app/

RUN mkdir -p /data && chown nocapi:nocapi /data

USER nocapi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
