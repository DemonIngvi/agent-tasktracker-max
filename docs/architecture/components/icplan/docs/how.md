Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/icplan.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в [архитектуре](..\..\..\..\source\architecture.md).

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Пользователь двигает задачу по доске | Пользователь → Task UI → [ICPlan](../README.md) | колонка задачи | — | С1 |
| 2 | Автоподхват: агент шага становится делегатом | [ICPlan](../README.md) → [ICPlan](../README.md) | `delegateUserId` задачи | — | С1 |
| 3 | Запуск в очередь | [ICPlan](../README.md) → БД [ICPlan](../README.md) | [`Run`](../../../data/model-Run.yaml) (pending) | — | С1 |
| 4 | Runner забирает запуск | [Agent Runner](../../agent-runner/README.md) → [ICPlan](../README.md) | [`Run`](../../../data/model-Run.yaml) | [I1](../../agent-runner/integrations/I1.yaml) | С1 |
| 4а | Runner берёт определение и настройки версии запуска ([AD-23](../../../decisions/AD-23.yaml)) | [Agent Runner](../../agent-runner/README.md) → [Platform module](../../platform-module/README.md) (в api [ICPlan](../README.md)) | `{version, definition: AgentDefinition, settings: AgentSettings}` | [I4](../../agent-runner/integrations/I4.yaml) | С1 |
| 5 | Ход работы агента в чат задачи | [Agent Runner](../../agent-runner/README.md) → [ICPlan](../README.md) → Task UI | [`RunEvent`](../../../data/model-RunEvent.yaml) → чат запуска | [I2](../../agent-runner/integrations/I2.yaml) | С1 |
| 6 | Подтверждение действия | Пользователь → Task UI → [ICPlan](../README.md) → [Agent Runner](../../agent-runner/README.md) (ответ heartbeat) | [`ApprovalDecision`](../../../data/model-ApprovalDecision.yaml) | [I20](../integrations/I20.yaml), [I3](../../agent-runner/integrations/I3.yaml) | С1 |
| 7 | Итог в задачу | [Agent Runner](../../agent-runner/README.md) → [ICPlan](../README.md) | [`RunResult`](../../../data/model-RunResult.yaml) | [I2](../../agent-runner/integrations/I2.yaml) | С1 |
| 8 | Переход задачи по итогу запуска | [ICPlan](../README.md) → [ICPlan](../README.md) | `process_step.on_success / on_failure` | — | С1 |
| 9 | Администратор настраивает агента | Администратор → Control Plane UI → [ICPlan](../README.md) | [`AgentDefinition`](../../../data/model-AgentDefinition.yaml) | [I20](../integrations/I20.yaml) | — |
| 10 | Агент работает с задачей через MCP | MCP-прокси [Agent Runner](../../agent-runner/README.md) → MCP itsaplan-core | [`McpToolCall`](../../../data/model-McpToolCall.yaml) | [I24](../../agent-runner/integrations/I24.yaml) | — |

#### С1. Задача проходит шаг процесса

{{seq:seq-icplan-1}}

