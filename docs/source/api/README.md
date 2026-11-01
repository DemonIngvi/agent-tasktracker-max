# Каталог API

← Справка · типы данных · сборка запроса к модели

Все API, которые нужны историям: что уже есть в ICPlan, что дорабатываем в форке и что делаем в сервисах платформы. У каждого вызова — кто вызывает, аутентификация, истории, требования и интерфейс (I-код).

<div class="api-legend"><span class="st st-ok">✅ есть</span> <span class="st st-fork">🛠 доработка форка</span> <span class="st st-new">🆕 новое</span></div>

| Компонент | Базовый адрес | Аутентификация | ✅ | 🛠 | 🆕 |
|---|---|---|---|---|---|
| ICPlan (форк) | `https://<домен>/api` (api ICPlan, порт 3000) | UI — сессия пользователя; агент и Runner — `Authorization: Bearer <ключ агента>` | 35 | 11 | 0 |
| Platform module | `/api/platform` (в api форка ICPlan) | UI — сессия администратора; Runner — сервисный токен | 0 | 0 | 10 |
| Agent Runner ↔ Harness | Harness: `http://<sandbox>:8090`; Runner: `http://agent-runner:8080` | одноразовый токен запуска `RUN_TOKEN` | 0 | 0 | 9 |
| Memory API | `http://memory-api:8085` | токен запуска (Harness), сервисный токен (администрирование) | 0 | 0 | 4 |
| LiteLLM gateway | `http://litellm:4000` | virtual key агента; админ — master key | 3 | 0 | 1 |
| Guardrails (OPA) | `http://opa:8181` | внутренняя сеть (mTLS — этап 4) | 3 | 0 | 0 |
| Sandbox | своего API нет: среду создаёт Runner | — | 3 | 0 | 0 |
| Harness | см. Agent Runner ↔ Harness | токен запуска | 0 | 0 | 1 |
| MCP / Tools | MCP-серверы по протоколу MCP (streamable HTTP) | ключ агента / секрет сервера | 2 | 0 | 0 |
| Observability | в api ICPlan | сессия | 1 | 0 | 0 |
| Инфраструктура | ingress Traefik | TLS | 2 | 0 | 0 |

## Модели данных

Основные объекты, которыми обмениваются компоненты.

### Run

_выдача запуска (`/agent-runs/claim`)_

```json
{ "run": { "id": 1042, "trigger": "process_step", "attempts": 0,
          "prompt": "Work item MKT-42 has been delegated to you…", "systemPrompt": "You are running as agent analyst…",
          "issueId": 318, "issueIdentifier": "MKT-42",
          "rule": { "process": "Фича", "stepId": "sdd" } } }
```

### RunBundle

_Runner → Harness (`POST /run`)_

```json
{ "runId": 1042, "agent": { "agentId": 7, "model": "team-default", "version": 5, "instructions": "…", "skills": ["…"] },
  "prompt": "Work item MKT-42…", "systemPrompt": "You are running as agent analyst…",
  "guidance": "…", "params": { "model.temperature": 0.2, "limits.max_steps": 30 },
  "workspace": [ { "name": "repo", "type": "git", "url": "…", "branch": "agent/MKT-42", "right": "write" },
                 { "name": "task", "type": "folder", "prefix": "projects/MKT/tasks/42/", "right": "read" } ],
  "memory": { "m3": { … }, "m2": [ … ] },
  "task": { "issueId": 318, "issueIdentifier": "MKT-42", "stepId": "sdd",
            "criteria": [ { "text": "…", "origin": "process", "status": "active" }, { "text": "…", "origin": "user:anna", "status": "active" } ],
            "returnNote": null } }
```

### RunEvent

_событие запуска — конверт вокруг события AG-UI (AD-21; `/run/events`, `POST /agent-runs/:runId/events`)_

```json
{ "runId": 1042, "seq": 6, "at": "2026-10-10T12:00:04Z",
  "event": { "type": "TEXT_MESSAGE_END", "messageId": "m-6", "role": "assistant", "delta": "Читаю задачу, чтобы понять границы экспорта." } }
{ "runId": 1042, "seq": 7, "at": "2026-10-10T12:00:05Z",
  "event": { "type": "TOOL_CALL_START", "toolCallId": "tc-7", "toolCallName": "itsaplan_get_issue", "parentMessageId": "m-6" } }
{ "runId": 1042, "seq": 8, "at": "2026-10-10T12:00:09Z",
  "event": { "type": "CUSTOM", "name": "approval_request", "value": { "tool": "git_push", "argsHash": "…", "reason": "push требует подтверждения" } } }
```

