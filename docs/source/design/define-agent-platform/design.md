# Design

## Context

Проект новый, кода нет. Мотивация и состав — см. proposal.md, требования — specs/. Верхнеуровневая схема — `architecture.md` в корне проекта.

Принятые решения по стеку: sandbox — Docker с переходом на K8s; харнес — LangGraph; Runner и Control Plane — Go, [Harness](../../../architecture/components/harness/README.md) — Python; память — Postgres + отдельная векторная БД.

## Goals / Non-Goals

**Goals:**
- Агент собирается из конфига Registry без кода.
- Все вызовы LLM — только через LiteLLM.
- Абстракция sandbox, позволяющая сменить Docker на K8s без изменения спек.
- [Guardrails](../../../architecture/components/guardrails/README.md) в 4 точках из одного источника правил.

**Non-Goals:**
- Планирование и выбор агента (это [ICPlan](../../../architecture/components/icplan/README.md)).
- Прямое взаимодействие агентов друг с другом.
- UI в первой итерации (сначала API + CLI).

## Decisions

R&D по каждому решению: [docs/rnd](..\..\..\research\README.md).

### AD-1. Sandbox: тёплый пул + одноразовое использование, Docker за интерфейсом `SandboxProvider`
Runner работает с интерфейсом `create / claim / exec / destroy`; первая реализация — Docker, следующая — K8s Pod. По каждому профилю держится пул из N запущенных sandbox; запуск забирает готовый, после запуска sandbox уничтожается, пул доливается (подход Copilot coding agent, E2B, Daytona).
- Альтернативы: контейнер на запуск без пула (2–10 с старта), контейнер на агента (запуски видят друг друга), контейнер на задачу (ресурсы заняты в простое), microVM (сильнее изоляция, сложнее) — можно добавить как провайдера.
- Ориентиры ресурсов: harness 150–300 МБ RAM, агент-разработчик 0.5–2 ГБ, CPU почти не нужен (ожидание LLM).

### AD-2. Harness: LangGraph (Python) внутри sandbox — подтверждено
Агентский цикл — граф LangGraph: `context → llm → tools → context`. Hooks (G2) реализуются как узлы/обёртки графа до и после `llm` и `tools`. LLM-клиент настроен на endpoint LiteLLM (OpenAI-совместимый API).
- Альтернативы ([R&D v3.1](..\..\..\research\harness-framework.md), 11.10.2026): OpenAI Agents SDK (запасной: пауза через `RunState`, сравнение прототипом в 1.3.9), PydanticAI, Google ADK, Microsoft Agent Framework, Claude Agent SDK (формат Anthropic, CLI в образе), Hermes Agent (готовый агент: заменил бы Runner, [Sandbox](../../../architecture/components/sandbox/README.md), [Memory](../../../architecture/components/memory/README.md), [Guardrails](../../../architecture/components/guardrails/README.md)), свой минимальный цикл (всё писать самим).
- Почему LangGraph: `interrupt` для approve (G2), checkpoint на каждом шаге для возобновления (хранится у Runner в S5, [Harness](../../../architecture/components/harness/README.md) пишет через [I12](../../../architecture/components/harness/integrations/I12.yaml) — [AD-18](../../../architecture/decisions/AD-18.yaml)), стрим шагов для чата запуска. Версию фиксируем, LangGraph держим за своим интерфейсом harness.
- Следствие: скиллы и MCP подключаем сами — MCP через `langchain[mcp]` (`langchain.mcp`; архивный `langchain-mcp-adapters` перенесён туда), скилл = промпт-фрагмент + набор тулов.

### AD-3. Go для Runner, TypeScript для Platform module (в ICPlan), Python для Harness
Go — долгоживущий Runner, конкурентность, работа с Docker/K8s API. [Platform module](../../../architecture/components/platform-module/README.md) — модуль форка [ICPlan](../../../architecture/components/icplan/README.md) на его стеке. Python — экосистема LLM (LangGraph, LiteLLM, MCP).
- Граница: Runner ↔ [Harness](../../../architecture/components/harness/README.md) по gRPC или HTTP + поток событий; [Harness](../../../architecture/components/harness/README.md) — образ контейнера.
- Альтернатива: всё на Python — проще, но слабее для Runner под нагрузкой.

### AD-4. Хранилища
| Данные | Хранилище |
|---|---|
| Определения агентов, версии, данные guardrails, профили | БД [ICPlan](../../../architecture/components/icplan/README.md) (Postgres), [Platform module](../../../architecture/components/platform-module/README.md) — отдельная схема |
| Запуски, статусы, события запуска | БД [ICPlan](../../../architecture/components/icplan/README.md) |
| M1 сессионная, M2 эпизодическая, M3 задачная, M5 процедурная | БД [ICPlan](../../../architecture/components/icplan/README.md) |
| M6 организационная | Документы [ICPlan](../../../architecture/components/icplan/README.md) |
| M4 семантическая (после MVP, вместе с RAG) | pgvector в Postgres [ICPlan](../../../architecture/components/icplan/README.md) |
| Логика guardrails (Rego) | git |

Права и TTL памяти проверяет [Memory](../../../architecture/components/memory/README.md) Service, агенты не ходят в БД напрямую.
- Пересмотрено: Qdrant заменён на pgvector — расширение уже установлено в Postgres [ICPlan](../../../architecture/components/icplan/README.md), меньше компонентов; отдельный движок — по данным нагрузки.

### AD-5. LLM Gateway — LiteLLM Proxy
Алиасы моделей, virtual keys на агента (лимиты, бюджеты), fallback; callbacks в Langfuse — после MVP. G4 — guardrail-хуки LiteLLM (PII-маскирование, модерация, детект injection).

### AD-6. Guardrail Policy
Движок решений G1 и G2 — OPA (Apache 2.0, CNCF): логика (Rego) в git с тестами `opa test`, данные (allowlist, лимиты) в БД [ICPlan](../../../architecture/components/icplan/README.md). Каждая точка G1–G4 включается и выключается в конфиге деплоя (`guardrails.gN.enabled`), режим отказа движка — `on_engine_error: deny | allow`. Точки применения: G1 — проверяет сам Runner; G2 — передаются в [Harness](../../../architecture/components/harness/README.md) при старте; G3 — транслируются в параметры контейнера и egress-прокси; G4 — в конфиг virtual key LiteLLM.

### AD-7. Сеть и секреты (G3)
[Sandbox](../../../architecture/components/sandbox/README.md) в изолированной сети; исходящий трафик только через egress-прокси с allowlist. Секреты подставляет прокси, в контейнер не передаются.

