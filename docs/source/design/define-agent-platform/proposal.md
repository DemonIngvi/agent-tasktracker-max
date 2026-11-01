# Proposal

## Why

Нужна расширяемая платформа для запуска LLM-агентов: агенты добавляются и настраиваются конфигом, без кода; модели, тулы, MCP, промпты, скиллы и память управляются централизованно; каждый запуск изолирован; расход токенов и безопасность контролируются в одной точке. Платформа должна встраиваться в [ICPlan](../../../architecture/components/icplan/README.md), который назначает агента на задачу.

## What Changes

- Вводится **[Agent Runner](../../../architecture/components/agent-runner/README.md)** — исполняет задачу назначенным агентом: поднимает sandbox, контролирует лимиты, возвращает результат, убирает среду. Планирования не делает (это [ICPlan](../../../architecture/components/icplan/README.md)).
- Вводится **Registry** — версионируемый каталог: модели, промпты, скиллы, тулы/MCP, guardrail-правила, определения агентов.
- Вводится **Control Plane** — API (+CLI/UI) управления Registry и просмотра запусков.
- Вводится **[Harness](../../../architecture/components/harness/README.md)** — рантайм агентского цикла внутри sandbox: Context Manager, LLM client, Tool Executor, hooks.
- Вводится **[Sandbox](../../../architecture/components/sandbox/README.md)** — изолированная среда на каждый запуск.
- Вводится **[Memory](../../../architecture/components/memory/README.md) Service** — 4 уровня памяти (L1 рабочая … L4 общая).
- Вводится **Tool integration** — подключение тулов и MCP-серверов к агенту.
- Вводится **[Guardrails](../../../architecture/components/guardrails/README.md)** — единая политика из Registry и 4 точки применения G1–G4.
- Вводится **LLM Gateway** на LiteLLM — единственный выход к моделям, учёт токенов, fallback.
- Вводится **[Observability](../../../architecture/components/observability/README.md)** — трейсы, токены, стоимость по запуску и агенту.

## Capabilities

### New Capabilities
- `agent-runner`: жизненный цикл запуска агента по задаче от [ICPlan](../../../architecture/components/icplan/README.md)
- `agent-registry`: каталог ресурсов и декларативное определение агента
- `control-plane`: API/CLI/UI управления платформой
- `agent-harness`: агентский цикл, контекст, вызов LLM и тулов, hooks
- `agent-sandbox`: изоляция каждого запуска
- `agent-memory`: многоуровневая память агентов
- `tool-integration`: подключение тулов и MCP-серверов
- `guardrails`: политики и точки применения G1–G4
- `llm-gateway`: проксирование к LLM через LiteLLM, учёт токенов
- `observability`: трейсы, токены, стоимость

### Modified Capabilities
<!-- нет: проект новый -->

## Impact

- Новый проект, существующего кода нет.
- Внешние зависимости: LiteLLM, контейнерная среда для sandbox (Docker/K8s — решение в design), SDK харнеса (решение в design), MCP.
- Внешняя интеграция: [ICPlan](../../../architecture/components/icplan/README.md) — только контракт (задача + agent_id → статус/результат); сам [ICPlan](../../../architecture/components/icplan/README.md) вне скоупа.
