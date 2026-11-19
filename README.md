# keitaro-wrapper

Обёртка над Keitaro. Сейчас здесь только каркас: один эндпоинт и одна страница.

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
