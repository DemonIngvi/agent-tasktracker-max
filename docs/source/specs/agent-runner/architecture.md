# agent-runner — схема

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
  b1["<b>ICPlan · Run Queue</b><br/><small>очередь запусков</small>"]:::ext
  subgraph z2["Agent Runner [G1]"]
    b3["<b>Poller</b><br/><small>забирает запуск из очереди</small>"]:::todo
    b4["<b>Scheduler</b><br/><small>слоты: глобальный, агента, модели, задачи; sequential / parallel</small>"]:::todo
    b5["<b>Admission [G1]</b><br/><small>допуск, бюджет, kill switch</small>"]:::todo
    b6["<b>Sandbox claim</b><br/><small>берёт контейнер из тёплого пула</small>"]:::todo
    b7["<b>Токены репозиториев</b><br/><small>короткоживущие, на запуск</small>"]:::todo
    b3 --> b6
    b3 ~~~ b7
    b8["<b>Run supervisor</b><br/><small>старт Harness, таймаут, отмена</small>"]:::todo
    b9["<b>Event relay</b><br/><small>события Harness → стрим в ICPlan</small>"]:::todo
    b6 --> b8
    b6 ~~~ b9
    b10["<b>MCP-прокси [G2]</b><br/><small>allowlist и G2 вне sandbox, ключи серверов (AD-19)</small>"]:::todo
    b11["<b>Шаг подготовки</b><br/><small>зависимости проекта, кэш по lock-файлам (AD-19)</small>"]:::todo
    b8 --> b10
    b8 ~~~ b11
    b12["<b>Finalizer</b><br/><small>итог в задачу, destroy sandbox</small>"]:::todo
    b10 --> b12
  end
  class z2 zone
  b1 -->|"опрос по ключу агента · стрим и итог"| b3
  b1 ~~~ b4
  b1 ~~~ b5
  b13["<b>Sandbox</b><br/><small>контейнер запуска</small>"]:::ext
  b14["<b>Platform module</b><br/><small>профили, бюджеты</small>"]:::ext
  b15["<b>Observability</b><br/><small>события запуска</small>"]:::ext
  b16["<b>MCP / Tools</b><br/><small>вызовы тулов через прокси (I9)</small>"]:::ext
  b12 --> b13
  b12 ~~~ b14
  b12 ~~~ b15
  b12 ~~~ b16
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Poller | забирает запуск из очереди | ⬜ не начато |
| Scheduler | слоты: глобальный, агента, модели, задачи; sequential / parallel | ⬜ не начато |
| Admission | допуск, бюджет, kill switch | ⬜ не начато |
| Sandbox claim | берёт контейнер из тёплого пула | ⬜ не начато |
| Токены репозиториев | короткоживущие, на запуск | ⬜ не начато |
| Run supervisor | старт Harness, таймаут, отмена | ⬜ не начато |
| Event relay | события Harness → стрим в ICPlan | ⬜ не начато |
| MCP-прокси | allowlist и G2 вне sandbox, ключи серверов (AD-19) | ⬜ не начато |
| Шаг подготовки | зависимости проекта, кэш по lock-файлам (AD-19) | ⬜ не начато |
| Finalizer | итог в задачу, destroy sandbox | ⬜ не начато |

## Настройка

Параметры модуля — interfaces.md (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Каждый запуск изолирован и под контролем лимитов и бюджета | Гонки слотов — конкурентный тест в 2.7. |
| Минимум доработок ICPlan: для него мы — обычный внешний раннер | Пересмотр: на этапе 4 (Kubernetes) — Kueue для ёмкости узлов поверх наших слотов модели. |
| Одна точка, где виден жизненный цикл запуска |  |

Обоснование: R&D.