### AD-8. Контракт ICPlan
[Agent Runner](../../../architecture/components/agent-runner/README.md) работает как внешний раннер [ICPlan](../../../architecture/components/icplan/README.md): опрашивает очередь запусков по ключу агента и стримит результат обратно (протокол `@itsaplan/runner`). Прежний вариант `POST /runs` (push) заменён — см. `add-icplan-integration`.

### AD-9. Хранение конфигурации
Источник правды — БД [ICPlan](../../../architecture/components/icplan/README.md); версии определений агента; экспорт/импорт YAML для ревью и переноса между окружениями. Наши настройки — [Platform module](../../../architecture/components/platform-module/README.md) в [ICPlan](../../../architecture/components/icplan/README.md). Альтернатива (Config Repo в git, проект AI-агент) отклонена: два источника правды и синхронизация с UI.

### AD-10. MCP или прямой вызов
Гибрид по правилам R1–R7: решает модель — тул; тул для нескольких агентов или с секретом — MCP; детерминированное, пакетное и внутреннее — прямой вызов; админ-функции — отдельные MCP по уровню доверия. Агент ходит к MCP-серверам только через MCP-прокси Runner ([AD-19](../../../architecture/decisions/AD-19.yaml)).

| # | Правило | Как |
|---|---|---|
| R1 | Последовательность известна заранее (детерминированно) | прямой вызов (REST / gRPC / SDK) |
| R2 | Следующий шаг решает модель | тул агента |
| R3 | Тул нужен нескольким агентам или держит секрет вне агента | MCP-сервер |
| R4 | Тул один, стабильный, только внутри [Harness](../../../architecture/components/harness/README.md) | нативный тул [Harness](../../../architecture/components/harness/README.md) |
| R5 | Пакетные и массовые операции | прямой вызов (MCP медленнее и дороже по токенам) |
| R6 | Админ-функции | отдельные MCP-серверы по уровню доверия, рабочим агентам недоступны |
| R7 | Внутренности платформы: Runner ↔ [ICPlan](../../../architecture/components/icplan/README.md), [Harness](../../../architecture/components/harness/README.md) ↔ LiteLLM, проверки G1–G4, автозапись M1, M2 | только прямой вызов |

### AD-11. Рабочие данные
Workspace эфемерный; код — ветка `agent/<KEY>` + PR; документы и артефакты — в задачу [ICPlan](../../../architecture/components/icplan/README.md) (RustFS, S3 API); M2/M3 — БД. Доступ к репозиториям — allowlist агента и короткоживущий токен на запуск через прокси. Общая папка на хосте (проект AI-агент) отклонена: изоляция и масштабирование.

### AD-12. Observability
MVP — таблица событий запуска в БД [ICPlan](../../../architecture/components/icplan/README.md) → чат запуска в задаче. Langfuse — после MVP (тяжёлый self-host: Postgres + ClickHouse + Redis + S3). Prometheus / Grafana / Loki — в бэклоге.

### AD-14. Очередь и планирование запусков
Альтернативы ([R&D v3.1](..\..\..\research\runner-and-scheduling.md), 11.10.2026): Hatchet (ключи параллельности CEL — вторая очередь и новый сервис), River Pro (лимиты по аргументам — платно), Temporal (кластер), Kueue (квоты ресурсов — на этапе 4, лимит модели остаётся у нас).
Очередь запусков — в [ICPlan](../../../architecture/components/icplan/README.md); [Agent Runner](../../../architecture/components/agent-runner/README.md) забирает запуски и решает, когда стартовать, планировщиком со слотами (вариант B): запуск стартует, только когда свободны все его слоты — глобальный (`global_max`), агента (`parallel`, `max`), модели (`models.<alias>.max`), задачи (`per_issue: 1`). Режим `scheduling.mode: sequential | parallel` переключает всю платформу. Порядок `fifo | priority`. Несколько экземпляров Runner делят слоты через блокировку в Postgres. Сравнение вариантов A/B/C — [R&D](..\..\..\research\runner-and-scheduling.md).

### AD-15. Развёртывание и инфраструктура
k3s на одном узле; namespaces `itsaplan-core`, `itsaplan-data`, `itsaplan-agents`, `itsaplan-platform`; Helm-чарты с `existingSecret`; Traefik (в k3s) — ingress и TLS, админки без ingress; Service — балансировка по репликам; PostgreSQL 17 + pgvector под CloudNativePG с пулером PgBouncer (transaction); RustFS (S3) для вложений и копий; бэкап вне узла; NetworkPolicy по списку интерфейсов. Локально — compose (этапы 1–2) и k3d. Отклонены: ingress-nginx и MinIO (архивированы). R&D: [Kubernetes](..\..\..\research\kubernetes-runtime.md), [ingress](..\..\..\research\ingress-and-balancing.md), [СУБД](..\..\..\research\data-stores.md).

### AD-16. Профиль нагрузки
Базовые гипотезы: 15 одновременных пользователей, ~20 RPS на API [ICPlan](../../../architecture/components/icplan/README.md) (p95 < 300 мс), до 6 запусков в очереди и 4 активных, ~1 RPS и ~55 тыс. токенов/мин к LiteLLM; узел 8 vCPU / 32 ГБ / 400 ГБ. Подтверждаются нагрузочным тестом (задача 4.8). R&D: [профиль нагрузки](..\..\..\research\load-profile.md).

### AD-13. RAG
Не в MVP: документы — через `get_document`, код — агентный поиск. RAG (pgvector + локальный эмбеддер) — механизм чтения M4/M6, вводится по мере роста корпуса.

## Risks / Trade-offs

- [Тёплый пул постоянно занимает ресурсы] → размер пула — параметр профиля, 1–2 на старте.
- [LangGraph не даёт готовых skills/hooks] → тонкий собственный слой поверх графа, покрыть тестами.
- [Два языка] → чёткий контракт Runner↔[Harness](../../../architecture/components/harness/README.md) (proto/OpenAPI), контрактные тесты.
- [Модуль в форке [ICPlan](../../../architecture/components/icplan/README.md) расходится с upstream] → отдельная схема БД и отдельный модуль кода.
- [LiteLLM как единая точка отказа] → несколько реплик, health-check.
- [Hooks в [Harness](../../../architecture/components/harness/README.md) можно обойти при компрометации sandbox] → критичные проверки дублируются в G3/G4.

## Migration Plan

Не применимо — новый проект. Переход Docker → K8s: новая реализация `SandboxProvider`, переключение конфигом.

## Open Questions

