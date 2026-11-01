Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/observability.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в [архитектуре](..\..\..\..\source\architecture.md).

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Шаги запуска | [Harness](../../harness/README.md) → [Agent Runner](../../agent-runner/README.md) → [ICPlan](../../icplan/README.md) (БД) | [`RunEvent`](../../../data/model-RunEvent.yaml) | [I7](../../agent-runner/integrations/I7.yaml), [I2](../../agent-runner/integrations/I2.yaml) | С1 |
| 2 | Решения guardrails | [Agent Runner](../../agent-runner/README.md), [Harness](../../harness/README.md) → [ICPlan](../../icplan/README.md) (БД) | [`RunEvent`](../../../data/model-RunEvent.yaml) (`CUSTOM` `guardrail_decision`) | [I2](../../agent-runner/integrations/I2.yaml) | — |
| 3 | Затраты | LLM Gateway → журнал затрат → агрегаты | токены, $, `run_id` | [I14](../../llm-gateway/integrations/I14.yaml) | С1 |
| 4 | Чат запуска в задаче | БД и живой поток → панель «Агент» | [`RunEvent`](../../../data/model-RunEvent.yaml) (AG-UI), поток | [I20](../../icplan/integrations/I20.yaml) | С1 |
| 5 | Затраты задачи | агрегаты → Task UI | [`CostAggregate`](../../../data/model-CostAggregate.yaml) | [I20](../../icplan/integrations/I20.yaml) | С1 |
| 6 | Очистка по сроку | БД | события старше срока; агрегаты остаются | — | — |

#### С1. Шаг агента и затраты в задаче

{{seq:seq-observability-1}}

