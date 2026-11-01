# Сводная таблица задач

← README · план документации · [бэклог](BACKLOG.md)

По компонентам: сначала выполненное ✅ (и частично ⚠️), затем то, что нужно сделать ⬜. Детали и критерии приёмки — по ссылке в колонке «Где».

Источники: `ap` — [icplan-agent-autopickup/tasks.md](design\icplan-agent-autopickup\tasks.md), `arch` — [architecture.md → Доработки по модулям](architecture.md).

Порядок, оценки и документы задач по INVEST — в [ROADMAP](ROADMAP.md).

## ICPlan

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ✅ | Локальный стек [ICPlan](../architecture/components/icplan/README.md) (web, api, worker, bot, postgres + pgvector, rustfs) | `локальный путь` | [FR-169](../architecture/components/infrastructure/prd.md) |
| ✅ | CRUD агентов: имя, модель, инструкция, проекты | [ICPlan](../architecture/components/icplan/README.md): Команда → ИИ-агенты | [FR-54](../architecture/components/platform-module/prd.md), [FR-8](../architecture/components/icplan/prd.md) |
| ✅ | Ключи провайдеров, тулы, навыки, MCP-серверы | [ICPlan](../architecture/components/icplan/README.md): Команда → Настройки | [FR-140](../architecture/components/llm-gateway/prd.md), [FR-176](../architecture/components/mcp-tools/prd.md), [FR-181](../architecture/components/mcp-tools/prd.md) |
| ✅ | MCP-сервер `itsaplan-core` (весь REST API как тулы) | [ICPlan](../architecture/components/icplan/README.md) | [FR-182](../architecture/components/mcp-tools/prd.md) |
| ✅ | Запуск агента по делегату и по упоминанию | [ap 0.1](design\icplan-agent-autopickup\tasks.md) | [FR-204](../architecture/components/icplan/prd.md) |
| ✅ | Автоназначение исполнителя на статус (без запуска) | [ap 0.2](design\icplan-agent-autopickup\tasks.md) | [FR-204](../architecture/components/icplan/prd.md) |
| ✅ | Агент меняет поля задачи через `update_issue` (колонку задачи в процессе меняет [ICPlan](../architecture/components/icplan/README.md)) | [ap 0.3](design\icplan-agent-autopickup\tasks.md) | [FR-182](../architecture/components/mcp-tools/prd.md), [FR-197](../architecture/components/icplan/prd.md) |
| ✅ | Очередь запусков внешнего раннера, стрим ответа | [ICPlan](../architecture/components/icplan/README.md) `@itsaplan/runner` | [FR-2](../architecture/components/icplan/prd.md), [FR-4](../architecture/components/icplan/prd.md) |
| ✅ | Ответ агента публикуется комментарием в задаче | Форк `itsaplan-app` (`postRunAnswer`) | [FR-4](../architecture/components/icplan/prd.md) |
| ⚠️ | История запусков — только итог, без шагов | [задача 3.3](tasks\3.3-run-events-timeline.md) | [FR-4](../architecture/components/icplan/prd.md), [FR-147](../architecture/components/observability/prd.md) |
| ⬜ | Агент шага процесса: колонка → делегат → запуск | [ap 1.1–1.3](design\icplan-agent-autopickup\tasks.md) | [FR-188](../architecture/components/icplan/prd.md), [FR-196](../architecture/components/icplan/prd.md) |
| ⬜ | Тип задачи задаёт процесс: первый шаг при создании и смене типа | [ap 2.1–2.3](design\icplan-agent-autopickup\tasks.md) | [FR-189](../architecture/components/icplan/prd.md) |
| ⬜ | Эффект Действия «делегировать агенту» (T-04) | [ap 3.1–3.2](design\icplan-agent-autopickup\tasks.md) | [FR-190](../architecture/components/icplan/prd.md) |
| ⬜ | Приоритет правил, защита от дублей, очистка при выходе агента | [ap 4.1–4.3](design\icplan-agent-autopickup\tasks.md) | [FR-191](../architecture/components/icplan/prd.md), [FR-192](../architecture/components/icplan/prd.md), [FR-195](../architecture/components/icplan/prd.md) |
| ⬜ | Передача итога следующему агенту, запись в истории | [ap 5.1–5.2](design\icplan-agent-autopickup\tasks.md) | [FR-193](../architecture/components/icplan/prd.md), [FR-194](../architecture/components/icplan/prd.md) |
| ⬜ | Процесс: переходы по итогу запуска, лимит шага, очередь агента | [задача 3.6](tasks\3.6-icplan-process-engine.md) | [FR-197](../architecture/components/icplan/prd.md), [FR-198](../architecture/components/icplan/prd.md), [FR-205](../architecture/components/icplan/prd.md), [FR-206](../architecture/components/icplan/prd.md) |
| ⬜ | Управление ходом задачи: проверка, вердикт, остановка, повтор шага, версии процесса | [задача 3.7](tasks\3.7-icplan-task-control.md) | [FR-199](../architecture/components/icplan/prd.md), [FR-200](../architecture/components/icplan/prd.md), [FR-201](../architecture/components/icplan/prd.md), [FR-202](../architecture/components/icplan/prd.md), [FR-203](../architecture/components/icplan/prd.md), [FR-207](../architecture/components/icplan/prd.md) |
| ⬜ | Чат с агентом, указания во время работы, выключение агента | [задача 3.8](tasks\3.8-agent-chat-control.md) | [FR-10](../architecture/components/icplan/prd.md), [FR-11](../architecture/components/icplan/prd.md), [FR-12](../architecture/components/icplan/prd.md), [FR-28](../architecture/components/harness/prd.md) |
| ⬜ | Сводка задач с агентами, статистика и недельный отчёт затрат владельцу | [задача 3.9](tasks\3.9-agent-summary-stats.md) | [FR-152](../architecture/components/observability/prd.md), [FR-153](../architecture/components/observability/prd.md) |
| ⬜ | Approve действия агента в UI | [задача 3.4](tasks\3.4-icplan-approve-ui.md), [задача 1.5](tasks\1.5-harness-hooks-approve.md) | [FR-5](../architecture/components/icplan/prd.md), [FR-6](../architecture/components/icplan/prd.md), [FR-23](../architecture/components/harness/prd.md) |
| ⬜ | Результат quality gate в задаче | [задача 1.6](tasks\1.6-harness-limits-context.md), [задача 3.3](tasks\3.3-run-events-timeline.md) | [FR-26](../architecture/components/harness/prd.md), [FR-4](../architecture/components/icplan/prd.md) |
| ⬜ | Пошаговый чат запуска в задаче | [задача 3.3](tasks\3.3-run-events-timeline.md) | [FR-147](../architecture/components/observability/prd.md), [FR-4](../architecture/components/icplan/prd.md) |
| ⬜ | Затраты по задаче | [задача 3.5](tasks\3.5-icplan-type-actions-cost.md) | [FR-150](../architecture/components/observability/prd.md), [FR-136](../architecture/components/llm-gateway/prd.md) |
| ⬜ | Версии определения агента, экспорт/импорт YAML | [задача 1.2](tasks\1.2-agent-definition-yaml.md) | [FR-98](../architecture/components/platform-module/prd.md), [FR-99](../architecture/components/platform-module/prd.md), [FR-55](../architecture/components/platform-module/prd.md), [FR-56](../architecture/components/platform-module/prd.md) |
| ⬜ | Allowlist репозиториев агента | [задача 4.4](tasks\4.4-platform-module.md), [задача 4.2](tasks\4.2-egress-repo-access.md) | [FR-95](../architecture/components/platform-module/prd.md), [FR-85](../architecture/components/sandbox/prd.md) |
| ⬜ | Передача в запуске quality gate, лимитов; события approve/вопрос | [задача 2.3](tasks\2.3-config-from-icplan.md), [задача 2.8](tasks\2.8-config-storage-interfaces-fmea.md), [задача 3.4](tasks\3.4-icplan-approve-ui.md) | [FR-2](../architecture/components/icplan/prd.md), [FR-5](../architecture/components/icplan/prd.md), [FR-26](../architecture/components/harness/prd.md) |