- Формат событий для [ICPlan](../../../architecture/components/icplan/README.md) (webhook или брокер) — уточняется при интеграции, на спеки не влияет.
- Конкретный движок human approval (G2) — UI/мессенджер — решается при появлении UI.

### AD-17. Управление ходом задачи пользователем и агентом

Закрыты открытые вопросы историй [ICPlan](../../../architecture/components/icplan/README.md) (проверено по коду [ICPlan](../../../architecture/components/icplan/README.md) и аналогам, [R&D потоков](..\..\..\research\us-analogs-agent-tracker.md)):

| Вопрос | Решение | Основание |
|---|---|---|
| Вердикт по результату | «принято» → переход при успехе; «не выполнено» с обязательной заметкой → новый запуск того же шага, учёт в лимите шага ([FR-200](../../../architecture/components/icplan/prd.md)) | Copilot: итерация комментариями на той же работе |
| Проверка со мной | настройка шага `require_review` и флаг задачи `review_with_me`; задача ждёт вердикта, без ответа — напоминания ([FR-199](../../../architecture/components/icplan/prd.md)) | Jira + Rovo: ревью перед передачей; Devin: двигает человек |
| Остановка процесса | флаг `process_paused`: отмена запуска, шаги не срабатывают, ручные переводы разрешены ([FR-201](../../../architecture/components/icplan/prd.md)); отмену Runner узнаёт по ответу heartbeat [ICPlan](../../../architecture/components/icplan/README.md) (`false` для не-`pending`) | Linear «stop», Copilot «Stop session»; код `heartbeatRun` |
| Повтор шага | новый запуск того же шага; «начать с шага N» = обычный вход; сверх лимита — только владелец ([FR-202](../../../architecture/components/icplan/prd.md)) | лимит шага [FR-197](../../../architecture/components/icplan/prd.md) |
| Версии процесса | изменения для новых переходов; удаление шага с задачами требует переноса ([FR-203](../../../architecture/components/icplan/prd.md)) | Jira: сопоставление статусов при публикации workflow |
| Указания во время работы | сообщение к активному запуску по задаче, доставка в ответе heartbeat, [Harness](../../../architecture/components/harness/README.md) учитывает на следующем шаге ([FR-10](../../../architecture/components/icplan/prd.md), [FR-28](../../../architecture/components/harness/prd.md)) | Linear «prompted» в той же сессии; канал чата [ICPlan](../../../architecture/components/icplan/README.md) |
| Выключение агента | `agent.enabled` в форке [ICPlan](../../../architecture/components/icplan/README.md): запуски не создаются и не выдаются, очередь ждёт, активные — по выбору ([FR-11](../../../architecture/components/icplan/prd.md)) | в [ICPlan](../../../architecture/components/icplan/README.md) флага нет (`ai_agent`) |
| Тестовый запуск | чат с агентом (тред агент × пользователь без задачи), изменения задач — с подтверждением, mock-модель ([FR-12](../../../architecture/components/icplan/prd.md)) | `agent_chat_thread`, канал `/agent-chats/*` |
| Сводка и статистика | из `agent_run` (статус, время, токены), событий и затрат LiteLLM ([FR-152](../../../architecture/components/observability/prd.md)) | поля `agent_run` |

Задачи: [3.7](..\..\tasks\3.7-icplan-task-control.md), [3.8](..\..\tasks\3.8-agent-chat-control.md), [3.9](..\..\tasks\3.9-agent-summary-stats.md).

### AD-18. Закрытие открытых вопросов спек

Все открытые вопросы (❓ и 📌) решены агентом по коду [ICPlan](../../../architecture/components/icplan/README.md), документации и R&D; решения 📌 вынесены владельцу продукта на подтверждение (`approvals.md`, роль «Владелец продукта»).

