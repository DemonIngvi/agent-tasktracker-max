# agent-registry — схема

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
  b1["<b>Control Plane UI</b><br/><small>настройка агентов</small>"]:::ext
  b2["<b>Platform module</b><br/><small>наши настройки</small>"]:::ext
  subgraph z3["Registry (БД ICPlan)"]
    b4["<b>Агенты</b>"]:::done
    b5["<b>Тулы и навыки</b>"]:::done
    b6["<b>MCP-серверы</b>"]:::done
    b7["<b>Ключи провайдеров</b><br/><small>→ LiteLLM</small>"]:::part
    b8["<b>Версии агента</b>"]:::todo
    b9["<b>Экспорт / импорт YAML</b>"]:::todo
    b4 --> b7
    b4 ~~~ b8
    b4 ~~~ b9
  end
  class z3 zone
  b1 -->|"сохранение"| b4
  b1 ~~~ b5
  b1 ~~~ b6
  b10["<b>Agent Runner</b>"]:::ext
  b11["<b>Harness</b>"]:::ext
  b7 -->|"определение агента"| b10
  b7 ~~~ b11
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Агенты | — | ✅ есть |
| Тулы и навыки | — | ✅ есть |
| MCP-серверы | — | ✅ есть |
| Ключи провайдеров | → LiteLLM | ⚠️ частично |
| Версии агента | — | ⬜ не начато |
| Экспорт / импорт YAML | — | ⬜ не начато |

## Настройка

Параметры модуля — [interfaces.md](agent-registry-interfaces.md) (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Не пишем трекер и UI с нуля — экономия месяцев разработки | Небольшое сообщество (925★): держим свой форк, доработки — модулями. |
| Процесс (статусы, переходы) настраивает сам пользователь, без кода | Стоимость сопровождения форка: каждое слияние с upstream — разбор конфликтов с нашими доработками; объём не оценён. Мера: доработки отдельными модулями и миграциями с префиксом за флагами, общие исправления — PR в upstream (AD-18); время слияний учитываем и при росте выносим на пересмотр. |
| Агенты видны как участники команды: исполнитель, комментарии, история | Пересмотр, если релизов It's a Plan нет больше 6 месяцев или агенты Plane выйдут в Community Edition с внешним исполнителем. |

Обоснование: [R&D](..\..\..\..\research\tracker-choice.md).