## Platform module (модуль ICPlan)

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ⬜ | Модуль в форке [ICPlan](../architecture/components/icplan/README.md), своя схема БД | [задача 4.4](tasks\4.4-platform-module.md) | [FR-96](../architecture/components/platform-module/prd.md), [FR-106](../architecture/components/platform-module/prd.md) |
| ⬜ | Алиасы LLM, бюджеты, профили sandbox и памяти | [задача 4.4](tasks\4.4-platform-module.md) | [FR-95](../architecture/components/platform-module/prd.md), [FR-134](../architecture/components/llm-gateway/prd.md), [FR-120](../architecture/components/guardrails/prd.md), [FR-86](../architecture/components/sandbox/prd.md) |
| ⬜ | Хранение данных guardrails (allowlist, лимиты) | [задача 4.4](tasks\4.4-platform-module.md) | [FR-95](../architecture/components/platform-module/prd.md), [FR-110](../architecture/components/guardrails/prd.md) |
| ⬜ | Экраны настроек в UI [ICPlan](../architecture/components/icplan/README.md) | [задача 4.4](tasks\4.4-platform-module.md) | [FR-95](../architecture/components/platform-module/prd.md) |
| ⬜ | Аутентификация и роли для этих настроек | [задача 4.4](tasks\4.4-platform-module.md) | [FR-101](../architecture/components/platform-module/prd.md) |

