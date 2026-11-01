# agent-harness — схема

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
  b1["<b>Agent Runner</b><br/><small>задание + определение агента</small>"]:::ext
  subgraph z2["Harness (LangGraph) [G2]"]
    b3["<b>Bootstrap</b><br/><small>определение агента (YAML / ICPlan), скиллы, лимиты</small>"]:::todo
    b4["<b>Context Manager</b><br/><small>промпт, сжатие истории, M0 + M2/M3</small>"]:::todo
    b5["<b>LLM client</b><br/><small>только через LiteLLM, алиас модели</small>"]:::todo
    b6["<b>Tool Executor</b><br/><small>MCP через прокси Runner, allowlist, таймауты</small>"]:::todo
    b3 --> b4
    b3 ~~~ b5
    b3 ~~~ b6
    b7["<b>Hooks [G2]</b><br/><small>before/after llm и tool, on_stop</small>"]:::todo
    b8["<b>Pause / resume</b><br/><small>interrupt на approve и вопрос, checkpoint через Runner (I12)</small>"]:::todo
    b9["<b>Policy / stop</b><br/><small>лимиты шагов, времени, токенов</small>"]:::todo
    b4 -->|"↺ цикл: context → llm → tools → context"| b7
    b4 ~~~ b8
    b4 ~~~ b9
    b10["<b>Event stream</b><br/><small>шаги для чата запуска</small>"]:::todo
    b7 --> b10
  end
  class z2 zone
  b1 --> b3
  b11["<b>LiteLLM gateway</b><br/><small>модели</small>"]:::ext
  b12["<b>MCP / Tools</b><br/><small>действия</small>"]:::ext
  b13["<b>Memory</b><br/><small>M1–M6</small>"]:::ext
  b14["<b>Guardrails</b><br/><small>OPA для G2</small>"]:::ext
  b10 --> b11
  b10 ~~~ b12
  b10 ~~~ b13
  b10 ~~~ b14
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Bootstrap | определение агента (YAML / ICPlan), скиллы, лимиты | ⬜ не начато |
| Context Manager | промпт, сжатие истории, M0 + M2/M3 | ⬜ не начато |
| LLM client | только через LiteLLM, алиас модели | ⬜ не начато |
| Tool Executor | MCP через прокси Runner, allowlist, таймауты | ⬜ не начато |
| Hooks | before/after llm и tool, on_stop | ⬜ не начато |
| Pause / resume | interrupt на approve и вопрос, checkpoint через Runner (I12) | ⬜ не начато |
| Policy / stop | лимиты шагов, времени, токенов | ⬜ не начато |
| Event stream | шаги для чата запуска | ⬜ не начато |

## Настройка

Параметры модуля — interfaces.md (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Approve и возобновление без своего механизма | Частые изменения API LangChain — версия закреплена (1.2.14), LangGraph за своим интерфейсом. |
| Долгие задачи переживают падение процесса | Пересмотр: прототип 1.3.9 покажет, что OpenAI Agents SDK проходит AG1–AG5 не хуже при меньшем коде. |
| Шаги агента видны в задаче по мере работы |  |

Обоснование: R&D.
