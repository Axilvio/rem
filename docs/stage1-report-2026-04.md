# Stage 1 — Работоспособность экосистемы (апрель 2026)

Дата проверки: **2026-04-28**.

## Что работает из коробки
- Remnawave Panel 2.7.x + Node 2.7.0 совместимы, Node требует Panel >=2.7.0.
- Server-Side Routing/Bridge официально задокументирован и работоспособен как схема (RU entry -> DE exit).
- В official backend repo присутствуют production compose-файлы (`docker-compose-prod.yml`, `docker-compose-prod-with-cf.yml`, advanced вариации).
- Python SDK официально мигрировал на пакет `remnawave` (ветка 2.x), async API и pydantic-модели доступны.
- Bedolaga-бот имеет зрелую базу: авто-синхронизация, вебхуки panel->bot, multi-tariff режим.

## Breaking changes / ограничения / риски
- В changelog Panel 2.8.0 (development) есть миграции `userUuid -> userId` и изменения типов в API (`trafficLimitBytes` integer->number), что ломает старые интеграции.
- Документация Server-Side Routing прямо помечена как demonstration-only, не production template.
- Есть жёсткая версия-совместимость Node/Panel.
- В Bedolaga исторически высокая скорость изменений env-переменных; при апдейтах нужен lock версий и regression suite.

## Рекомендации по BEDOLAGA-DEV
- Брать как основу: структуру платежей/синхронизации/админ-workflows.
- Переработать полностью: security hardening webhook-слоя, idempotency storage, строгую типизацию и DI-границы, production observability.
- Зафиксировать контракты API через адаптер над official SDK, чтобы переживать изменения panel API.

## План тестов работоспособности
1. Image pull/smoke: panel/node/postgres/redis/caddy.
2. API smoke: `/api/health`, auth token, users CRUD minimal.
3. SDK smoke: create/get user через official SDK package `remnawave`.
4. Config Profiles: валидация JSON, привязка inbound/squad.
5. Bridge routing: e2e трасса RU->DE, `.ru` direct and non-ru via bridge.
6. Webhook security: HMAC verify, replay/idempotency reject.
7. Payment lifecycle: pending -> paid -> subscription extend.
8. Failover: node health degradation -> auto exclude.

## Минимально необходимое для 100% production-ready
- Канареечные обновления + rollback.
- Полный e2e автотест по сценарию "регистрация -> оплата -> получение конфига -> подключение".
- Полный мониторинг SLI/SLO, алерты, runbook.
- Регулярная ротация ключей Reality/shortId и secrets management.
- DR-план с квартальными restore-репетициями.