| Вопрос | Решение | Основание |
|---|---|---|
| AGPL-3.0 доработок [ICPlan](../../../architecture/components/icplan/README.md) | доработки форка [ICPlan](../../../architecture/components/icplan/README.md), включая [Platform module](../../../architecture/components/platform-module/README.md) (модуль внутри форка, [AD-3](../../../architecture/decisions/AD-3.yaml)), публикуются в открытом репозитории форка; сервисы платформы ([Agent Runner](../../../architecture/components/agent-runner/README.md), [Harness](../../../architecture/components/harness/README.md), [Memory](../../../architecture/components/memory/README.md) API, конфигурация и образы sandbox) — отдельные программы, связь с [ICPlan](../../../architecture/components/icplan/README.md) только по сети и API, **код закрыт** (решение владельца продукта 11.10.2026) | лицензия [ICPlan](../../../architecture/components/icplan/README.md) распространяется на форк, но не на отдельные программы, общающиеся по сети |
| Доступ [Harness](../../../architecture/components/harness/README.md) к checkpoint | только через API Runner ([I12](../../../architecture/components/harness/integrations/I12.yaml)); учётных данных БД в sandbox нет | sandbox — недоверенная среда |
| Протокол Runner ↔ [Harness](../../../architecture/components/harness/README.md) | HTTP + NDJSON ([I7](../../../architecture/components/agent-runner/integrations/I7.yaml)) | проще gRPC, тот же стиль, что протокол [ICPlan](../../../architecture/components/icplan/README.md) |
| Язык Runner | Go | [AD-8](../../../architecture/decisions/AD-8.yaml), один бинарник, низкое потребление |
| Формат критериев приёмки | чек-лист «Критерии приёмки» в задаче [ICPlan](../../../architecture/components/icplan/README.md) (`issue_checklist`), у пункта — происхождение (процесс, человек, агент); источники и подтверждение — [AD-20](../../../architecture/decisions/AD-20.yaml) | в [ICPlan](../../../architecture/components/icplan/README.md) есть чек-листы задач |
| Версии | LangGraph 1.2.14, `langchain` 1.4.4 с extra `mcp` (fastmcp ≥ 4.0.11; `langchain-mcp-adapters` в архиве), LiteLLM v1.104.2, OPA v1.21.1 | PyPI и релизы GitHub на 10.10.2026 |
| Запись M2 | M2 = `agent_run` [ICPlan](../../../architecture/components/icplan/README.md): пишет [ICPlan](../../../architecture/components/icplan/README.md) по итогу Runner (`/agent-runs/{id}/result`) и вердикту; [Memory](../../../architecture/components/memory/README.md) API только читает | протокол раннера [ICPlan](../../../architecture/components/icplan/README.md) |
| Где M3 | БД [ICPlan](../../../architecture/components/icplan/README.md), таблица M3 (S4); схема — `memory`, владелец [Memory](../../../architecture/components/memory/README.md) API (уточнено [AD-22](../../../architecture/decisions/AD-22.yaml), было `platform`) | одна БД, бэкап вместе с S1 |
| Граница Registry и [Platform module](../../../architecture/components/platform-module/README.md) | Registry = сущности агента [ICPlan](../../../architecture/components/icplan/README.md) (модель, инструкция, тулы, навыки, MCP, проекты, версия); [Platform module](../../../architecture/components/platform-module/README.md) — бюджеты, профили, данные guardrails, автономия, политика доступа | [AD-9](../../../architecture/decisions/AD-9.yaml) |
| Голодание при `order: priority` | старение приоритета: +1 уровень за каждые `scheduling.aging_s` (600 с) ожидания | стандартная техника планировщиков |
| Рабочее пространство (ОВ-WS-1…5) | вариант B; каталог проекта в [Platform module](../../../architecture/components/platform-module/README.md); при смене шага — `read` на workspace задачи, `write` — своя подпапка; ограничение токенами Runner и MCP-серверами (промпт права не расширяет); шаблоны политики по ролям агентов с ручной правкой | [R&D](..\..\..\research\agent-workspace.md): B = 87 |
| Docker-сокет у Runner | этапы 1–3: rootless Docker, Runner под отдельным пользователем; этап 4 — Kubernetes API с ServiceAccount только на `itsaplan-agents` ([I23](../../../architecture/components/agent-runner/integrations/I23.yaml)) | изоляция хоста |
| Egress-прокси | Squid (allowlist доменов по CONNECT, без расшифровки TLS); mitmproxy отклонён | меньше рисков, зрелость |
| mTLS | этапы 1–3 без mTLS: один узел, NetworkPolicy, сервисные токены; mTLS — этап 4 при нескольких узлах (бэклог) | риск принят для одного узла |
| Латентность OPA | OPA на том же узле, p95 решения ≤ 20 мс; кэш решения на запуск для одинакового входа `opa.cache_ttl_s` 60 с; таймаут 200 мс — аварийный | локальная оценка Rego — миллисекунды |
| Калибровка порогов | значения по умолчанию обоснованы в таблицах параметров; калибровка по статистике (3.9) и нагрузочному тесту (4.8) | таблицы параметров |
| LiteLLM и общий Postgres | LiteLLM — 2 реплики; Postgres — один экземпляр на этапах 1–3 с непрерывным архивом WAL и копиями вне узла (RPO — минуты), HA — этап 4 | риск принят, восстановление по 4.7 |
| Маскирование | список шаблонов в `observability/interfaces.md` | типовые форматы секретов |
| Детализация событий | «всё» по умолчанию: промпты, ответы, размышления, вызовы и вывод тулов; маскирование секретов и персональных данных до записи | решение владельца продукта 11.10.2026: разбор каждого запуска; объём ~250 МБ/день |
| Цифры нагрузки | профиль-гипотеза принят проектным; подтверждение — нагрузочный тест 4.8 до выпуска | R&D профиля нагрузки |
| Облако или свой сервер; копии вне узла | свой сервер (1 узел k3s, 8 vCPU, 32 ГБ); копии — внешнее S3-совместимое хранилище на другой площадке | [AD-15](../../../architecture/decisions/AD-15.yaml), стоимость |
| Образ Postgres с pgvector | стандартный образ CloudNativePG (pgvector в комплекте); проверка `CREATE EXTENSION vector` в 4.7 | документация CNPG |
| PgBouncer transaction | [ICPlan](../../../architecture/components/icplan/README.md) совместим (`postgres-js` с `prepare: false`); LiteLLM — Prisma с `pgbouncer=true`; миграции — прямым подключением | код [ICPlan](../../../architecture/components/icplan/README.md), документация Prisma |
| Слияние с upstream [ICPlan](../../../architecture/components/icplan/README.md) | доработки — отдельными модулями и миграциями с префиксом, за флагами; общие исправления — PR в upstream | поддержка форка |
| Параметр автономии | `autonomy_level` в таблице guardrails и control-plane | — |

### AD-19. Проверка тулов вне sandbox и зависимости проекта

Закрывает вопросы Q-MCP-01 и Q-SBX-01 по исследованию ([R&D MCP](..\..\..\research\mcp-vs-direct.md), [R&D рабочего пространства](..\..\..\research\agent-workspace.md)).

| Вопрос | Решение | Почему |
|---|---|---|
| Где проверять allowlist тулов и G2 для MCP | **MCP-прокси [Agent Runner](../../../architecture/components/agent-runner/README.md)**: [Harness](../../../architecture/components/harness/README.md) ходит к MCP только через Runner (`/runs/:id/mcp/:server`, [I9](../../../architecture/components/harness/integrations/I9.yaml)); Runner фильтрует `tools/list` и проверяет `tools/call` по allowlist манифеста запуска, вызывает G2 в OPA ([I10](../../../architecture/components/harness/integrations/I10.yaml)) и подставляет учётные данные сервера из Secret. [Sandbox](../../../architecture/components/sandbox/README.md) к MCP-серверам напрямую не ходит; egress-прокси ключ агента к MCP не подставляет | проверка вне недоверенной среды; у Runner уже есть манифест, токен запуска, подтверждения и клиент OPA; нового сервиса нет; MCP ~1 RPS; официальный MCP SDK для Go (v1.8.0). Шлюзы (ContextForge, agentgateway) потребовали бы настройки на каждый запуск и нового сервиса |
| Как агенту ставить зависимости проекта | **Шаг подготовки**: до старта агента Runner выполняет `setup.script` проекта в контейнере подготовки в сети `sbx-setup`, где Squid пускает к `setup.registries`; результат кэшируется по хешу lock-файлов (`setup.cache_ttl_h`) и подключается в `/workspace/.deps`. Во время работы — нативный тул `install_dependencies`: Runner повторяет шаг. Среда агента к реестрам не ходит; секреты приватных реестров — только в шаге подготовки | как Codex (скрипт подготовки, секреты только в нём) и Copilot (шаги подготовки вне firewall агента); Squid умеет списки доменов по подсети источника; канал утечки через реестры закрыт |
| Этап 1 (без Runner) | [Harness](../../../architecture/components/harness/README.md) подключается к MCP напрямую только в разработке (CLI, mock) | Runner появляется на этапе 2 |

### AD-20. Контракт шага: данные, память, критерии приёмки

Решено по исследованию ([R&D контракта шага](..\..\..\research\step-contract.md)) по поручению владельца продукта 11.10.2026.

