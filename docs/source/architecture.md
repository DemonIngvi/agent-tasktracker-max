# Агентная архитектура (v0.9)

Модель C4: **C1** — наша система (Agent Platform) и её связь с ICPlan и внешним миром (ниже). **C2** — карта платформы выше: компоненты и связи между ними. Устройство каждого компонента (C3) — на его вкладке «Архитектура». Схемы — по FORMAT.md.

## C1 — System Context

```mermaid
flowchart LR
  classDef self fill:#c5cae9,color:#1a237e,stroke:#1a237e,stroke-width:3px
  classDef comp fill:#e8eaf6,stroke:#5c6bc0,color:#1a237e
  classDef user fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
  classDef ext fill:#fff3e0,stroke:#ef6c00,color:#e65100,stroke-dasharray:4 3
  U(["Пользователь ICPlan"]):::user
  A(["Администратор платформы"]):::user
  IC["ICPlan<br/><small>задачи, процесс, чат запуска</small>"]:::comp
  P["Agent Platform<br/><small>Runner, Sandbox, Harness, Memory, Guardrails, LLM Gateway</small>"]:::self
  L(["LLM-провайдеры"]):::ext
  X(["Внешние системы, MCP, git"]):::ext
  U -->|"задачи, approve"| IC
  A -->|"агенты, модели, правила"| IC
  P -->|"I1–I3: запуски, события, итог ↩ решения"| IC
  P -->|"I24: тулы ICPlan (MCP)"| IC
  P -->|"I13: запросы к моделям"| L
  P -->|"I17, I18: исходящий трафик, git"| X
```

Интеграция с ICPlan: Agent Runner — внешний раннер ICPlan (забирает запуски, шлёт события и итог, получает решения пользователя в ответе heartbeat). Стыки каждого компонента — вкладка «Интеграции», типы данных и матрица интерфейсов — Справка.

## Взаимодействие компонентов {#interaction}

Сквозной поток MVP: пользователь двигает задачу — агент выполняет — итог возвращается в задачу. Правило оформления — «Порядок работы и сценарии»; порядок работы каждого компонента — раздел «Как работает» на его вкладке «Архитектура».

### Порядок работы и сценарии

#### Порядок работы

| # | Шаг | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Задача вошла в шаг процесса с агентом | ICPlan → ICPlan | `delegateUserId` задачи | — | С1 |
| 2 | Запуск в очередь | ICPlan → БД ICPlan | `Run` (pending) | — | С1 |
| 3 | Runner забирает запуск | Agent Runner → ICPlan | `Run` | I1 | С1 |
| 4 | Допуск и бюджет (G1) | Agent Runner → Guardrails | `PolicyInput` → `PolicyDecision` | I5 | С1 |
| 5 | Среда и задание | Agent Runner → Sandbox, Harness | `SandboxClaim`, `RunBundle` | I6, I7 | С1 |
| 6 | Вызов модели | Harness → LLM Gateway | `ChatCompletionRequest` | I8 | С1 |
| 7 | Действия и память | Harness → MCP-прокси Runner → MCP; Harness → Memory | `McpToolCall`, `M3Record` | I9, I11 | С1 |
| 8 | Шаги работы | Harness → Agent Runner → ICPlan | `RunEvent` | I7, I2 | С1 |
| 9 | Подтверждение | ICPlan → Agent Runner → Harness | `ApprovalDecision` | I3, I7 | С1 |
| 10 | Итог | Harness → Agent Runner → ICPlan | `RunResult` | I7, I2 | С1 |
| 11 | Уничтожение среды | Agent Runner → Sandbox | `sandboxId` | I6 | С1 |
| 12 | Переход задачи по итогу запуска — следующий шаг процесса (снова 1) | ICPlan → ICPlan | `process_step.on_success / on_failure` | — | С1 |

#### С1. Сквозной поток MVP

