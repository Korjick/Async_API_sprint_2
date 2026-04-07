FROM python:3.14-slim

ARG WORKER_COUNT
ENV WORKER_COUNT=${WORKER_COUNT:-4}

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

WORKDIR /app

RUN chown -R appuser:appuser /app

COPY requirements.txt pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

USER appuser

EXPOSE 8000
CMD ["sh", "-c", "gunicorn content_api.command.app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers ${WORKER_COUNT}"]