| Вопрос | Решение | Почему |
|---|---|---|
| Что шаг получает и отдаёт | вход: задание, критерии с происхождением, передача предыдущего шага (M3: сделано, дальше, ссылки на артефакты, вопросы, предложенные критерии), M2; выход: итог, артефакты в своей подпапке, передача. Не передаются: M0, промпты, вывод тулов — они в событиях запуска | ссылки вместо содержимого (Anthropic), фильтр передачи (OpenAI Agents SDK) |
| Кто задаёт критерии | процесс («результат шага», «готовность шага»), человек (чек-лист задачи), предыдущий агент (предлагает в передаче), ревьюер (добавляет при возврате); порядок при конфликте: человек > процесс > агент | готовность шага — DoD, `expected_output` (CrewAI); задание исполнителю (Anthropic); Kiro, Spec Kit |
| Противоречие критериев двух людей (уточнение 11.10.2026 по [проверке двумя читателями](..\..\reviews\2026-10-11-dual-read.md)) | агент не выбирает сам: задаёт вопрос (`CUSTOM` `question`) исполнителю задачи, шаг ждёт ответа; ответ — пояснение к критериям | порядок «человек > процесс > агент» не различает двух людей; выбор агентом подогнал бы проверку |
| Кто проверяет | не исполнитель: gate [Harness](../../../architecture/components/harness/README.md) (формат — кодом, смысл — судья по рубрике), шаг-ревью агентом или человеком; исполнитель не меняет критерии своего шага | разделение обязанностей; судья по рубрике (Anthropic) |
| Подтверждение критериев агента | настройка шага `criteria_approval`: `auto` (по умолчанию: действуют сразу; человек подтверждает при проверке на шаге, флаге «проверять со мной» или автономии автора R0–R1), `review`, `always`; агент только добавляет критерии | разбор 10 сценариев: ни один «чистый» вариант не закрывает все |
| Доступ к данным | read — папка и ветка задачи; write — своя подпапка шага; M3 пишет агент текущего шага | [AD-18](../../../architecture/decisions/AD-18.yaml), конфликты К1, К6 |

### AD-21. Чат запуска в задаче на протоколе AG-UI

Решено по исследованию ([R&D вида работы агента](..\..\..\research\run-view.md)) по замечанию владельца продукта 11.10.2026.

| Вопрос | Решение | Почему |
|---|---|---|
| Что видит пользователь | панель «Агент» в задаче: реплики агента о намерении, свёрнутые рассуждения модели (если провайдер отдаёт), шаги цикла и вызовы тулов, план «сделано / дальше», вопросы и подтверждения с кнопками, указания пользователя, карточка итога (критерии ✓ / ✗, артефакты, токены, вердикт шага); все запуски задачи — одна лента по шагам процесса | замечание владельца; Linear (thought, elicitation, response), журнал сессии Copilot |
| Формат событий | события AG-UI (`RUN_*`, `STEP_*`, `TEXT_MESSAGE_*`, `REASONING_*`, `TOOL_CALL_*`, `ACTIVITY_SNAPSHOT`); события платформы — `CUSTOM` (`question`, `approval_request`, `guardrail_decision`, `memory_write`, `llm_call`) | форк уже принимает AG-UI в чате с агентом и рисует его `AgentChatPanel` — один протокол и экран |
| Доставка | [Harness](../../../architecture/components/harness/README.md) → Runner ([I7](../../../architecture/components/agent-runner/integrations/I7.yaml), NDJSON) → `POST /agent-runs/:runId/events` ([I2](../../../architecture/components/agent-runner/integrations/I2.yaml)) → S3 → `GET /agent-runs/:runId/stream` (SSE) → web | как чат форка (`/agent-chats/:id/events` → `/chat/:id/stream`) |
| Хранение | событие целиком; дельты `*_CONTENT` собираются в сообщение на `*_END`, по отдельности идут только в SSE | объём при `events.level: всё` |
| Рассуждения | основа — реплика агента перед действием (правило промпта); `reasoning_content` LiteLLM — свёрнутым блоком, маскируется как промпт | рассуждения есть не у всех моделей и часто это сводка |

### AD-22. Базы, схемы и роли БД сервисов

Решено по исследованию ([R&D: базы, схемы и роли](..\..\..\research\db-roles-schemas.md)), уточняет [AD-4](../../../architecture/decisions/AD-4.yaml) и [AD-18](../../../architecture/decisions/AD-18.yaml).

| Схема | База | Владелец (роль БД) | Что хранит |
|---|---|---|---|
| `public` | `itsaplan` | api [ICPlan](../../../architecture/components/icplan/README.md) (`itsaplan`) | таблицы форка, процесс задачи |
| `platform` | `itsaplan` | api [ICPlan](../../../architecture/components/icplan/README.md) (`itsaplan`): [Platform module](../../../architecture/components/platform-module/README.md), [Observability](../../../architecture/components/observability/README.md) | настройки агентов, профили, доступы, события запуска |
| `runner`, `harness_ckpt` | `itsaplan` | [Agent Runner](../../../architecture/components/agent-runner/README.md) (`runner`) | слоты, кэш подготовки, checkpoint цикла |
| `memory` | `itsaplan` | [Memory](../../../architecture/components/memory/README.md) API (`memory`) | M3, позже M4 |
| `public` | `litellm` | LiteLLM (`litellm`) | ключи, бюджеты, журнал затрат |

Роль сервиса — владелец своей схемы и своих миграций; чужие таблицы — только явным `GRANT` ([Memory](../../../architecture/components/memory/README.md) — чтение `agent_run`, `agent_chat_message`, `issue_activity` (уточнено [AD-25](../../../architecture/decisions/AD-25.yaml)); api — чтение журнала затрат ролью `litellm_read`). Роли — managed roles CloudNativePG. Сервису нужно писать в чужую схему — признак ошибки границы компонента: сначала решение.

### AD-23. Определение агента для запуска — через API Platform module

Решено по исследованию ([R&D: откуда Agent Runner берёт определение агента](..\..\..\research\runner-agent-definition.md)), закрывает Z-ICP-3.

