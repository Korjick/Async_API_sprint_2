# Проектная работа 5 спринта

https://github.com/Korjick/Async_API_sprint_2

Сервис выдачи контента онлайн-кинотеатра. Отдаёт данные о фильмах, жанрах и персонах, работает с Elasticsearch и Redis.

## Стек

- Python 3.14, FastAPI
- Elasticsearch — хранилище индексов контента
- Redis — кэш ответов API
- gRPC-клиент Auth — валидация JWT токенов
- OpenTelemetry + Jaeger — распределённые трейсы (HTTP + gRPC)
- structlog — структурированные логи приложения
- Loki + Promtail — сбор и хранение логов контейнеров

## Архитектура

Hexagonal (Ports & Adapters). Слои:

```
src/content_api/internal/
	core/domain/models/      — доменные модели (Film, Genre, Person)
	core/application/        — use cases (queries)
	ports/input/             — входные порты (handler interfaces)
	ports/output/            — выходные порты (repositories, auth verifier)
	adapters/input/http/     — FastAPI роутеры и dependency
	adapters/output/         — Elasticsearch, Redis реализации
	infrastructure/          — настройки, auth gRPC клиент
src/content_api/command/app/ — точка входа приложения
```

## Интеграция с Auth и деградация

- Во всех текущих HTTP-роутах используется `optional_auth_identity`.
- Если `Authorization` не передан, запрос обрабатывается как anonymous.
- Если заголовок `Authorization` некорректный (не `Bearer <token>`), возвращается `401 Unauthorized`.
- Если токен передан, но невалиден, запрос продолжается как anonymous.
- Если Auth недоступен (включая открытый circuit breaker), запрос продолжается как anonymous.

## Запуск

### 1. Настройка окружения

```bash
cd fastapi-solution
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

pip install -r requirements.txt
pip install -e .
```

### 2. Конфигурация

Для локального запуска с хоста:
- скопируйте `fastapi-solution/.env.sample` в `fastapi-solution/.env`

Для запуска в контейнерах (prod/nginx) создайте:
- `fastapi-solution/.env` (скопировать из `fastapi-solution/.env.sample` и изменить хосты на имена сервисов: `redis`, `elasticsearch`, `auth-api`)
- `etl/.env` (можно скопировать из `etl/.env.sample`)

Параметры логирования:
- `LOG_JSON=true|false` — JSON-формат или цветной консольный формат.
- `LOG_LEVEL=INFO|DEBUG|...` — уровень логирования.

Параметры трассировки:
- `OTEL_ENABLED` — включить/выключить экспорт трейсов.
- `OTEL_SERVICE_NAME` — имя сервиса в Jaeger.
- `OTEL_SERVICE_VERSION` — версия сервиса.
- `OTEL_ENVIRONMENT` — окружение (`development`/`production`).
- `OTEL_EXPORTER_OTLP_ENDPOINT` — OTLP endpoint (`http://127.0.0.1:4317` для локального запуска с хоста).
- `OTEL_EXPORTER_OTLP_INSECURE` — отключение TLS для локального окружения.

### 3. Запуск через Docker Compose

Из папки `content_api`:

```bash
docker compose -f docker-compose.dev.yaml up -d
```

Это dev-инфраструктура для локальной разработки:
- Elasticsearch: `http://localhost:9200`
- Redis: `localhost:6379`

Prod (без nginx):

```bash
docker compose -f docker-compose.yaml up -d --build
```

Loki API: `http://localhost:3100`
Jaeger UI: `http://localhost:16686`

Prod + nginx:

```bash
docker compose -f docker-compose.yaml -f docker-compose.nginx.yaml up -d --build
```

### 4. Локальный запуск без Docker

```bash
cd fastapi-solution
uvicorn content_api.command.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger-документация: `http://localhost:8000/api/openapi`

## Тесты

Из `content_api/fastapi-solution`:

```bash
pytest -v
```

Интеграционные тесты используют testcontainers — автоматически поднимают
Elasticsearch и Redis в Docker-контейнерах.

## Логирование и наблюдаемость

- В приложении подключен `structlog`.
- В `RequestContextMiddleware` добавляется контекст запроса:
  `request_id`, `method`, `path`, `client_ip`.
- На каждый запрос пишется событие `request_completed` (или `request_failed` при исключении).
- В `docker-compose.yaml` добавлены `loki` и `promtail`.
- Promtail читает Docker-логи и отправляет их в Loki.
