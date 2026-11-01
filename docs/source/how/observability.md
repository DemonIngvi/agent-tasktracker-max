Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/observability.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в архитектуре.

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Шаги запуска | Harness → Agent Runner → ICPlan (БД) | `RunEvent` | I7, I2 | С1 |
| 2 | Решения guardrails | Agent Runner, Harness → ICPlan (БД) | `RunEvent` (`CUSTOM` `guardrail_decision`) | I2 | — |
| 3 | Затраты | LLM Gateway → журнал затрат → агрегаты | токены, $, `run_id` | I14 | С1 |
| 4 | Чат запуска в задаче | БД и живой поток → панель «Агент» | `RunEvent` (AG-UI), поток | I20 | С1 |
| 5 | Затраты задачи | агрегаты → Task UI | `CostAggregate` | I20 | С1 |
| 6 | Очистка по сроку | БД | события старше срока; агрегаты остаются | — | — |

#### С1. Шаг агента и затраты в задаче

```mermaid
sequenceDiagram
  autonumber
  actor U as Пользователь
  participant H as Harness
  participant R as Agent Runner
  participant IC as ICPlan (run_event, сводка)
  participant L as LLM Gateway
  participant D as БД litellm
  H-->>R: RunEvent (I7)
  R->>IC: POST /agent-runs/:runId/events (I2)
  IC-->>U: SSE: шаг в чате запуска (I20)
  L->>D: журнал затрат: токены, $, run_id (I14)
  U->>IC: открыть задачу (I20)
  IC->>D: чтение журнала затрат по run_id (I14)
  IC-->>U: CostAggregate по задаче ↩
```

