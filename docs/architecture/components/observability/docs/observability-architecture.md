# observability — схема

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
  b1["<b>Harness · Event stream</b><br/><small>шаги</small>"]:::ext
  b2["<b>LiteLLM · Spend log</b><br/><small>токены и $</small>"]:::ext
  b3["<b>Guardrails · аудит</b><br/><small>срабатывания</small>"]:::ext
  subgraph z4["Observability (MVP)"]
    b5["<b>События запуска</b><br/><small>таблица в БД ICPlan, срок хранения</small>"]:::todo
    b6["<b>Агрегаты затрат</b><br/><small>запуск, задача, агент, модель</small>"]:::todo
  end
  class z4 zone
  b1 -->|"через Agent Runner"| b5
  b1 ~~~ b6
  b7["<b>Чат запуска в задаче</b><br/><small>ICPlan Task UI</small>"]:::ext
  b8["<b>Затраты в задаче</b><br/><small>ICPlan Task UI</small>"]:::ext
  b5 --> b7
  b5 ~~~ b8
  b9["<b>Langfuse (бэклог)</b><br/><small>evals, анализ промптов</small>"]:::back
  b10["<b>Prometheus / Grafana / Loki (бэклог)</b><br/><small>метрики и логи</small>"]:::back
  b7 -->|"бэклог"| b9
  b7 ~~~ b10
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| События запуска | таблица в БД [ICPlan](../../icplan/README.md), срок хранения | ⬜ не начато |
| Агрегаты затрат | запуск, задача, агент, модель | ⬜ не начато |
| Langfuse | evals, анализ промптов | бэклог |
| Prometheus / Grafana / Loki | метрики и логи | бэклог |

## Настройка

Параметры модуля — [interfaces.md](observability-interfaces.md) (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Чат запуска работы агента в задаче | Объём событий при `events.level: всё` (решение владельца) — ~250 МБ/день; маскирование до записи, срок 90 дней. |
| Затраты по задаче и агенту | Соглашения OTel GenAI в статусе Development — версию фиксируем при экспорте. |
| Разбор отказов guardrails | Пересмотр: разработчикам нужен разбор промптов на каждом запуске → Langfuse или Phoenix. |

Обоснование: [R&D](..\..\..\..\research\observability.md).
