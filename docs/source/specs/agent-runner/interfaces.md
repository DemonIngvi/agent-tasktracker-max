# agent-runner — конфигурация, данные, интерфейсы, отказы

← spec.md · схема · трассировка · правила

## Уровни конфигурации

| Уровень | Что | Где хранится | Область |
|---|---|---|---|
| L0 | Конфиг деплоя | S9 | платформа целиком: адреса, переключатели G1–G4, режим планирования, потолки лимитов |
| L1 | Platform module | S2 | агент: бюджеты, профили, данные guardrails, флаги планирования |
| L2 | Определение агента | S1 (+ YAML импорт) | агент: модель, инструкция, тулы, навыки, MCP, лимиты запуска |
| L3 | Запуск | задача ICPlan / `Run` | версия агента, критерии приёмки, задание |

Правило: значение берётся с самого конкретного уровня (L3 → L0), но не выше потолка L0.

## Параметры модуля

Значения и границы пересматриваются по статистике запусков (3.9) и нагрузочному тесту (4.8); правило — виды спек, таблица параметров.

| Параметр | Что задаёт | Уровень | Хранилище | По умолчанию | Почему так по умолчанию | Мин | Макс | Тип | На что опираться при выборе |
|---|---|---|---|---|---|---|---|---|---|
| `scheduling.aging_s` | Интервал повышения приоритета ждущего запуска при `order: priority` | L0 | S9 | 600 | низкий приоритет стартует не позже ~30 мин при 3 уровнях выше | 60 | 3600 |  | длина очереди в пике и ожидание низкоприоритетных задач |
| `poll_interval_ms` | Как часто опрашивать очередь | L0 | S9 | 3000 | ~0,3 RPS на агента — малая доля пика API (20 RPS) | 1000 | 30000 |  | агентов × 1000 / интервал ≤ 10% пика API; дольше — задержка старта запуска |
| `concurrency` | Параллельных запусков на агента | L1 | S2 | 1 | задачи агента обычно в одной кодовой базе — без гонок | 1 | `scheduling.global_max` |  | параллельно — только агентам с независимыми задачами |
| `timeout_s` | Таймаут запуска по умолчанию | L1 | S2 | 1800 | 30 мин — длинная задача с кодом и тестами | 60 | 14400 |  | p95 длительности запусков; дольше 4 ч — дробить задачу |
| `retry` | Повтор при сбое инфраструктуры | L0 | S9 | 0 (без повтора) | повтор неидемпотентной работы даёт двойные комментарии и PR | 0 | 3 |  | 3 — как `AGENT_RUN_MAX_ATTEMPTS` ICPlan; повторять, только если инфраструктура упала до первого действия |
| `agents` | Ключи агентов, которые обслуживает Runner | L0 | S9 | — (обязательный) | Runner без ключей не получает запусков | 1 ключ | все внешние агенты команды | список agents | один Runner может вести несколько агентов |
| `guardrails.g1.enabled` | Проверка допуска и бюджета | L0 | S9 | true | fail-closed по умолчанию | false | true |  | false — только в dev |
| `scheduling.mode` | sequential или parallel | L0 | S9 | parallel | полезная пропускная способность | sequential | parallel |  | sequential — для отладки и разбора проблем |
| `scheduling.global_max` | Всего запусков одновременно | L0 | S9 | 4 | профиль нагрузки: 4 активных; 8 vCPU узла − сервисы ≈ 4 CPU по 1 CPU на sandbox | 1 | (vCPU узла − резерв сервисов) / CPU профиля sandbox |  | ёмкость узла и лимиты провайдера моделей |
| `scheduling.per_issue` | Запусков на задачу | L0 | S9 | 1 | исключает гонки внутри задачи (FR-70) | 1 | 1 |  | фиксировано требованием |
| `scheduling.order` | fifo или priority | L0 | S9 | fifo | предсказуемо, без голодания | fifo | priority |  | priority — если есть срочные задачи; следить за голоданием |
| `scheduling.agents.<id>.parallel / max` | Может ли агент идти в несколько потоков | L1 | S2 | нет / 1 | как `concurrency` | 1 | `concurrency` | одно из: да, нет / число | независимость задач агента |
| `scheduling.models.<alias>.max` | Запусков на модель | L0 | S9 | 3 | rate limit типового ключа провайдера при ~1 RPS к LiteLLM | 1 | `scheduling.global_max` |  | rpm / tpm ключа провайдера модели |
| `pool.size` | Готовых контейнеров на профиль: Sandbox claim берёт из пула, Finalizer доливает | L1 | S2 | 2 | см. agent-sandbox | 0 | `scheduling.global_max` |  | см. agent-sandbox |
| `provider` | Реализация `SandboxProvider`: Docker или K8s | L0 | S9 | docker | см. agent-sandbox | docker | k8s |  | см. agent-sandbox |
| `workspace.sources` | Источники рабочего пространства запуска: из них манифест и токены репозиториев | L1 | S2 | нет | см. agent-sandbox | нет | все ресурсы каталога проекта | список sources | см. agent-sandbox |
| `setup.script` | Скрипт шага подготовки проекта | L1 | S2 | нет | см. agent-sandbox | нет | — | строка | см. agent-sandbox |
| `setup.cache_ttl_h` | Срок кэша подготовки по хешу lock-файлов (`setup_cache`) | L0 | S9 | 168 | см. agent-sandbox | 0 | 720 |  | см. agent-sandbox |
| `setup.timeout_s` | Таймаут шага подготовки | L1 | S2 | 600 | см. agent-sandbox | 60 | 3600 |  | см. agent-sandbox |
| `servers` | MCP-серверы агента, к которым пускает MCP-прокси | L2 | S1 | itsaplan-core | см. tool-integration | itsaplan-core | каталог серверов | список servers | см. tool-integration |
| `tools` | Allowlist тулов сервера, по которому MCP-прокси фильтрует `tools/list` и проверяет `tools/call` | L2 | S1 | минимальный (чтение задачи, комментарий) | см. tool-integration | пусто | все тулы сервера | список tools | см. tool-integration |
| `auth.secret_ref` | Secret с учётными данными MCP-сервера, которые подставляет MCP-прокси | L2 | S1 | — (обязательный) | см. tool-integration | ссылка на Secret | ссылка на Secret | ссылка Secret | см. tool-integration |
| `on_engine_error` | Решение G1 и G2, если OPA не ответила | L0 | S9 | deny | см. guardrails | deny | allow |  | см. guardrails |
| `kill_switch` | Аварийная остановка агента или платформы: Admission не пускает новые запуски | L1 | S2 | выкл | см. guardrails | выкл | вкл |  | см. guardrails |
| `budget.run / agent_day / project_month` | Бюджеты, которые проверяет G1 до старта | L1 | S2 | 1 $ / 5 $ / задаётся | см. guardrails | 0,1 $ / 0 $ / 0 $ | run ≤ agent_day ≤ project_month / 20 | число $ / число $ / число $ | см. guardrails |
| `limits.idle_s` | Простой без событий, после которого Run supervisor останавливает запуск | L1 | S2 | 300 | см. guardrails | 60 | `timeout_s` |  | см. guardrails |
| `events.level` | Детализация событий, которые Event relay передаёт в ICPlan | L0 | S9 | всё | см. observability | итоги | всё | одно из: итоги, всё | см. observability |

