Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/llm-gateway.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в архитектуре.

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Запрос к модели по алиасу | Harness → LLM Gateway | `ChatCompletionRequest`, virtual key агента | I8 | С1 |
| 2 | Проверка бюджета и rate limit | LLM Gateway → LLM Gateway | ключ, лимиты | — | С1 |
| 3 | Проверки G4 | хуки LLM Gateway | вход и ответ | — | С1 |
| 4 | Маршрут к модели | LLM Gateway → провайдер / mock | запрос провайдера | I13 | С1 |
| 5 | Резервная модель при сбое | LLM Gateway → резервный провайдер | тот же запрос | I13 | С1 |
| 6 | Учёт затрат | LLM Gateway → БД `litellm` → Observability | токены, $, `run_id` | I14 | С1 |
| 7 | Выдача virtual key и бюджетов | Platform module → LLM Gateway | `VirtualKey` | I15 | — |

#### С1. Вызов модели

```mermaid
sequenceDiagram
  autonumber
  participant H as Harness
  participant L as LLM Gateway (LiteLLM)
  participant P as Провайдер / mock
  participant D as БД litellm
  H->>L: POST /v1/chat/completions — ChatCompletionRequest, virtual key (I8)
  L->>L: бюджет и rate limit ключа
  opt G4 включён
    L->>L: хуки: PII, injection, модерация
  end
  L->>P: запрос к модели по алиасу (I13)
  alt сбой провайдера
    P-->>L: ошибка ↩
    L->>P: резервная модель (I13)
  end
  P-->>L: ответ ↩
  L->>D: журнал затрат: токены, $, run_id (I14)
  L-->>H: ответ модели ↩
```