| Вопрос | Решение | Почему |
|---|---|---|
| Через какой стык Runner получает определение | [I4](../../../architecture/components/agent-runner/integrations/I4.yaml): `GET /platform/runs/:runId/agent` → `{version, definition: AgentDefinition, settings: AgentSettings}`; определение в формате `agent/v1` экспорта ([FR-56](../../../architecture/components/platform-module/prd.md)). Claim форка ([I1](../../../architecture/components/agent-runner/integrations/I1.yaml)) не меняется | [Platform module](../../../architecture/components/platform-module/README.md) уже владеет единой версией и снимком (`agent_settings_version`) и читает таблицы Registry той же ролью `itsaplan` ([AD-3](../../../architecture/decisions/AD-3.yaml), [AD-22](../../../architecture/decisions/AD-22.yaml)); код форка вне нашего модуля не меняется ([AD-18](../../../architecture/decisions/AD-18.yaml)) |
| Как закрепляется версия | версию задаёт задача ([FR-55](../../../architecture/components/platform-module/prd.md)) или [Platform module](../../../architecture/components/platform-module/README.md) при первом вызове пишет её в `agent_run.agent_version`; повторный вызов отдаёт ту же версию. Вызов — при старте после слотов планировщика ([FR-97](../../../architecture/components/platform-module/prd.md)) | запуск, ждущий слота, стартует с новыми настройками; продолжение с checkpoint — по той же инструкции |
| Что видит токен Runner | только запуск в `pending` агента `kind = external`, иначе 404; версии нет — 409 ([FR-55](../../../architecture/components/platform-module/prd.md)); секретов в `agent/v1` нет ([FR-99](../../../architecture/components/platform-module/prd.md)) | Runner получает только своё |
| Когда появляется | эндпоинт и сервисный токен — минимальный [Platform module](../../../architecture/components/platform-module/README.md) в задаче 2.3; настройки до 4.4 — значения по умолчанию и YAML | определение нужно на этапе 2 |
| Модель и MCP внешнего агента | модель — алиас LiteLLM в `ai_agent.model` (Registry, [FR-54](../../../architecture/components/platform-module/prd.md), [AD-18](../../../architecture/decisions/AD-18.yaml)); MCP-серверы — `project_resource` (`mcp`) и `access_policy` [Platform module](../../../architecture/components/platform-module/README.md), подтвердить в 2.3 | у внешнего агента форка модель и тулы пусты; MCP-серверов агента в форке нет |

Пересмотр — если [Platform module](../../../architecture/components/platform-module/README.md) вынесут из api [ICPlan](../../../architecture/components/icplan/README.md) в свой сервис (риск [AD-22](../../../architecture/decisions/AD-22.yaml)): тогда он читает Registry через API [ICPlan](../../../architecture/components/icplan/README.md).

### AD-24. Экраны настроек Platform module

Решено по исследованию ([R&D: где администратор задаёт настройки Platform module](..\..\..\research\platform-module-screens.md)), закрывает ОВ-control-plane-1 и Z-ICP-19.

| Уровень | Экран [ICPlan](../../../architecture/components/icplan/README.md) | Права | Эндпоинты [Platform module](../../../architecture/components/platform-module/README.md) ([I20](../../../architecture/components/icplan/integrations/I20.yaml)) |
|---|---|---|---|
| агент | карточка агента → раздел «Платформа» | ресурс `ai_agents` форка (чтение и `edit`) | `/platform/agents/:agentId/settings`, история и откат версий, экспорт и импорт, kill switch `agent:<id>` |
| проект | Проект → ИИ-команда → «Платформа» | ресурс `ai_agents` форка в разделе проекта | `/platform/projects/:projectKey/guidance`, `/budget`, `/access`, ресурсы проекта и шаг подготовки |
| экземпляр | God mode → «Платформа», через точку расширения `@/cloud` | владелец экземпляра | профили среды и памяти, kill switch `platform`, `GET /platform/audit` (чтение — и Безопасность) |

Своей консоли нет. Правки файлов форка — стек карточки (`TeamAiAgentFields.tsx`), `settingsSections.ts` и сообщения; PR в upstream с точкой расширения разделов карточки и проекта через `@/cloud`. Карточка внешнего агента показывает поля Registry (модель-алиас, навыки, тулы, MCP; [FR-54](../../../architecture/components/platform-module/prd.md), [AD-23](../../../architecture/decisions/AD-23.yaml)). Kill switch есть и в API для эксплуатации ([US-GRD-04](../../../architecture/components/guardrails/stories/us-grd-04.yaml)). Пересмотр — если глобальные настройки должны править не только владельцы экземпляра (раздел рабочего пространства) или upstream не примет точки расширения.

### AD-25. Срок хранения запусков, переписки и истории задачи

Решено по исследованию ([R&D: срок хранения в таблицах форка](..\..\..\research\fork-run-retention.md)), закрывает ОВ-icplan-integration-1 и Z-ICP-16; уточняет [FR-43](../../../architecture/components/memory/prd.md).

| Данные | Срок | Кто удаляет |
|---|---|---|
| M1, M2 в таблицах форка (`agent_chat_message`, `agent_run`, `issue_activity`) для памяти | `retention` профиля памяти — фильтр чтения [Memory](../../../architecture/components/memory/README.md) API: старше срока не отдаются | никто: [Memory](../../../architecture/components/memory/README.md) только читает (`SELECT`) |
| `agent_run` (завершённые, по `finished_at`) | `runs.retention_days` ≥ 365 (верхняя граница M2 и `retention_days` событий) | [ICPlan](../../../architecture/components/icplan/README.md), задача worker форка; запуски, у которых ещё есть `run_event`, пропускаются |
| `agent_chat_thread` (тред целиком по `updated_at`) → сообщения и события каскадом | `chat.retention_days` ≥ 90 (верхняя граница M1) | [ICPlan](../../../architecture/components/icplan/README.md), задача worker форка |
| `issue_activity` | без очистки по времени: журнал задачи живёт с задачей | каскад форка |
| M3, позже M4 | `retention` профиля | [Memory](../../../architecture/components/memory/README.md) API, `POST /retention/run` → `{deleted: {m3}}` |

Очистка — по образцу `cleanupOldDeliveries` worker форка, параметры через env, 0 — не чистить. Пересмотр — если требования к персональным данным запретят хранить переписку дольше M1 (тогда `chat.retention_days` = M1 профиля) или поднимут верхние границы `retention` либо `retention_days`.

### AD-26. Уточнения по замечаниям ролей ICPlan (без отдельного R&D — по фактам кода форка и решениям AD-9, AD-20, AD-23)