## Хранилища данных

| ID | Хранилище | Что хранит | Владелец | Резервирование / срок |
|---|---|---|---|---|
| S2 | Postgres ICPlan, схема `platform` | настройки агентов, версии, профили sandbox и памяти, данные guardrails, параметры планирования | Platform module | вместе с S1 |
| S3 | Postgres ICPlan (база `itsaplan`): `run_event` — схема `platform`; `scheduler_slot`, `setup_cache` — схема `runner` (AD-22) | события запусков, слоты планировщика | Agent Runner / Observability | события — 90 дней; слоты — оперативные |
| S5 | Postgres ICPlan, схема `harness_ckpt` | checkpoint цикла Harness по API I12 | Agent Runner | 7 дней (`checkpoint.ttl`) |
| S9 | Конфиг деплоя: `values.yaml` (git, без секретов) + Secret / `.env` (вне git) | параметры платформы, адреса, переключатели guardrails, секреты | эксплуатация | версии в git; секреты — вне git |

## Интерфейсы обмена

| ID | От → к | Протокол | Формат | Аутентификация | Режим | Таймаут | Повтор | Идемпотентность |
|---|---|---|---|---|---|---|---|---|
| I1 | Agent Runner → ICPlan Run Queue (claim, pull) | HTTP REST (протокол `@itsaplan/runner`) | JSON `Run` | Bearer API-ключ агента | pull, опрос 3 с | 10 с | backoff до 60 с | аренда запуска: выдаётся одному Runner |
| I2 | Agent Runner → ICPlan (шаги, итог) | HTTP REST | JSON-пакеты `RunEvent` с `seq`, `RunResult` | Bearer API-ключ агента | асинхронно | 10 с | повтор с дедупликацией по (run_id, seq) | да, по (run_id, seq) |
| I3 | Agent Runner → ICPlan: heartbeat, в ответе (approve, отмена) | HTTP REST, опрос состояния запуска | JSON `ApprovalDecision`, статус | Bearer API-ключ агента | pull | 10 с | backoff | да, по (run_id, seq) |
| I4 | Agent Runner → Platform module API | HTTP REST | JSON `AgentSettings`; на старте запуска после слотов `GET /platform/runs/:runId/agent` → `{version, definition: AgentDefinition, settings: AgentSettings}` (AD-23) | сервисный токен | синхронно | 2 с | 3 раза | чтение |
| I5 | Agent Runner → OPA (G1) | HTTP REST `POST /v1/data/agent/g1` | JSON `PolicyInput` / `PolicyDecision` | внутренняя сеть (mTLS — позже) | синхронно | 200 мс | нет → `on_engine_error` | чтение |
| I6 | Agent Runner → Docker Engine API | HTTP поверх unix-сокета (позже K8s API) | JSON Docker API | доступ к сокету | синхронно | 30 с | 1 раз | create — нет; destroy — да |
| I7 | Agent Runner ↔ Harness | HTTP внутри сети sandbox; события — NDJSON-поток | `RunBundle`, `RunEvent`, `RunResult`, `ApprovalDecision` | одноразовый токен запуска | поток | = `timeout_s` | переподключение с последнего `seq` | да, по `seq` |
| I9 | Harness → MCP-прокси Agent Runner → MCP-серверы (AD-19) | MCP Streamable HTTP, JSON-RPC 2.0 | `tools/list` (фильтр по allowlist запуска), `tools/call` (allowlist и G2 в Runner) | токен запуска до Runner; учётные данные сервера подставляет Runner из Secret | синхронно | 30 с | чтение — 2 раза; запись — нет | запись — нет |
| I10 | Agent Runner → OPA (G2 для вызовов MCP, AD-19) | HTTP REST `POST /v1/data/agent/g2` | JSON `PolicyInput` / `PolicyDecision` | внутренняя сеть | синхронно | 200 мс | нет → `on_engine_error` | да |
| I12 | Harness → Agent Runner (checkpoint, приём) | HTTP внутри сети sandbox: `PUT / GET /runs/{id}/checkpoint`; Runner пишет в схему `harness_ckpt` (S5) | LangGraph checkpoint | одноразовый токен запуска (учётных данных БД в sandbox нет) | синхронно | 5 с | 3 раза | да, по (run_id, step) |
| I18 | Agent Runner → git-провайдер (токены) | HTTPS REST (GitHub App / Gitea API) | JSON | ключ приложения (Secret) | синхронно | 10 с | 2 раза | да |
| I19 | Agent Runner / ICPlan → объектное хранилище (RustFS) | S3 API | файлы | ключи сервиса (Secret) | синхронно | 30 с | 3 раза | да, по ключу объекта |
| I22 | Сервисы → PgBouncer → Postgres | протокол PostgreSQL | SQL | логин / пароль из Secret, роль на схему | синхронно | 5 с на запрос | 1 раз (только чтение) | — |
| I23 | Agent Runner → Kubernetes API (этап 4) | HTTPS REST (client-go) | JSON манифесты Pod / Job | ServiceAccount с правами только на namespace `itsaplan-agents` | синхронно | 30 с | 1 раз | create — нет |
| I24 | MCP-прокси Agent Runner → MCP itsaplan-core в api ICPlan (`POST /mcp`, AD-19) | MCP Streamable HTTP, JSON-RPC 2.0 | `tools/list`, `tools/call` — после фильтра по allowlist и G2 в прокси | `Authorization: Bearer <ключ агента>`, ключ подставляет Runner из Secret | синхронно | 30 с | чтение — 2 раза; запись — нет | запись — нет |

