Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/guardrails.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в [архитектуре](..\..\..\..\source\architecture.md).

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Точка | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|---|
| 1 | Правила (логика) | — | git → бандл OPA | Rego | — | — |
| 2 | Данные правил | — | [Platform module](../../platform-module/README.md) → [Guardrails](../README.md) | [`OpaBundleData`](../../../data/model-OpaBundleData.yaml) | [I16](../../platform-module/integrations/I16.yaml) | — |
| 3 | Включение точек | — | конфиг деплоя → сервисы | `gN.enabled` | — | — |
| 4 | Допуск запуска | G1 | [Agent Runner](../../agent-runner/README.md) → [Guardrails](../README.md) | [`PolicyInput`](../../../data/model-PolicyInput.yaml) → [`PolicyDecision`](../../../data/model-PolicyDecision.yaml) | [I5](../../agent-runner/integrations/I5.yaml) | С1 |
| 5 | Проверка действия; для MCP — повторно в Runner | G2 | [Harness](../../harness/README.md) → [Guardrails](../README.md) | [`PolicyInput`](../../../data/model-PolicyInput.yaml) → [`PolicyDecision`](../../../data/model-PolicyDecision.yaml) | [I10](../../harness/integrations/I10.yaml) | С1 |
| 6 | Изоляция | G3 | профиль → [Sandbox](../../sandbox/README.md) | сеть, ФС, ресурсы | [I6](../../agent-runner/integrations/I6.yaml) | — |
| 7 | Проверка запроса к модели | G4 | хуки LLM Gateway | вход и ответ модели | [I8](../../harness/integrations/I8.yaml) | — |
| 8 | Аудит решений | все | [Agent Runner](../../agent-runner/README.md) → [ICPlan](../../icplan/README.md) | [`RunEvent`](../../../data/model-RunEvent.yaml) (`CUSTOM` `guardrail_decision`) | [I2](../../agent-runner/integrations/I2.yaml) | С1 |

#### С1. Допуск запуска (G1) и проверка действия (G2)

{{seq:seq-guardrails-1}}