## Agent Runner

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ✅ | Протокол раннера [ICPlan](../architecture/components/icplan/README.md) как основа (опрос очереди, стрим) | [ICPlan](../architecture/components/icplan/README.md) `docs/runner.md` | [FR-2](../architecture/components/icplan/prd.md), [FR-66](../architecture/components/agent-runner/prd.md) |
| ⬜ | Каркас Runner (Go), контракт Runner↔[Harness](../architecture/components/harness/README.md) | [задача 2.1](tasks\2.1-runner-external.md) | [FR-66](../architecture/components/agent-runner/prd.md), [FR-79](../architecture/components/agent-runner/prd.md) |
| ⬜ | Работа как внешний раннер [ICPlan](../architecture/components/icplan/README.md): опрос, стрим, итог | [задача 2.1](tasks\2.1-runner-external.md) | [FR-1](../architecture/components/icplan/prd.md), [FR-2](../architecture/components/icplan/prd.md), [FR-4](../architecture/components/icplan/prd.md), [FR-73](../architecture/components/agent-runner/prd.md) |
| ⬜ | Жизненный цикл: claim из пула → [Harness](../architecture/components/harness/README.md) → результат → destroy | [задача 2.2](tasks\2.2-sandbox-docker-oneshot.md) | [FR-82](../architecture/components/sandbox/prd.md), [FR-83](../architecture/components/sandbox/prd.md), [FR-75](../architecture/components/agent-runner/prd.md) |
| ⬜ | Планировщик: слоты, режим sequential / parallel, один запуск на задачу | [задача 2.7](tasks\2.7-runner-scheduler.md) | [FR-67](../architecture/components/agent-runner/prd.md), [FR-68](../architecture/components/agent-runner/prd.md), [FR-69](../architecture/components/agent-runner/prd.md), [FR-70](../architecture/components/agent-runner/prd.md), [FR-71](../architecture/components/agent-runner/prd.md) |
| ⬜ | Таймаут и отмена | [задача 2.1](tasks\2.1-runner-external.md) | [FR-74](../architecture/components/agent-runner/prd.md), [FR-7](../architecture/components/icplan/prd.md), [FR-119](../architecture/components/guardrails/prd.md) |
| ⬜ | Короткоживущий токен репозиториев на запуск | [задача 4.2](tasks\4.2-egress-repo-access.md) | [FR-85](../architecture/components/sandbox/prd.md), [FR-88](../architecture/components/sandbox/prd.md) |