## Нагрузка и развёртывание

| | |
|---|---|
| **Нагрузка** (гипотеза, R&D) | опрос очереди ~0.3 RPS на агента; до 6 запусков в очереди, 4 активны; старт запуска после взятия < 5 с (с пулом < 1 с); MCP-прокси ~1 RPS (AD-19); шаг подготовки — до `setup.timeout_s` при промахе кэша |
| **Развёртывание** (R&D) | Deployment `agent-runner` в `itsaplan-agents`, 1 реплика (MVP), 2 — с общими слотами; requests 0.1 CPU / 128 МиБ, limits 0.5 / 512 МиБ; без ingress |

Детали форматов — потоки.

## Отказы (FMEA)

| Отказ | Обнаружение | Поведение | Восстановление |
|---|---|---|---|
| ICPlan недоступен | ошибки I1 | опрос с backoff, активные запуски продолжаются, события буферизуются | досылка событий по `seq` |
| Platform module недоступен | ошибки I4 | новые запуски не стартуют (нет настроек) | повтор; кэш настроек не используется — безопасность |
| Docker / пул недоступен | ошибки I6 | запуск остаётся в `queued` | повтор, событие оператору |
| MCP-сервер недоступен | ошибка I9 | агент получает ошибку тула, цикл продолжается | повтор чтения 2 раза |
| Шаг подготовки упал или превысил `setup.timeout_s` | код выхода, таймаут | запуск `failed` с причиной «подготовка среды» | исправить скрипт или реестр; повторить запуск |
| Runner упал | истечение аренды | запуски возвращаются в очередь, слоты освобождаются | новый экземпляр подхватывает |
| Нет настроек агента / ключа | пустой ответ I4 | запуск `agent_unavailable` | администратор заполняет настройки |
| Postgres платформы (S2, S3) недоступен | ошибки записи `run_event`, `scheduler_slot` | новые запуски не стартуют; события активных буферизуются в памяти Runner | досылка по `seq` после восстановления; слоты пересчитываются по активным запускам |
