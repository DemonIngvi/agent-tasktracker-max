# tool-integration — схема

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
  b1["<b>Harness · Tool Executor</b><br/><small>вызывает тулы</small>"]:::ext
  b2["<b>Правила R1–R7</b><br/><small>MCP, нативный тул или прямой вызов</small>"]:::todo
  b1 -->|"решает модель → тул · детерминированное → прямой вызов"| b2
  subgraph z3["MCP-серверы и тулы"]
    b4["<b>itsaplan-core</b><br/><small>задачи, комментарии, документы</small>"]:::done
    b5["<b>git-провайдер</b><br/><small>PR, ревью (Gitea / GitHub)</small>"]:::todo
    b6["<b>memory</b><br/><small>запись M3</small>"]:::todo
    b7["<b>web-research (бэклог)</b><br/><small>интернет</small>"]:::back
    b8["<b>Админ-MCP (бэклог)</b><br/><small>бюджеты, политики — не для рабочих агентов</small>"]:::back
    b4 --> b7
    b4 ~~~ b8
  end
  class z3 zone
  b2 --> b4
  b2 ~~~ b5
  b2 ~~~ b6
  b9["<b>ICPlan</b><br/><small>MCP itsaplan-core</small>"]:::ext
  b10["<b>Agent Runner</b><br/><small>MCP-прокси: allowlist, G2, ключи</small>"]:::ext
  b7 --> b9
  b7 ~~~ b10
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Правила R1–R7 | MCP, нативный тул или прямой вызов | ⬜ не начато |
| itsaplan-core | задачи, комментарии, документы | ✅ есть |
| git-провайдер | PR, ревью (Gitea / GitHub) | ⬜ не начато |
| memory | запись M3 | ⬜ не начато |
| web-research | интернет | бэклог |
| Админ-MCP | бюджеты, политики — не для рабочих агентов | бэклог |

## Настройка

Параметры модуля — interfaces.md (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Новые действия агента без изменения кода | Runner на пути каждого вызова MCP — таймаут 30 с, отказ сервера — ошибка тула (FMEA Runner). |
| Внешние агенты (Claude Code и др.) используют те же тулы | Пересмотр: число тулов агента > 30 — включить поиск тулов. |
| Правила R1–R7 не дают тащить в MCP то, что быстрее прямым вызовом |  |

Обоснование: R&D.
