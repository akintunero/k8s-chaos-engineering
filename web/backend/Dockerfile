FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL "https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl

COPY pyproject.toml README.md LICENSE NOTICE /app/
COPY src/ /app/src/
COPY hack/sync-package-data.sh /app/hack/sync-package-data.sh
COPY config/ /app/config/
COPY experiments/ /app/experiments/
COPY web/backend/ /app/web/backend/

RUN chmod +x /app/hack/sync-package-data.sh \
    && /app/hack/sync-package-data.sh \
    && pip install --no-cache-dir -e "/app[web]"

WORKDIR /app/web/backend

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
