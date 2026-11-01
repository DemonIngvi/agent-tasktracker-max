Порядок работы компонента: что за чем происходит внутри и с соседями (источник — `docs/how/harness.md`, на сайте — вкладка «Архитектура» компонента). Поля данных — в контрактах на вкладке «Интеграции» компонента, таблицы — на вкладке «Данные», стороны и протоколы — в карточках «Интеграций», сквозной сценарий — в [архитектуре](..\..\..\..\source\architecture.md).

### Порядок работы и сценарии

#### Порядок работы

| # | Поток | Участники | Данные | I | Сценарий |
|---|---|---|---|---|---|
| 1 | Задание | [Agent Runner](../../agent-runner/README.md) → [Harness](../README.md) | [`RunBundle`](../../../data/model-RunBundle.yaml) | [I7](../../agent-runner/integrations/I7.yaml) | С1 |
| 2 | Сборка контекста: инструкция, навыки, M3, M2 | [Harness](../README.md) → [Memory](../../memory/README.md) | [`M3Record`](../../../data/model-M3Record.yaml), итоги запусков | [I11](../integrations/I11.yaml) | С1 |
| 3 | Вызов модели | [Harness](../README.md) → LLM Gateway | [`ChatCompletionRequest`](../../../data/model-ChatCompletionRequest.yaml) | [I8](../integrations/I8.yaml) | С1 |
| 4 | Проверка действия (G2) | [Harness](../README.md) → [Guardrails](../../guardrails/README.md) | [`PolicyInput`](../../../data/model-PolicyInput.yaml) → [`PolicyDecision`](../../../data/model-PolicyDecision.yaml) | [I10](../integrations/I10.yaml) | С1 |
| 5 | Вызов тула | [Harness](../README.md) → MCP-прокси [Agent Runner](../../agent-runner/README.md) → MCP-сервер | [`McpToolCall`](../../../data/model-McpToolCall.yaml) | [I9](../integrations/I9.yaml) | С1 |
| 6 | Пауза на подтверждение | [Harness](../README.md) → [Agent Runner](../../agent-runner/README.md) → [ICPlan](../../icplan/README.md) | [`RunEvent`](../../../data/model-RunEvent.yaml) (`CUSTOM` `approval_request`) | [I7](../../agent-runner/integrations/I7.yaml), [I2](../../agent-runner/integrations/I2.yaml) | С1 |
| 7 | Сохранение шага | [Harness](../README.md) → [Agent Runner](../../agent-runner/README.md) (checkpointer) | [`Checkpoint`](../../../data/model-Checkpoint.yaml) | [I12](../integrations/I12.yaml) | С1 |
| 8 | Шаги работы | [Harness](../README.md) → [Agent Runner](../../agent-runner/README.md) | [`RunEvent`](../../../data/model-RunEvent.yaml) | [I7](../../agent-runner/integrations/I7.yaml) | С1 |
| 9 | Итог | [Harness](../README.md) → [Agent Runner](../../agent-runner/README.md) | [`RunResult`](../../../data/model-RunResult.yaml) | [I7](../../agent-runner/integrations/I7.yaml) | С1 |

#### С1. Шаг цикла с вызовом тула

{{seq:seq-harness-1}}

### Цикл


```mermaid
flowchart TD
  A[RunBundle] --> B[Bootstrap] --> C[Context Manager] --> D[LLM client]
  D --> E{tool_calls?}
  E -- нет --> F[RunResult]
  E -- да --> G{hook before_tool G2}
  G -- allow --> T[Tool Executor MCP]
  G -- confirm --> P[пауза interrupt] --> Q[ApprovalDecision] --> T
  G -- deny --> X[отказ в контекст] --> C
  T -- результат --> C
```

### Сборка запроса к модели {#llm-request}


Что уходит в модель на каждом шаге, откуда это берётся и кто это меняет. Требование — R-HRN «Сборка запроса к модели»; параметры — [таблица параметров Harness](agent-harness-interfaces.md).

```mermaid
flowchart LR
  classDef box fill:#f5f5f5,stroke:#9e9e9e,color:#212121
  subgraph MS["messages"]
    direction TB
    m1["1 системный промпт платформы — образ Harness, L0"]:::box
    m2["2 руководство проекта — Platform module, L1"]:::box
    m3["3 инструкция + навыки агента — Registry ICPlan, L2, M5"]:::box
    m4["4 тулы и рабочее пространство — RunBundle, L2 + политика"]:::box
    m5["5 контекст памяти M1, M2, M3 — Memory API"]:::box
    m6["6 задание запуска — задача ICPlan, L3"]:::box
    m7["7 указания пользователя — чат / комментарий, L3"]:::box
    m8["8 рабочий контекст M0 — шаги цикла, вывод тулов"]:::box
    m1 ~~~ m2 ~~~ m3 ~~~ m4 ~~~ m5 ~~~ m6 ~~~ m7 ~~~ m8
  end
  subgraph PR["параметры"]
    p1["model (алиас) · temperature · top_p<br/>max_output_tokens · reasoning_*<br/>tool_choice · response_format"]:::box
  end
  subgraph SV["служебное"]
    s1["metadata: run_id, issue, agent, project<br/>virtual key · stream, timeout<br/>cache префикса"]:::box
  end
  H[Harness] -->|I8| L["LiteLLM: бюджет, лимиты, G4, учёт"] -->|I13| P["провайдер / mock"]
  MS --> H
  PR --> H
  SV --> H
```

