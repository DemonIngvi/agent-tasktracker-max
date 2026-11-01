Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/llm-gateway.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в [архитектуре](..\..\..\..\source\architecture.md).

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Запрос к модели по алиасу | [Harness](../../harness/README.md) → LLM Gateway | [`ChatCompletionRequest`](../../../data/model-ChatCompletionRequest.yaml), virtual key агента | [I8](../../harness/integrations/I8.yaml) | С1 |
| 2 | Проверка бюджета и rate limit | LLM Gateway → LLM Gateway | ключ, лимиты | — | С1 |
| 3 | Проверки G4 | хуки LLM Gateway | вход и ответ | — | С1 |
| 4 | Маршрут к модели | LLM Gateway → провайдер / mock | запрос провайдера | [I13](../integrations/I13.yaml) | С1 |
| 5 | Резервная модель при сбое | LLM Gateway → резервный провайдер | тот же запрос | [I13](../integrations/I13.yaml) | С1 |
| 6 | Учёт затрат | LLM Gateway → БД `litellm` → [Observability](../../observability/README.md) | токены, $, `run_id` | [I14](../integrations/I14.yaml) | С1 |
| 7 | Выдача virtual key и бюджетов | [Platform module](../../platform-module/README.md) → LLM Gateway | [`VirtualKey`](../../../data/model-VirtualKey.yaml) | [I15](../../platform-module/integrations/I15.yaml) | — |

#### С1. Вызов модели

{{seq:seq-llm-gateway-1}}

