Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/mcp-tools.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в [архитектуре](..\..\..\..\source\architecture.md).

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | Правило | I | Сценарий |
|---|---|---|---|---|---|---|
| 1 | Список тулов агенту | MCP-сервер → MCP-прокси [Agent Runner](../../agent-runner/README.md) → [Harness](../../harness/README.md) | тулы, отфильтрованные allowlist запуска ([AD-19](../../../decisions/AD-19.yaml)) | R3 | [I9](../../harness/integrations/I9.yaml) | С1 |
| 2 | Вызов тула | [Harness](../../harness/README.md) → MCP-прокси [Agent Runner](../../agent-runner/README.md) → MCP-сервер | [`McpToolCall`](../../../data/model-McpToolCall.yaml) | R2 | [I9](../../harness/integrations/I9.yaml), [I24](../../agent-runner/integrations/I24.yaml) | С1 |
| 3 | Проверка перед вызовом | [Harness](../../harness/README.md), затем MCP-прокси → [Guardrails](../../guardrails/README.md) | [`PolicyInput`](../../../data/model-PolicyInput.yaml) G2 | — | [I10](../../harness/integrations/I10.yaml) | С1 |
| 4 | Работа с задачей | MCP itsaplan-core внутри api [ICPlan](../../icplan/README.md) | задача, комментарий, поля задачи | R3 | [I24](../../agent-runner/integrations/I24.yaml) | С1 |
| 5 | Работа с кодом | MCP git → git-провайдер | ветка, PR | R3 | — | — |
| 6 | Запись памяти | нативный тул [Harness](../../harness/README.md) → [Memory](../../memory/README.md) | [`M3Record`](../../../data/model-M3Record.yaml) | R4 | [I11](../../harness/integrations/I11.yaml) | — |
| 7 | Внутренние вызовы платформы | сервис → сервис | REST, не MCP | R7 | — | — |

#### С1. Вызов тула itsaplan-core

{{seq:seq-mcp-tools-1}}