Сохранённое сообщение — одно событие на `*_END` с полным текстом в `delta`: дельты `*_CONTENT` идут только в живой поток (SSE).

Соответствие OpenTelemetry GenAI (semconv v1.44.0, статус Development — имена атрибутов сверяются при экспорте; R&D observability):

| `event.type` | Спан или событие OTel | Атрибуты |
|---|---|---|
| `RUN_STARTED` / `RUN_FINISHED` | спан `invoke_agent` (начало / конец) | агент, версия, `runId`; итог и токены — на конце |
| `CUSTOM` `llm_call` | спан `chat` (`gen_ai.operation.name`) | провайдер, модель запроса и ответа, токены ввода, вывода, размышлений |
| `TOOL_CALL_START` … `TOOL_CALL_RESULT` | спан `execute_tool` | имя тула, статус, длительность |
| `CUSTOM` `memory_write` | спан `execute_tool` (тул памяти) | уровень памяти, область |
| `CUSTOM` `approval_request`, `question`, `guardrail_decision` | событие спана `invoke_agent` | решение, точка G, причина |

### RunResult

_итог (`/agent-runs/:id/result`)_

```json
{ "status": "success", "output": "## Требования…", "error": null,
  "usage": { "inputTokens": 18450, "outputTokens": 2210, "reasoningTokens": 900, "costUsd": 0.12, "iterations": 9 },
  "reason": "done", "artifacts": [ { "name": "requirements.md", "url": "s3://…" } ], "gate": { "passed": true, "failed": [] } }
```

### ApprovalDecision

_решение пользователя; `scope` (только для `approve`): `once` — этот вызов, `run` — такие же вызовы до конца запуска (FR-112)_

```json
{ "runId": 1042, "seq": 8, "decision": "approve", "scope": "once", "by": "anna", "comment": null }
```

### UserMessage

_указание во время работы (ответ heartbeat)_

```json
{ "id": "m-91", "text": "используй pytest", "by": "anna", "at": "2026-10-10T12:03:00Z" }
```

### Verdict

_вердикт по результату_

```json
{ "issueId": 318, "stepId": "code", "runId": 1042, "verdict": "rejected", "note": "нет тестов", "by": "lead",
  "criteria": [ { "text": "есть тест на пустой список", "origin": "reviewer:lead", "status": "active" } ] }
```

### Process

_процесс типа задачи_

```json
{ "issueType": "Фича", "owner": "lead", "firstStep": "sdd", "version": 4,
  "steps": [ { "id": "sdd", "column": "SDD", "agentId": 7, "maxRuns": 3, "requireReview": false,
               "deliverable": "spec.md и tasks.md в ветке задачи",
               "doneCriteria": [ { "text": "у каждого требования есть сценарий", "origin": "process", "status": "active" } ],
               "criteriaApproval": "auto",
               "onSuccess": { "step": "code" }, "onFailure": { "step": "help" } },
             { "id": "code", "column": "Код", "agentId": 9, "requireReview": true, "criteriaApproval": "review",
               "onSuccess": { "done": true }, "onFailure": { "step": "help" } },
             { "id": "help", "column": "Нужна помощь", "requireReview": true, "criteriaApproval": "always",
               "onSuccess": { "step": "code" }, "onFailure": { "done": true } } ] }
```

### M3Record

_состояние задачи_

```json
{ "issueId": 318, "scope": "issue", "agentId": 7, "version": 3, "done": ["…"], "next": ["…"], "blockers": ["…"],
  "artifacts": [ { "path": "openspec/changes/mkt-42/spec.md", "ref": "agent/MKT-42@a1b2c3" } ],
  "questions": [ "…" ],
  "criteriaNext": [ { "text": "тест на пустой список", "origin": "agent:analyst", "status": "active" } ] }
```

### PolicyInput / PolicyDecision

_OPA G1 / G2: запрос `{input}` и ответ `{result}`_

```json
{ "input": { "point": "g2", "agentId": 9, "run": { "id": 1042, "issueId": 318, "stepId": "code" }, "tool": "git_push", "argsHash": "…" } }
```

Ответ:

```json
{ "result": { "allow": false, "approval": true, "reason": "push требует подтверждения" } }
```

### AgentDefinition

_определение агента для экспорта и импорта (`GET /platform/agents/:agentId/export`, `POST /platform/agents/import`)_

```yaml
apiVersion: agent/v1
id: analyst
version: 3
model: team-default
instructions: |
  Ты аналитик. По задаче пишешь требования в формате SDD.
skills: [sdd-writer]
mcp:
  - server: itsaplan-core
    tools: [get_issue, add_comment, update_issue]
limits: { max_steps: 30, timeout_s: 1800, max_tokens: 200000 }
approval: { tools: [update_issue] }
memory: { profile: default, read: [M2, M3, M6], write: [M3] }
sandbox: { profile: light }
```

### Heartbeat

_ответ на продление аренды (доработка: сейчас форк отвечает 204 без тела) — подтверждения и указания (I3); отмена — ответ 404, как в форке_

```json
{ "approvals": [ { "runId": 1042, "seq": 8, "decision": "approve", "scope": "once", "by": "anna" } ],
  "messages": [ { "id": "m-91", "text": "используй pytest", "by": "anna", "at": "2026-10-10T12:03:00Z" } ] }
```

### AgentSettings

_настройки агента в Platform module (I4)_

```json
{ "agentId": 7, "version": 5, "autonomy": "R2", "budget": { "runUsd": 1, "dayUsd": 5 },
  "sandboxProfile": "light", "memoryProfile": "default",
  "toolsAllow": ["itsaplan_get_issue", "itsaplan_add_comment", "git_push"], "approvalTools": ["git_push"],
  "scheduling": { "parallel": 1, "max": 3 } }
```

### SandboxClaim

_заявка на среду запуска (I6, I23)_

```json
{ "profile": "light", "sandboxId": "sbx-7f3a", "image": "agent-harness:0.3.1", "runtime": "runc", "cpu": 1, "memoryMb": 1024, "diskGb": 5, "readyMs": 140 }
```

### RepoGrant

_доступ к репозиторию на один запуск (I6, I18)_

```json
{ "repo": "org/app", "access": "write", "branchPrefix": "agent/", "protected": ["main"], "ttlSec": 3600 }
```

### Checkpoint

_состояние цикла Harness (I12, `PUT /runs/{id}/checkpoint`)_

```json
{ "runId": 1042, "iteration": 7, "parentIteration": 6, "state": "<base64>" }
```

### ChatCompletionRequest

_вызов модели через LiteLLM (I8); полный пример со слоями промпта — сборка запроса_

```json
{ "model": "team-default", "messages": [ { "role": "system", "content": "…" }, { "role": "user", "content": "MKT-42: …" } ],
  "tools": [ { "type": "function", "function": { "name": "itsaplan_add_comment", "parameters": { "type": "object" } } } ],
  "temperature": 0.2, "max_tokens": 8192, "stream": true,
  "metadata": { "run_id": 1042, "issue_key": "MKT-42", "agent": "analyst" } }
```

### McpToolCall

_вызов тула через MCP-прокси Runner (I9, JSON-RPC 2.0)_

```json
{ "jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": { "name": "itsaplan_add_comment", "arguments": { "issue": "MKT-42", "body": "Черновик требований готов" } } }
{ "jsonrpc": "2.0", "id": 12, "result": { "content": [ { "type": "text", "text": "ok" } ] } }
```

### VirtualKey

_ключ LiteLLM на агента (I15, `/key/generate`)_

```json
{ "key_alias": "agent:7", "models": ["team-default"], "max_budget": 5, "budget_duration": "1d", "rpm_limit": 30, "tpm_limit": 200000, "metadata": { "agent_id": 7 } }
```

### OpaBundleData

_данные бандла OPA (I16, `data.json`)_

```json
{ "agents": { "7": { "tools_allow": ["itsaplan_get_issue", "git_push"], "approval": ["git_push"], "autonomy": "R2", "budget": { "run_usd": 1, "day_usd": 5 } } },
  "projects": { "12": { "budget": { "month_usd": 100 } } },
  "platform": { "kill_switch": false } }
```

### CostAggregate

_сводка затрат по задаче (экран «Затраты»)_

```json
{ "issueId": 318, "agentId": 7, "runs": 3, "inputTokens": 51200, "outputTokens": 6400, "costUsd": 0.34 }
```