| Вопрос | Решение | Основание |
|---|---|---|
| Формат навыка (ОВ-agent-registry-1) | Anthropic Agent Skill: `SKILL.md` с frontmatter `name`, `description`, справочные файлы, без исполняемых скриптов | так в форке: `apps/api/src/modules/agents/skills/skill-format.ts` |
| Каталог для валидатора определения (ОВ-agent-registry-3) | офлайн-валидатор (задача 1.2) проверяет схему `agent/v1` и внутренние ссылки файла; ссылки на ресурсы (навыки, тулы, MCP, профили) проверяет импорт [Platform module](../../../architecture/components/platform-module/README.md) `POST /platform/agents/import` по БД | один источник каталога — БД ([AD-9](../../../architecture/decisions/AD-9.yaml)) |
| Где YAML дополнений до [Platform module](../../../architecture/components/platform-module/README.md) (ОВ-agent-registry-4) | отдельного файла нет: дополнения — настройки [Platform module](../../../architecture/components/platform-module/README.md) (`agent_settings`), загрузка YAML — тот же импорт; минимальный [Platform module](../../../architecture/components/platform-module/README.md) — в задаче 2.3 ([AD-23](../../../architecture/decisions/AD-23.yaml)) | [AD-23](../../../architecture/decisions/AD-23.yaml) |
| Кто вправе подтверждать действие агента (ОВ-icplan-integration-2) | право `work_items.edit` в проекте задачи (роли форка); уведомление — исполнителю задачи, без исполнителя — участникам с этим правом | права форка: `packages/db/src/permissions.ts` |
| Как `criteriaNext` попадает в [ICPlan](../../../architecture/components/icplan/README.md) (ОВ-icplan-integration-3) | поле `RunResult.criteriaNext: Criterion[]` (доработка): Runner берёт его из итога [Harness](../../../architecture/components/harness/README.md); [ICPlan](../../../architecture/components/icplan/README.md) при приёме итога создаёт пункты чек-листа с `origin = agent:<username>` и статусом по `criteriaApproval` шага | [AD-20](../../../architecture/decisions/AD-20.yaml) |
| Где отклоняется вызов модели без `run_id` ([FR-136](../../../architecture/components/llm-gateway/prd.md)) | pre-call хук LiteLLM вместе с G4 — задача 4.5; задача 3.5 только суммирует затраты по `run_id` | [AD-5](../../../architecture/decisions/AD-5.yaml), хуки LiteLLM |
| Новая версия определения при правке через `PATCH` форка | [Platform module](../../../architecture/components/platform-module/README.md) при вызове [I4](../../../architecture/components/agent-runner/integrations/I4.yaml) сравнивает хеш определения [ICPlan](../../../architecture/components/icplan/README.md) с последней версией и при отличии создаёт новую версию (`agent_settings_version.data` — снимок определения и настроек) | [AD-23](../../../architecture/decisions/AD-23.yaml) |

**Подтверждения владельца продукта (👤, 11.10.2026):** [AD-18](../../../architecture/decisions/AD-18.yaml) — лицензия (форк [ICPlan](../../../architecture/components/icplan/README.md) с [Platform module](../../../architecture/components/platform-module/README.md) открыт; сервисы платформы — закрытый код), один сервер с копиями вне площадки, риски без HA и mTLS на этапах 1–3, профиль нагрузки, журнал событий «всё»; [AD-19](../../../architecture/decisions/AD-19.yaml), [AD-20](../../../architecture/decisions/AD-20.yaml) и [AD-21](../../../architecture/decisions/AD-21.yaml) — выбор по результатам R&D поручен агенту, ревьюер добавляет критерии с пометкой происхождения.


### AD-27. Цепочки агентов: граф процесса, возвраты с причинами, лимиты, бюджет задачи, обучение через предложения

Решено по исследованию ([R&D: цепочка агентов в трекере](..\..\..\research\agent-chain.md), Э9), решение принято 14.10.2026 по результату анализа (выбор поручен агенту владельцем продукта).

| Вопрос | Решение | Альтернативы и почему не они | Сила опоры |
|---|---|---|---|
| Маршрут | детерминированный граф процесса трекера ([AD-17](../../../architecture/decisions/AD-17.yaml)), роли в шагах произвольные; агент маршрут не выбирает, меняет колонку только [ICPlan](../../../architecture/components/icplan/README.md); режим «супервизор» — не основной | супервизор выбирает исполнителя сам: усиление ошибок (Google 2512.08296), ответственность размыта | сильная для проблемы, средняя для выбора |
| Возвраты | `ProcessStep.transitions[{reason, to}]`; исход шага агент выбирает только из разрешённых переходов (`RunResult.outcome`, `returnTo`, `returnNote`); причина «вопрос правил или спеки» ведёт к шагу — владельцу знания или к человеку; вердикт человека сохраняется; `onFailure` остаётся как переход по умолчанию (совместимость) | один «возврат на предыдущий шаг» без причин: не отличает ошибку исполнения от дефекта постановки | средняя: эффект кодов не измерен |
| Лимиты цепочки | `maxRuns` шага и `maxTotalRuns` задачи, «нет прогресса» (круг без нового результата); значения по умолчанию — пересмотр по замеру (agent-chain.md, ворота G9) | только лимит шага: кружение по разным шагам не ловит | сильная для необходимости, слабая для значений |
| Бюджет | бюджет задачи `budget.issue` в иерархии run ≤ issue ≤ agent_day ≤ project_month, принудительный (Runner/шлюз LiteLLM, G4), связан с защитой от зацикливания | бюджет только на запуск и агента: цепочка из N запусков обходит его | сильная для необходимости |
| Проверка | независимый шаг-верификатор перед завершением по умолчанию; шаг и агент отличны от исполнителя | самопроверка исполнителем: MAST — неверная проверка 9,1% | средняя |
| Базовая линия | один агент (процесс из одного шага) — базовая линия; метрики сравнимы с цепочкой; число ролей заранее не выбираем, если замер не покажет выигрыш по стоимости на принятую задачу, процесс по умолчанию — один шаг | сразу многоролевая цепочка: LATS — более 50× стоимости без выигрыша | сильная для методики, топология ⚠️ |
| Самообучение | агент может ПРЕДЛАГАТЬ изменение навыков и плейбука (заметки к исходу `M3Record.notesFor`); применяет администратор новой версией настроек (4.4) после регрессионного набора и утверждения человеком, с откатом и чисткой; прирост в цепочке не измерен ⚠️ | агент сам переписывает инструкции (LangMem): Misevolution — отказы 99,4% → 54,4% | слабая-средняя |

**Пересмотр прежнего решения.** [Модель памяти](..\..\..\research\memory-model.md): «M5 меняет только администратор» остаётся в части применения (запись M5 — только версией настроек, R-REG), но агент теперь вправе предлагать ([FR-45](../../../architecture/components/memory/prd.md)). Что изменилось: R&D цепочки показал рост от приращений вне цепочек (ACE, GEPA) при условии человеческого утверждения. Пересмотр [AD-27](../../../architecture/decisions/AD-27.yaml) — если замер покажет, что цепочка не лучше одного агента, лимиты режут полезные цепочки (меняем значения, не принцип) или контур обучения не даёт прироста на отложенных задачах (контур закрывается).