## Sandbox [G3]

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ⚠️ | Локальный k3d-кластер работает (основа для K8s-провайдера) | [задача 4.6](tasks\4.6-k8s-helm-ingress.md) | [FR-169](../architecture/components/infrastructure/prd.md) |
| ⬜ | `SandboxProvider` + Docker-реализация | [задача 2.2](tasks\2.2-sandbox-docker-oneshot.md) | [FR-82](../architecture/components/sandbox/prd.md) |
| ⬜ | Тёплый пул по профилям, одноразовое использование | [задача 4.1](tasks\4.1-sandbox-warm-pool.md) | [FR-83](../architecture/components/sandbox/prd.md) |
| ⬜ | Профили CPU/RAM/disk | [задача 4.1](tasks\4.1-sandbox-warm-pool.md) | [FR-86](../architecture/components/sandbox/prd.md) |
| ⬜ | Изолированная сеть + egress-прокси с allowlist | [задача 4.2](tasks\4.2-egress-repo-access.md) | [FR-87](../architecture/components/sandbox/prd.md), [FR-113](../architecture/components/guardrails/prd.md) |
| ⬜ | Подстановка секретов и токенов прокси | [задача 4.2](tasks\4.2-egress-repo-access.md) | [FR-88](../architecture/components/sandbox/prd.md) |
| ⬜ | Эфемерный `/workspace`, клон репозиториев, запрет push в защищённые ветки | [задача 2.2](tasks\2.2-sandbox-docker-oneshot.md), [задача 4.2](tasks\4.2-egress-repo-access.md) | [FR-84](../architecture/components/sandbox/prd.md), [FR-85](../architecture/components/sandbox/prd.md) |

## Harness [G2]

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ⬜ | Образ [Harness](../architecture/components/harness/README.md), сборка агента из определения | [задача 1.3](tasks\1.3-harness-core.md) | [FR-19](../architecture/components/harness/prd.md) |
| ⬜ | Граф LangGraph `context → llm → tools` | [задача 1.3](tasks\1.3-harness-core.md) | [FR-20](../architecture/components/harness/prd.md), [FR-21](../architecture/components/harness/prd.md) |
| ⬜ | Hooks before/after llm\|tool, on_stop | [задача 1.5](tasks\1.5-harness-hooks-approve.md) | [FR-22](../architecture/components/harness/prd.md) |
| ⬜ | MCP через адаптер, таймауты тулов | [задача 1.4](tasks\1.4-harness-mcp-tools.md) | [FR-178](../architecture/components/mcp-tools/prd.md) |
| ⬜ | Пауза на approve и возобновление (checkpointer) | [задача 1.5](tasks\1.5-harness-hooks-approve.md) | [FR-23](../architecture/components/harness/prd.md) |
| ⬜ | Стрим шагов для чата запуска | [задача 1.3](tasks\1.3-harness-core.md) | [FR-24](../architecture/components/harness/prd.md) |
| ⬜ | Управление контекстом и сжатие | [задача 1.6](tasks\1.6-harness-limits-context.md) | [FR-25](../architecture/components/harness/prd.md) |
| ⬜ | Завершение done/limit/error, отдача результата | [задача 1.6](tasks\1.6-harness-limits-context.md) | [FR-27](../architecture/components/harness/prd.md) |