```mermaid
sequenceDiagram
  autonumber
  actor U as Пользователь
  participant IC as ICPlan
  participant R as Agent Runner
  participant G as Guardrails
  participant H as Sandbox + Harness
  participant L as LLM Gateway
  participant M as MCP / Memory
  U->>IC: двигает задачу
  IC->>IC: агент шага — делегат, запуск в очередь
  R->>IC: POST /agent-runs/claim (I1)
  IC-->>R: Run ↩
  R->>G: PolicyInput G1 (I5)
  G-->>R: PolicyDecision ↩
  R->>H: среда из пула, RunBundle (I6, I7)
  loop шаги агента
    H->>L: ChatCompletionRequest (I8)
    L-->>H: ответ модели ↩
    H->>M: тулы через MCP-прокси Runner, память (I9, I11)
    H-->>R: RunEvent (I7)
    R->>IC: события в чат запуска (I2)
  end
  opt нужно подтверждение
    U->>IC: approve
    IC-->>R: ApprovalDecision в ответе heartbeat ↩ (I3)
    R->>H: ApprovalDecision (I7)
  end
  H-->>R: RunResult (I7)
  R->>IC: итог запуска (I2)
  R->>H: уничтожить среду (I6)
  IC->>IC: переход по итогу запуска (AD-17) — следующий шаг
```

## Развёртывание (C4 deployment)

```mermaid
flowchart LR
  classDef user fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
  classDef ext fill:#fff3e0,stroke:#ef6c00,color:#e65100,stroke-dasharray:4 3
  U(["Пользователи"]):::user -->|"HTTPS (I21)"| T["Traefik — k3s ingress, TLS"]
  subgraph K["Узел k3s (один узел для MVP)"]
    T
    subgraph NC["itsaplan-core"]
      W["web ×1–2 · api ×2 · worker · bot"]
    end
    subgraph NA["itsaplan-agents"]
      AG["Runner · LiteLLM ×2 · OPA ×2 · Memory · egress · запуски"]
    end
    subgraph ND["itsaplan-data"]
      %% databases — генерируется из datamodel.DATABASES (AD-22)
      RF[("RustFS (S3)")]
    end
    T --> W
  end
  PG -->|"копии"| S3[("S3 вне узла")]:::ext
```

Ресурсы узла и профиль нагрузки — R&D: профиль нагрузки, разделы «Нагрузка и производительность» спек. Подробно: спека platform-infrastructure и схема. Технологии — сводная таблица. Обоснование: Kubernetes · ingress · СУБД и хранилища · design AD-15, AD-16.

## Сквозные решения

Что выбрано — одной фразой; почему и подробности — в решении (design) и на странице компонента (правило).

| Решение | Что выбрано | D | Подробно |
|---|---|---|---|
| Агентский цикл | Harness на LangGraph внутри sandbox: модель «думает», остальное — Harness | AD-2 | Harness |
| Guardrails | четыре точки: G1, G2 видят смысл (OPA), G3, G4 не обойти; Rego в git, данные в Platform module | AD-6, AD-19 | Guardrails |
| Очередь и планирование | очередь в ICPlan; Runner стартует запуск, когда свободны все слоты | AD-14 | Agent Runner |
| Исполнение | тёплый пул + одноразовый контейнер на запуск | AD-1 | Sandbox |
| Память | уровни M0–M6, область видимости — атрибут записи; M3 — Memory API | AD-4, AD-20 | Memory |
| RAG | не в MVP: документы — `get_document`, код — агентный поиск | AD-13 | Memory |
| Хранение конфигурации | определения — БД ICPlan; наши настройки — Platform module; Runner получает определение и настройки одной версии у Platform module; экраны — у объекта настройки; Rego — git; перенос — YAML | AD-9, AD-23, AD-24 | Platform module |
| MCP или прямой вызов | правила R1–R7; агент ходит к MCP только через MCP-прокси Runner | AD-10, AD-19 | MCP / Tools |
| Рабочие данные | `/workspace` исчезает со средой; код — ветка и PR; документы — в задачу | AD-11 | Sandbox |
| Observability | события пишутся всегда в формате AG-UI, показываются в задаче чатом запуска | AD-12, AD-18, AD-21 | Observability |
| Ход задачи | процесс задачи: шаг = колонка + агент, переход делает ICPlan по итогу | AD-17 | ICPlan |
| Сроки хранения | срок памяти — фильтр чтения Memory; запуски и переписку удаляет владелец таблиц, ICPlan; журнал задачи живёт с задачей | AD-22, AD-25 | ICPlan |
