Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/platform-module.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в [архитектуре](..\..\..\..\source\architecture.md).

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Администратор меняет настройки агента | Control Plane UI → [Platform module](../README.md) | [`AgentSettings`](../../../data/model-AgentSettings.yaml) | [I20](../../icplan/integrations/I20.yaml) | С1 |
| 2 | Новая версия определения агента | [Platform module](../README.md) → БД | [`AgentDefinition`](../../../data/model-AgentDefinition.yaml) + версия | — | С1 |
| 3 | Runner читает профиль и бюджет перед запуском | [Agent Runner](../../agent-runner/README.md) → [Platform module](../README.md) | [`AgentSettings`](../../../data/model-AgentSettings.yaml) | [I4](../../agent-runner/integrations/I4.yaml) | С1 |
| 4 | Алиасы и бюджеты в LLM Gateway | [Platform module](../README.md) → LLM Gateway | [`VirtualKey`](../../../data/model-VirtualKey.yaml) | [I15](../integrations/I15.yaml) | С1 |
| 5 | Данные правил для OPA | [Platform module](../README.md) → [Guardrails](../../guardrails/README.md) | [`OpaBundleData`](../../../data/model-OpaBundleData.yaml) | [I16](../integrations/I16.yaml) | С1 |
| 6 | Экспорт / импорт агента | Администратор ↔ [Platform module](../README.md) | YAML [`AgentDefinition`](../../../data/model-AgentDefinition.yaml) | [I20](../../icplan/integrations/I20.yaml) | — |

#### С1. Настройки агента: от администратора до запуска

{{seq:seq-platform-module-1}}