## Memory (M0–M6)

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ✅ | M0 рабочая — в каждом запуске | [arch → Память](architecture.md) | [FR-36](../architecture/components/memory/prd.md) |
| ✅ | M1 сессионная — тред в БД [ICPlan](../architecture/components/icplan/README.md) | [arch → Память](architecture.md) | [FR-36](../architecture/components/memory/prd.md), [FR-38](../architecture/components/memory/prd.md) |
| ✅ | M2 эпизодическая — `agent_run` в БД | [arch → Память](architecture.md) | [FR-36](../architecture/components/memory/prd.md), [FR-38](../architecture/components/memory/prd.md) |
| ✅ | M5 процедурная — инструкция и навыки | [arch → Память](architecture.md) | [FR-36](../architecture/components/memory/prd.md) |
| ✅ | M6 организационная — документы, `get_document` | [arch → Память](architecture.md) | [FR-36](../architecture/components/memory/prd.md) |
| ⬜ | M3 задачная: тул записи + подача в контекст (первым) | [задача 2.5](tasks\2.5-memory-m2-m3.md) | [FR-39](../architecture/components/memory/prd.md) |
| ⬜ | M2 в контекст: итоги последних N запусков задачи | [задача 2.5](tasks\2.5-memory-m2-m3.md) | [FR-40](../architecture/components/memory/prd.md) |
| ⬜ | API памяти с проверкой профиля и области видимости | [задача 2.5](tasks\2.5-memory-m2-m3.md) | [FR-37](../architecture/components/memory/prd.md), [FR-42](../architecture/components/memory/prd.md) |
| ⬜ | Сроки хранения и админ-удаление | [задача 2.5](tasks\2.5-memory-m2-m3.md) | [FR-42](../architecture/components/memory/prd.md), [FR-43](../architecture/components/memory/prd.md) |

## MCP / Tools

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ✅ | MCP-серверы, тулы и навыки в [ICPlan](../architecture/components/icplan/README.md) | [ICPlan](../architecture/components/icplan/README.md) | [FR-176](../architecture/components/mcp-tools/prd.md), [FR-181](../architecture/components/mcp-tools/prd.md) |
| ⬜ | Передача списка тулов/MCP из [ICPlan](../architecture/components/icplan/README.md) в [Harness](../architecture/components/harness/README.md) | [задача 2.3](tasks\2.3-config-from-icplan.md), [задача 1.4](tasks\1.4-harness-mcp-tools.md) | [FR-177](../architecture/components/mcp-tools/prd.md) |
| ⬜ | MCP git-провайдера (Gitea / GitHub) | [задача 4.2](tasks\4.2-egress-repo-access.md) | [FR-176](../architecture/components/mcp-tools/prd.md), [FR-85](../architecture/components/sandbox/prd.md) |
| ⬜ | Тул памяти (запись M3) | [задача 2.5](tasks\2.5-memory-m2-m3.md) | [FR-39](../architecture/components/memory/prd.md) |
| ⬜ | Правила R1–R7: MCP или прямой вызов | [задача 1.4](tasks\1.4-harness-mcp-tools.md) | [FR-179](../architecture/components/mcp-tools/prd.md) |

## Guardrails [G1–G4]

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ⚠️ | Контейнер OPA развёрнут, не подключён | [задача 4.3](tasks\4.3-guardrails-opa.md) | [FR-116](../architecture/components/guardrails/prd.md) |
| ⬜ | Конфиг деплоя: включение/выключение G1–G4, режим отказа | [задача 4.3](tasks\4.3-guardrails-opa.md) | [FR-115](../architecture/components/guardrails/prd.md), [FR-126](../architecture/components/guardrails/prd.md) |
| ⬜ | G1 в Runner через OPA | [задача 4.3](tasks\4.3-guardrails-opa.md) | [FR-111](../architecture/components/guardrails/prd.md), [FR-116](../architecture/components/guardrails/prd.md) |
| ⬜ | G2 в [Harness](../architecture/components/harness/README.md) hooks через OPA, human approval | [задача 4.3](tasks\4.3-guardrails-opa.md) | [FR-112](../architecture/components/guardrails/prd.md), [FR-116](../architecture/components/guardrails/prd.md), [FR-117](../architecture/components/guardrails/prd.md) |
| ⬜ | G3: профиль контейнера и egress | [задача 4.2](tasks\4.2-egress-repo-access.md) | [FR-113](../architecture/components/guardrails/prd.md), [FR-87](../architecture/components/sandbox/prd.md) |
| ⬜ | G4: хуки LiteLLM (PII, injection, модерация) | [задача 4.5](tasks\4.5-litellm-budgets-fallback-g4.md) | [FR-114](../architecture/components/guardrails/prd.md) |
| ⬜ | Rego в git с тестами `opa test` | [задача 4.3](tasks\4.3-guardrails-opa.md) | [FR-110](../architecture/components/guardrails/prd.md) |
| ⬜ | Аудит срабатываний | [задача 4.3](tasks\4.3-guardrails-opa.md) | [FR-125](../architecture/components/guardrails/prd.md) |

