# keitaro-wrapper

Обёртка над Keitaro.

- `apps/api` — FastAPI и SQLAlchemy
- `apps/web` — React, Vite, Testing Library

Бизнес-процесс черновика потоков и тест-кейсы по нему: [docs/wrapper.md](docs/wrapper.md).

Создатель кампаний: [docs/campaign-creator.md](docs/campaign-creator.md).

## Запуск

Зависимости API и страницы:

```bash
pnpm deps
```

Postgres, API и страница одной командой:

```bash
pnpm dev
```

API открывается на [http://127.0.0.1:8000](http://127.0.0.1:8000), страница на [http://127.0.0.1:5173](http://127.0.0.1:5173). `GET /health` проверяет, что процесс жив и база принимает запрос.

Postgres, API и страница в Docker:

```bash
pnpm start
```

Страница открывается на [http://127.0.0.1:8080](http://127.0.0.1:8080). Nginx отдаёт сборку и проксирует `/health`, `/offers` и API `/campaigns` в контейнер API. Адрес базы внутри сети, URL проверок, `CORS_ORIGINS` и `CAMPAIGN_PREFIX` берутся из `.env` и `.env.docker`. Остановка — `pnpm db:down`.

## База

Postgres всегда в Docker, на порту `54330`. API подключается к нему и локально, и из контейнера.

```bash
pnpm db:up
pnpm db:down
```

## API локально

```bash
pnpm dev:api
```

Скрипт поднимает Postgres и запускает uvicorn с перезагрузкой.

## API в Docker

```bash
pnpm api:docker
```

Контейнер API слушает тот же порт `8000` и ходит в Postgres по имени сервиса `postgres`. Порт `8000` занимает один процесс: uvicorn на хосте или контейнер API.

## Web

Страница из `pnpm dev` открывается на [http://127.0.0.1:5173](http://127.0.0.1:5173) и показывает ответ `/health`. Vite проксирует этот путь на `http://127.0.0.1:8000`. Отдельно страница запускается из `apps/web` командой `pnpm dev`.

## Тесты

```bash
cd apps/api && .venv/bin/pytest
cd apps/web && pnpm test
```
