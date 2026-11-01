# Интеграции: Agent Runner ↔ Harness

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> Harness: `http://<sandbox>:8090`; Runner: `http://agent-runner:8080`</div>
<div><span class="about-label">Аутентификация</span> одноразовый токен запуска `RUN_TOKEN`</div>
</div>

## Harness (вызывает Runner)

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `/run` | <span class="st st-new">🆕 новое</span> | передать `RunBundle` и начать цикл | Agent Runner · токен запуска | US-RUN-01 | FR-19, FR-29, FR-66 | I7 |
| <span class="m m-get">GET</span> | `/run/events` | <span class="st st-new">🆕 новое</span> | поток `RunEvent` (NDJSON), переподключение с `seq` | Agent Runner · токен запуска | US-ICP-02 | FR-24 | I7 |
| <span class="m m-post">POST</span> | `/run/approval` | <span class="st st-new">🆕 новое</span> | решение пользователя (`ApprovalDecision`) | Agent Runner · токен запуска | US-HAR-02 | FR-23 | I7 |
| <span class="m m-post">POST</span> | `/run/message` | <span class="st st-new">🆕 новое</span> | указание пользователя во время работы | Agent Runner · токен запуска | US-HAR-06 | FR-28 | I7 |
| <span class="m m-post">POST</span> | `/run/cancel` | <span class="st st-new">🆕 новое</span> | отмена | Agent Runner · токен запуска | US-ICP-04 | FR-74 | I7 |
| <span class="m m-get">GET</span> | `/ready` | <span class="st st-new">🆕 новое</span> | готовность среды | Agent Runner · — | US-SBX-01 | FR-83 | I7 |

## Runner (вызывает Harness)

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-put">PUT</span> | `/runs/:runId/checkpoint` | <span class="st st-new">🆕 новое</span> | сохранить состояние цикла | Harness · токен запуска | US-HAR-05 | FR-23 | I12 |
| <span class="m m-get">GET</span> | `/runs/:runId/checkpoint` | <span class="st st-new">🆕 новое</span> | восстановить состояние | Harness · токен запуска | US-HAR-05 | FR-23 | I12 |
| <span class="m m-post">POST</span> | `/runs/:runId/mcp/:server` | <span class="st st-new">🆕 новое</span> | MCP-прокси запуска: `tools/list` с фильтром, `tools/call` с allowlist и G2, учётные данные сервера (AD-19) | Harness · токен запуска | US-MCP-05, US-SBX-03 | FR-177, FR-79 | I9 |
| <span class="m m-post">POST</span> | `/runs/:runId/deps` | <span class="st st-new">🆕 новое</span> | тул `install_dependencies`: повторить шаг подготовки (AD-19) | Harness · токен запуска | US-SBX-05 | FR-29, FR-89 | I7 |
| <span class="m m-get">GET</span> | `/healthz · /readyz` | <span class="st st-new">🆕 новое</span> | здоровье Runner | Kubernetes · — | US-RUN-05 | FR-81 | — |