## LiteLLM gw [G4]

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ✅ | LiteLLM развёрнут (`itsaplan-agents`) | `локальный путь` | [FR-145](../architecture/components/llm-gateway/prd.md) |
| ✅ | Маршрут по алиасу до провайдера проверен | AI-агент, решение 7.1 | [FR-134](../architecture/components/llm-gateway/prd.md) |
| ⚠️ | [ICPlan](../architecture/components/icplan/README.md) пока ходит к провайдерам напрямую | [задача 2.3](tasks\2.3-config-from-icplan.md) | [FR-21](../architecture/components/harness/prd.md), [FR-140](../architecture/components/llm-gateway/prd.md) |
| ⬜ | Алиасы, 2+ провайдера, локальная модель | [задача 1.1](tasks\1.1-mock-llm-litellm.md) | [FR-134](../architecture/components/llm-gateway/prd.md), [FR-140](../architecture/components/llm-gateway/prd.md) |
| ⬜ | Virtual key на агента с лимитами и бюджетом | [задача 1.1](tasks\1.1-mock-llm-litellm.md) | [FR-135](../architecture/components/llm-gateway/prd.md), [FR-136](../architecture/components/llm-gateway/prd.md), [FR-138](../architecture/components/llm-gateway/prd.md), [FR-120](../architecture/components/guardrails/prd.md) |
| ⬜ | Fallback-модель | [задача 4.5](tasks\4.5-litellm-budgets-fallback-g4.md) | [FR-139](../architecture/components/llm-gateway/prd.md) |

## Observability

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ✅ | История запусков в [ICPlan](../architecture/components/icplan/README.md) (итог) | [ICPlan](../architecture/components/icplan/README.md) | [FR-146](../architecture/components/observability/prd.md) |
| ⬜ | Таблица событий запуска в БД [ICPlan](../architecture/components/icplan/README.md) | [задача 3.3](tasks\3.3-run-events-timeline.md) | [FR-146](../architecture/components/observability/prd.md), [FR-155](../architecture/components/observability/prd.md) |
| ⬜ | Агрегаты затрат по запуску, задаче, агенту, модели | [задача 3.5](tasks\3.5-icplan-type-actions-cost.md) | [FR-150](../architecture/components/observability/prd.md), [FR-136](../architecture/components/llm-gateway/prd.md) |
| ⬜ | Срок хранения событий | [задача 3.3](tasks\3.3-run-events-timeline.md) | [FR-151](../architecture/components/observability/prd.md) |

