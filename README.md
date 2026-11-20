# keitaro-wrapper

Обёртка над Keitaro.

- `apps/api` — FastAPI и SQLAlchemy
- `apps/web` — React, Vite, Testing Library

Бизнес-процесс черновика потоков и тест-кейсы по нему: [docs/wrapper.md](docs/wrapper.md).

Создатель кампаний: [docs/campaign-creator.md](docs/campaign-creator.md).

## Что нужно

- Node.js 22 и [pnpm](https://pnpm.io) 12 (`corepack enable` подхватывает версию из `package.json`)
- Python 3.12 или новее
- [uv](https://docs.astral.sh/uv/) — `pnpm deps` вызывает `uvx`
- Docker с Compose. Postgres всегда в контейнере, и локальный запуск, и Docker-стек

Команды ниже запускаются из корня репозитория.

## Настройка

Скопируйте переменные окружения:

```bash
cp .env.example .env
```

В `.env` задаются адрес Keitaro, ключ API, префикс имён кампаний и локальный URL Postgres (`127.0.0.1:54330`). Файл в git не попадает.

Схема базы применяется при старте API. Отдельная команда миграции не нужна.

## Локально

Зависимости API и страницы ставятся один раз. `pnpm dev` вызовет ту же установку сам, если виртуального окружения или `node_modules` ещё нет.

```bash
pnpm deps
pnpm dev
```

`pnpm dev` поднимает Postgres, API с перезагрузкой и страницу Vite. Оба процесса живут, пока команда не остановлена через Ctrl+C. Контейнер Postgres после этого остаётся запущенным.

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Страница: [http://127.0.0.1:5173](http://127.0.0.1:5173)

`GET /health` проверяет, что процесс жив и база принимает запрос. Vite проксирует `/health`, `/offers` и API `/campaigns` на `http://127.0.0.1:8000`.

По отдельности:

```bash
pnpm dev:api
```

Скрипт поднимает Postgres и запускает uvicorn на `127.0.0.1:8000`. Страница из `apps/web`:

```bash
cd apps/web && pnpm dev
```

Остановить Postgres:

```bash
pnpm db:down
```

Порт `8000` занимает один процесс. Пока локальный uvicorn слушает его, контейнер API из раздела ниже не стартует.

## В Docker

Postgres, API и страница одной командой. Перед этим должен существовать `.env`: Compose читает из него `CAMPAIGN_PREFIX` и передаёт файл в контейнер API.

```bash
pnpm start
```

Страница открывается на [http://127.0.0.1:8080](http://127.0.0.1:8080). Nginx отдаёт сборку и проксирует `/health`, `/offers` и API `/campaigns` в контейнер API. Адрес базы внутри сети, URL проверок и `CORS_ORIGINS` берутся из `.env.docker` и перекрывают одноимённые значения из `.env`.

Остановка всего стека, включая Postgres:

```bash
pnpm db:down
```

Только API в контейнере, с тем же Postgres. Контейнер слушает порт `8000` и ходит в базу по имени сервиса `postgres`:

```bash
pnpm api:docker
```

## База

Postgres всегда в Docker, на порту `54330`. Локальный API подключается к опубликованному порту, контейнер API — к сервису `postgres` внутри сети Compose.

```bash
pnpm db:up
pnpm db:down
```

`pnpm db:down` останавливает контейнеры и не удаляет том с данными.

## Тесты

```bash
cd apps/api && .venv/bin/pytest
cd apps/web && pnpm test
```