Затронуто: [FR-205](../../../architecture/components/icplan/prd.md)…26 (спека автоподхвата), [FR-120](../../../architecture/components/guardrails/prd.md), [FR-45](../../../architecture/components/memory/prd.md), [FR-152](../../../architecture/components/observability/prd.md), модели [ProcessStep](../../../architecture/data/model-ProcessStep.yaml), [RunResult](../../../architecture/data/model-RunResult.yaml), [M3Record](../../../architecture/data/model-M3Record.yaml), [Run](../../../architecture/data/model-Run.yaml); задачи 3.6, 3.7, 3.9, 4.4, 4.5; BACKLOG (замер, прототип обучения). Ворота ⚠️ (число ролей, значения лимитов, прирост самообучения) не сняты.

<a id="d28"></a>
### AD-28. Самообучение агентов: модульный контур с режимами, ограничениями и снимками

Решено по исследованию ([R&D: цепочка агентов в трекере](..\..\..\research\agent-chain.md), Э7–Э9), решение принято 14.10.2026 по результату анализа (выбор поручен агенту владельцем продукта, как в [AD-27](../../../architecture/decisions/AD-27.yaml)). Контекст: [AD-27](../../../architecture/decisions/AD-27.yaml) разрешил агенту только предлагать изменения; владелец запросил самообучение с отключаемостью, настройками, снимками и откатом. Уточняет [AD-27](../../../architecture/decisions/AD-27.yaml): режим «применять с гейтами» добавляется как явная настройка, по умолчанию «выкл».

| Вопрос | Решение | Альтернативы и почему не они | Сила опоры |
|---|---|---|---|
| Сценарии качества (Decision Drivers) | С1 отключаемость (≤ 1 мин, потерь 0), С2 настраиваемость (без деплоя, хардкода 0), С3 откат на снимок (≤ 5 мин), С4 заменяемость движка памяти (правок ядра 0), С5 новое ограничение без релиза (≤ 5 мин), С6 отравление памяти (100% записей с источником, исходом, TTL; N=3), С7 контроль человека (100% применений с одобрением), С8 стоимость (блокировка ≤ 1 запуск), С9 просмотр и удаление памяти (≤ 1 мин), С10 трасса (≤ 5 мин на поиск), С11 автооткат (≤ 5 мин), С12 уровни (строже побеждает, 100% сочетаний) | — | числа целевые, пороги к калибровке |
| Решение (Decision Outcome) | Вариант B: модульный контур — виды обучения (факты, плейбук, навыки, оптимизация промптов) за адаптерами (`MemoryStore`, `PlaybookStore`, `SkillRegistry`, `PromptOptimizer`, `SnapshotStore`); режимы «выкл / предлагать / применять с гейтами» по видам на уровнях агент → проект → команда, политика администратора сверху, строже побеждает; выше «предлагать» только при включённых О4, О12, О14; каталог ограничений О1–О15 как политика, включаемая по одному; снимки (конфиг + память + плейбук + навыки + версия модели) как неизменяемые версии с указателем, откат и автооткат; агент-инструментальщик — отдельный выключаемый модуль. **Режим по умолчанию «выкл» для всех видов, ограничения включены заранее**; MVP модулей — факты и плейбук | 0 (ничего): не отвечает на запрос владельца (3 из 12 сценариев). A (зашитое самообучение): хардкод и общий тумблер, не закрывает С2, С4, С5, С11, С12. C (внешний сервис памяти целиком): привязка, снимок без плейбука и версий, не закрывает политику. Дообучение весов: нужны свои веса и десятки тысяч траекторий | слабая-средняя: польза подтверждена вне цепочек (ACE, GEPA), риск подтверждён (Misevolution), пороги не измерены ⚠️ |
| Настраиваемость и права | Хранится в [`AgentSettings`](../../../architecture/data/model-AgentSettings.yaml) (блоки `learning`, `snapshots`, `toolsmith`, `guardrails`); выключение не удаляет накопленное; память доступна для просмотра, правки и удаления; изменения без релиза; экраны 4.4 по [AD-24](../../../architecture/decisions/AD-24.yaml) | параметры в коде: каждая смена — релиз | средняя |
| Подтверждение (Confirmation) | Fitness-функции F1–F9: F1 схема без хардкода (CI), F2 прогон отключения (CI + раз в неделю), F3 тест отката на staging, F4 контрактный тест адаптеров на двух реализациях, F5 таблица уровней и ограничение без релиза, F6 доля записей с источником и TTL, F7 применение без одобрения блокируется, F8 потолок стоимости обучения, F9 квартальное ручное ревью каталога О1–О15 (слабое место: нет автоматики) | проверка вручную при релизе: дрейф незаметен | средняя |
| Пересмотр | По результату замера «без обучения / факты / плейбук / всё» (ворота G9) или при ложных срабатываниях автоотката (калибровка порога). Если «обучение включено» не лучше «без обучения» на отложенных задачах или ухудшает безопасность — режимы выше «выкл» закрываются | — | — |
| Последствия (Consequences) | Плюс: закрыто 12 из 12 сценариев, замена движка без правок ядра. Минус: лишний слой адаптеров и расхождение с возможностями Mem0; схема настроек и политика — источник ошибок конфигурации; трудоёмкость ~8 чел.-нед. по MVP, ~14 полностью (оценка ±2×); польза в проекте может быть нулевой. Подробно — Э10 R&D | — | — |

Затронуто (More Information): [FR-46](../../../architecture/components/memory/prd.md), [FR-47](../../../architecture/components/memory/prd.md) (agent-memory), [FR-64](../../../architecture/components/platform-module/prd.md), [FR-65](../../../architecture/components/platform-module/prd.md) (agent-registry), [FR-131](../../../architecture/components/guardrails/prd.md)…25 (guardrails), [FR-103](../../../architecture/components/platform-module/prd.md), [FR-104](../../../architecture/components/platform-module/prd.md) (control-plane), [FR-153](../../../architecture/components/observability/prd.md) (observability); модель [AgentSettings](../../../architecture/data/model-AgentSettings.yaml); задачи 3.9, 4.3, 4.4, 4.5; BACKLOG (замер, навыки и промпты). Ворота ⚠️ G9 (прирост обучения, пороги О4, О12, О13) не сняты.