## Инфраструктура

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ⚠️ | Локальный k3d-кластер, чарты `itsaplan`, `litellm`, `platform-infra`, Traefik с клиентским сертификатом (проект AI-агент 7.11–7.14) | [задача 4.6](tasks\4.6-k8s-helm-ingress.md) | [FR-169](../architecture/components/infrastructure/prd.md), [FR-160](../architecture/components/infrastructure/prd.md) |
| ⚠️ | Postgres 17 + pgvector и RustFS в compose [ICPlan](../architecture/components/icplan/README.md) | [задача 4.7](tasks\4.7-postgres-storage-backup.md) | [FR-163](../architecture/components/infrastructure/prd.md), [FR-164](../architecture/components/infrastructure/prd.md) |
| ⬜ | k3s, Helm, namespaces, сетевые политики и изоляция сред | [задача 4.6](tasks\4.6-k8s-helm-ingress.md) | [FR-159](../architecture/components/infrastructure/prd.md), [FR-160](../architecture/components/infrastructure/prd.md), [FR-161](../architecture/components/infrastructure/prd.md), [FR-167](../architecture/components/infrastructure/prd.md), [FR-175](../architecture/components/infrastructure/prd.md) |
| ⬜ | CloudNativePG, PgBouncer, RustFS, бэкап вне узла | [задача 4.7](tasks\4.7-postgres-storage-backup.md) | [FR-163](../architecture/components/infrastructure/prd.md), [FR-164](../architecture/components/infrastructure/prd.md), [FR-165](../architecture/components/infrastructure/prd.md) |
| ⬜ | Нагрузочный тест и подтверждение профиля | [задача 4.8](tasks\4.8-load-test.md) | NFR-11, NFR-12 |

## Интеграция (сквозное)

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ⬜ | Общий резолвер конфигурации L0–L3 (своя конфигурация, хранилища, интерфейсы, отказы — в задачах компонентов) | [задача 2.8](tasks\2.8-config-storage-interfaces-fmea.md) | [FR-31](../architecture/components/harness/prd.md), [FR-48](../architecture/components/memory/prd.md), [FR-77](../architecture/components/agent-runner/prd.md), [FR-90](../architecture/components/sandbox/prd.md), [FR-183](../architecture/components/mcp-tools/prd.md) |
| ⬜ | E2E: задача в [ICPlan](../architecture/components/icplan/README.md) → Runner → агент с MCP и памятью → итог в задаче | [задача 2.6](tasks\2.6-e2e-icplan.md) | [FR-1](../architecture/components/icplan/prd.md), [FR-4](../architecture/components/icplan/prd.md), [FR-73](../architecture/components/agent-runner/prd.md), [FR-40](../architecture/components/memory/prd.md) |
| ⬜ | E2E: смена модели агента без перезапуска | [задача 2.6](tasks\2.6-e2e-icplan.md) | [FR-58](../architecture/components/platform-module/prd.md), [FR-97](../architecture/components/platform-module/prd.md) |

## Документация

| Статус | Задача | Где | Требования |
|---|---|---|---|
| ✅ | Перевести 16 R&D на методологию v3.1: потребности, ключевые функции и ценность, перенос, встраивание по I-кодам, спор ролей, последствия во всей цепочке, микропрезентация | методология R&D | — (документация) |
| ✅ | README, гид по чтению, план, бэклог, architecture.md v0.7 | PLAN этапы 1–2 | — (документация) |
| ✅ | Спеки: 10 модулей, интеграция, автоподхват | `openspec/changes/` | — (документация) |
| ✅ | Roadmap и документы задач по INVEST с оценками | [ROADMAP](ROADMAP.md) | — (документация) |
| ✅ | `define-agent-platform/tasks.md` обновлён по ROADMAP | [tasks.md](design\define-agent-platform\tasks.md) | — (документация) |
| ✅ | Переписать спеки `control-plane` и `icplan-integration` | control-plane, icplan-integration | — (документация) |
| ✅ | Карточки компонентов — страницы сайта из `components.py` и `subcomponents.py` (PLAN этапы 3–4); синхронизированы с [AD-17](../architecture/decisions/AD-17.yaml)–[AD-19](../architecture/decisions/AD-19.yaml), схемы спек пересобраны | PLAN этапы 3–4 | — (документация) |
| ✅ | Перенос спек в `openspec/specs/`: решено — архивация каждого change после реализации и приёмки его задач (правило), раздел «Архивация» в `tasks.md`; `tasks.md` всех изменений собраны из ROADMAP; проверка ссылок и `validate --strict` — в сборке | PLAN этапы 5–7 | — (документация) |

Отложенное — в [BACKLOG.md](BACKLOG.md).
