# control-plane — схема

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
  b1["<b>Control Plane UI</b><br/><small>экраны настроек в ICPlan</small>"]:::ext
  subgraph z2["Platform module (модуль ICPlan)"]
    b3["<b>API модуля</b><br/><small>проверка прав, валидация, версии</small>"]:::todo
    b4["<b>Алиасы LLM</b><br/><small>алиас → модель</small>"]:::todo
    b5["<b>Бюджеты</b><br/><small>лимиты токенов и $ на агента</small>"]:::todo
    b6["<b>Профили sandbox</b><br/><small>образ, CPU/RAM, сеть</small>"]:::todo
    b3 --> b4
    b3 ~~~ b5
    b3 ~~~ b6
    b7["<b>Профили памяти</b><br/><small>уровни, области, сроки</small>"]:::todo
    b8["<b>Данные guardrails</b><br/><small>allowlist, лимиты для OPA</small>"]:::todo
    b9["<b>Версии агентов</b><br/><small>история, экспорт/импорт YAML</small>"]:::todo
    b4 --> b7
    b4 ~~~ b8
    b4 ~~~ b9
    b10[("<b>Схема platform в БД ICPlan</b><br/><small>отдельная схема — проще слияние с upstream</small>")]:::store
    b7 --> b10
  end
  class z2 zone
  b1 -->|"CRUD"| b3
  b11["<b>Agent Runner</b><br/><small>профили, бюджеты (G1)</small>"]:::ext
  b12["<b>LiteLLM gateway</b><br/><small>алиасы, virtual keys</small>"]:::ext
  b13["<b>Guardrails</b><br/><small>данные правил</small>"]:::ext
  b10 -->|"читают настройки"| b11
  b10 ~~~ b12
  b10 ~~~ b13
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| API модуля | проверка прав, валидация, версии | ⬜ не начато |
| Алиасы LLM | алиас → модель | ⬜ не начато |
| Бюджеты | лимиты токенов и $ на агента | ⬜ не начато |
| Профили sandbox | образ, CPU/RAM, сеть | ⬜ не начато |
| Профили памяти | уровни, области, сроки | ⬜ не начато |
| Данные guardrails | allowlist, лимиты для OPA | ⬜ не начато |
| Версии агентов | история, экспорт/импорт YAML | ⬜ не начато |
| Схема platform в БД [ICPlan](../../icplan/README.md) | отдельная схема — проще слияние с upstream | ⬜ не начато |

## Настройка

Параметры модуля — [interfaces.md](control-plane-interfaces.md) (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Одна БД, один UI, одна авторизация | Ошибочная правка в интерфейсе — версии и откат ([FR-55](../prd.md)), журнал изменений. |
| Все настройки агента в одном месте рядом с ним | Пересмотр: агентов начнут создавать разработчики в репозиториях чаще, чем администраторы в интерфейсе. |
| Каждый параметр меняет поведение агента без кода и деплоя |  |

Обоснование: [R&D](..\..\..\..\research\config-storage.md).