### Слои промпта

| # | Слой | Тип данных | Откуда | Где хранится | Кто меняет | Когда меняется | В кэше префикса |
|---|---|---|---|---|---|---|---|
| 1 | Системный промпт платформы: правила безопасности, формат итога, работа с тулами и памятью | промпт | образ [Harness](../README.md) | git платформы (S8), версия `prompt.platform_version` | разработчик платформы | новым образом [Harness](../README.md) | да |
| 2 | Руководство проекта | промпт | [Platform module](../../platform-module/README.md) | S2, `prompt.guidance` | администратор | со следующего запуска | да |
| 3 | Инструкция и навыки агента (M5) | промпт | Registry [ICPlan](../../icplan/README.md) | S1, версия определения агента | администратор | со следующего запуска | да |
| 4 | Описание тулов (схемы) и рабочего пространства | конфигурация | [`RunBundle`](../../../data/model-RunBundle.yaml) (Runner), MCP `tools/list` | S1, политика доступа S2 | администратор | со следующего запуска | да |
| 5 | Контекст памяти: переписка M1, итоги M2, состояние M3 | контекст памяти | [Memory](../../memory/README.md) API | S1, S4 | [ICPlan](../../icplan/README.md), Runner, агент ([потоки памяти](..\..\memory\docs\how.md)) | каждый запуск | нет |
| 6 | Задание: задача, критерии приёмки, заметка возврата, итог прошлого шага | промпт | [ICPlan](../../icplan/README.md) ([`Run`](../../../data/model-Run.yaml)) | S1 | пользователь | каждый запуск | нет |
| 7 | Указания пользователя во время работы | промпт | [ICPlan](../../icplan/README.md) → Runner (heartbeat) | S1 (M1) | пользователь | во время запуска | нет |
| 8 | Рабочий контекст M0: ответы модели, вызовы и вывод тулов | ответы модели и тулов | [Harness](../README.md) | только память запуска | [Harness](../README.md) | каждый шаг | нет |

Порядок задаёт приоритет: нижний слой не отменяет правила слоя 1 (защита от prompt injection в задаче и выводе тулов).

### Параметры запроса

Откуда [Harness](../README.md) берёт каждое поле запроса. Уровни, значения и границы параметров — в [interfaces.md спеки Harness](agent-harness-interfaces.md), поля запроса — в модели [`ChatCompletionRequest`](../../../data/model-ChatCompletionRequest.yaml).

| Поле запроса (OpenAI-совместимое) | Откуда берётся |
|---|---|
| `model` | `agent.model` (алиас) |
| `temperature`, `top_p` | `model.temperature`, `model.top_p` |
| `max_tokens` | `model.max_output_tokens` (не больше остатка `limits.max_tokens`) |
| `reasoning_effort` / `thinking.budget_tokens` | `model.reasoning_effort`, `model.reasoning_budget_tokens` |
| `tools`, `tool_choice`, `parallel_tool_calls` | набор тулов агента, `model.tool_choice`, `model.parallel_tool_calls` |
| `response_format` | `model.response_format` |
| `stream`, `timeout` | всегда `true`; `request.timeout_s` |
| `metadata` | `run_id`, `issue_key`, `agent` — атрибуция затрат ([FR-136](../../llm-gateway/prd.md)) |
| ключ (`Authorization`) | virtual key агента |

Неподдерживаемые моделью параметры LiteLLM отбрасывает (`drop_params: true`); токены размышлений входят в бюджет запуска; текст размышлений не пишется в события, кроме `events.level: всё`.

### Пример

Запрос [`ChatCompletionRequest`](../../../data/model-ChatCompletionRequest.yaml) со слоями промпта (поля сверяются с моделью при сборке):

```json
{ "model": "team-default",
  "messages": [
    { "role": "system", "content": "<1 правила платформы v1.3>\n<2 руководство проекта>\n<3 инструкция агента v5 + навыки>" },
    { "role": "user", "content": "<6 задание MKT-42: описание, критерии приёмки, итог прошлого шага>\n<5 контекст: M3, итоги M2>" }
  ],
  "tools": [ { "type": "function", "function": { "name": "itsaplan_get_issue", "parameters": { "type": "object" } } } ],
  "tool_choice": "auto", "parallel_tool_calls": false,
  "temperature": 0.2, "max_tokens": 8192, "reasoning_effort": "medium",
  "stream": true,
  "metadata": { "run_id": 1042, "issue_key": "MKT-42", "agent": "analyst" } }
```
