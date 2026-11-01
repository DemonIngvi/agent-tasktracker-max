# llm-gateway — схема

← spec.md

Схема C3 по FORMAT.md. Цвет: зелёный — есть, жёлтый — частично, серый — не начато; оранжевый пунктир — соседний компонент.

## Схема

```mermaid
flowchart TB
  classDef done fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
  classDef part fill:#fff8e1,stroke:#f9a825,color:#5d4037
  classDef todo fill:#f5f5f5,stroke:#9e9e9e,color:#424242
  classDef ext fill:#fff3e0,stroke:#ef6c00,color:#e65100,stroke-dasharray:4 3
  classDef user fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
  classDef store fill:#ede7f6,stroke:#5e35b1,color:#311b92
  classDef back fill:#fafafa,stroke:#bdbdbd,color:#9e9e9e,stroke-dasharray:2 2
  classDef zone fill:#fafafa,stroke:#9fa8da,color:#1a237e
  b1["<b>Harness · LLM client</b><br/><small>OpenAI-совместимый API</small>"]:::ext
  subgraph z2["LiteLLM [G4]"]
    b3["<b>Virtual keys</b><br/><small>ключ на агента</small>"]:::part
    b4["<b>Бюджеты, rate limit</b><br/><small>отказ до траты</small>"]:::todo
    b5["<b>G4 хуки [G4]</b><br/><small>PII, injection, модерация</small>"]:::todo
    b6["<b>Алиасы</b><br/><small>team-default → модель</small>"]:::part
    b7["<b>Fallback</b><br/><small>резервная модель</small>"]:::todo
    b8["<b>Spend log</b><br/><small>токены и $ по ключу</small>"]:::part
    b3 --> b6
    b3 ~~~ b7
    b3 ~~~ b8
  end
  class z2 zone
  b1 -->|"virtual key агента"| b3
  b1 ~~~ b4
  b1 ~~~ b5
  b9["<b>mock-LLM</b><br/><small>разработка и тесты</small>"]:::todo
  b10[("<b>Anthropic</b>")]:::store
  b11[("<b>OpenAI</b>")]:::store
  b12[("<b>Локальные модели</b>")]:::store
  b6 --> b9
  b6 ~~~ b10
  b6 ~~~ b11
  b6 ~~~ b12
  b13["<b>Observability</b><br/><small>затраты</small>"]:::ext
  b9 -->|"→ spend log"| b13
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Virtual keys | ключ на агента | ⚠️ частично |
| Бюджеты, rate limit | отказ до траты | ⬜ не начато |
| G4 хуки | PII, injection, модерация | ⬜ не начато |
| Алиасы | team-default → модель | ⚠️ частично |
| Fallback | резервная модель | ⬜ не начато |
| Spend log | токены и $ по ключу | ⚠️ частично |
| mock-LLM | разработка и тесты | ⬜ не начато |
| Anthropic | — | — |
| OpenAI | — | — |
| Локальные модели | — | — |

## Настройка

Параметры модуля — [interfaces.md](llm-gateway-interfaces.md) (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Смена модели без изменения агентов | Производительность Python-шлюза — тест 4.8. |
| Контроль и учёт затрат по агенту и задаче | Платные функции LiteLLM (enterprise) — используем только ядро. |
| Mock-LLM для разработки без ключей | Пересмотр: накладные расходы > 50 мс p95 на профиле или нужная функция уйдёт в enterprise → Bifrost. |
| Работа при сбое провайдера |  |

Обоснование: [R&D](..\..\..\..\research\llm-gateway.md).
