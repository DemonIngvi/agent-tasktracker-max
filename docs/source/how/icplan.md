Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/icplan.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в архитектуре.

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Пользователь двигает задачу по доске | Пользователь → Task UI → ICPlan | колонка задачи | — | С1 |
| 2 | Автоподхват: агент шага становится делегатом | ICPlan → ICPlan | `delegateUserId` задачи | — | С1 |
| 3 | Запуск в очередь | ICPlan → БД ICPlan | `Run` (pending) | — | С1 |
| 4 | Runner забирает запуск | Agent Runner → ICPlan | `Run` | I1 | С1 |
| 4а | Runner берёт определение и настройки версии запуска (AD-23) | Agent Runner → Platform module (в api ICPlan) | `{version, definition: AgentDefinition, settings: AgentSettings}` | I4 | С1 |
| 5 | Ход работы агента в чат задачи | Agent Runner → ICPlan → Task UI | `RunEvent` → чат запуска | I2 | С1 |
| 6 | Подтверждение действия | Пользователь → Task UI → ICPlan → Agent Runner (ответ heartbeat) | `ApprovalDecision` | I20, I3 | С1 |
| 7 | Итог в задачу | Agent Runner → ICPlan | `RunResult` | I2 | С1 |
| 8 | Переход задачи по итогу запуска | ICPlan → ICPlan | `process_step.on_success / on_failure` | — | С1 |
| 9 | Администратор настраивает агента | Администратор → Control Plane UI → ICPlan | `AgentDefinition` | I20 | — |
| 10 | Агент работает с задачей через MCP | MCP-прокси Agent Runner → MCP itsaplan-core | `McpToolCall` | I24 | — |

#### С1. Задача проходит шаг процесса

```mermaid
sequenceDiagram
  autonumber
  actor U as Пользователь
  participant UI as Task UI
  participant IC as ICPlan (api)
  participant PM as Platform module (в api ICPlan)
  participant DB as БД ICPlan
  participant R as Agent Runner
  Note over R,IC: Runner — Bearer API-ключ агента
  U->>UI: двигает задачу по доске
  UI->>IC: PATCH /issues/:issueId (колонка)
  IC->>IC: автоподхват: делегат = агент шага (delegateUserId)
  IC->>DB: запуск в очередь — Run (pending)
  R->>IC: POST /agent-runs/claim (I1)
  IC-->>R: Run ↩
  R->>PM: GET /platform/runs/:runId/agent (I4, AD-23)
  PM->>DB: agent_run.agent_version при первом вызове
  PM-->>R: version, definition, settings ↩
  loop пока агент работает
    R->>IC: POST /agent-runs/:runId/events — RunEvent (I2)
    IC-->>UI: SSE: шаги в чат запуска
    R->>IC: POST /agent-runs/:runId/heartbeat (I3)
  end
  opt нужно подтверждение
    U->>UI: approve / отклонить
    UI->>IC: POST /agent-runs/:runId/decisions — ApprovalDecision
    IC->>DB: agent_run_delivery
    IC-->>R: ApprovalDecision в ответе heartbeat ↩ (после доработки, FR-10)
  end
  R->>IC: POST /agent-runs/:runId/result — RunResult (I2)
  alt успех
    IC->>IC: переход по process_step.on_success
  else ошибка или лимит
    IC->>IC: переход по process_step.on_failure, уведомление владельцу процесса
  end
  IC-->>UI: карточка итога в чате запуска
```

