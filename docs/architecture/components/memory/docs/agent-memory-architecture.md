# agent-memory — схема

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
  b1["<b>Harness</b><br/><small>чтение в контекст, запись через тул</small>"]:::ext
  b2["<b>Memory API</b><br/><small>профиль памяти, области видимости, сроки</small>"]:::todo
  b1 --> b2
  subgraph z3["Уровни M0–M6"]
    b4["<b>M0 рабочая</b><br/><small>контекст запуска · Harness</small>"]:::done
    b5["<b>M1 сессионная</b><br/><small>тред · БД ICPlan</small>"]:::done
    b6["<b>M2 эпизодическая</b><br/><small>запуски · agent_run</small>"]:::done
    b7["<b>M3 задачная</b><br/><small>сделано / дальше · БД ICPlan · первой</small>"]:::todo
    b8["<b>M4 семантическая (бэклог)</b><br/><small>pgvector · с RAG</small>"]:::back
    b9["<b>M5 процедурная</b><br/><small>инструкция, навыки</small>"]:::done
    b4 --> b7
    b4 ~~~ b8
    b4 ~~~ b9
    b10["<b>M6 организационная</b><br/><small>документы проекта · get_document</small>"]:::done
    b7 --> b10
  end
  class z3 zone
  b2 --> b4
  b2 ~~~ b5
  b2 ~~~ b6
  b11[("<b>БД ICPlan</b><br/><small>M1, M2, M3, M5</small>")]:::store
  b12[("<b>Документы ICPlan</b><br/><small>M6</small>")]:::store
  b13["<b>pgvector (бэклог)</b><br/><small>M4, позже</small>"]:::back
  b10 --> b11
  b10 ~~~ b12
  b10 ~~~ b13
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Memory API | профиль памяти, области видимости, сроки | ⬜ не начато |
| M0 рабочая | контекст запуска · Harness | ✅ есть |
| M1 сессионная | тред · БД ICPlan | ✅ есть |
| M2 эпизодическая | запуски · agent_run | ✅ есть |
| M3 задачная | сделано / дальше · БД ICPlan · первой | ⬜ не начато |
| M4 семантическая | pgvector · с RAG | бэклог |
| M5 процедурная | инструкция, навыки | ✅ есть |
| M6 организационная | документы проекта · get_document | ✅ есть |
| БД ICPlan | M1, M2, M3, M5 | ✅ есть |
| Документы ICPlan | M6 | ✅ есть |
| pgvector | M4, позже | бэклог |

## Настройка

Параметры модуля — [interfaces.md](agent-memory-interfaces.md) (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Следующий агент продолжает работу, а не начинает заново | Агент не пишет M3 — проверки записи FR-44, напоминание перед завершением. |
| Меньше токенов: в контекст попадает нужное, а не вся история | Пересмотр: для M4 — выбор между Mem0 и LangMem на прототипе после MVP. |
| Агент учится на прошлых запусках (M2) |  |

Обоснование: [R&D](..\..\..\..\research\memory-model.md).
