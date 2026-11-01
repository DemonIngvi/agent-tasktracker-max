# Интеграции: Observability

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> в api ICPlan</div>
<div><span class="about-label">Аутентификация</span> сессия</div>
</div>

## Где описано

Своего API у Observability нет: затраты задачи (`GET /issues/:issueId/costs`, `CostAggregate`), сводку (`GET /me/agent-summary`) и статистику запусков (`GET /projects/:projectKey/analytics/agent-run-stats`) отдаёт API ICPlan (I20), считая их из журнала LiteLLM, `agent_run` и `run_event`; события запуска Agent Runner передаёт в API ICPlan (I2), собственного приёма у Observability нет. Операции, входы и ошибки — на странице ICPlan.

**Чтение затрат и статистики** (операции ICPlan, полное описание):

| Операция | Что читает | Откуда считается | Требование |
|---|---|---|---|
| `GET /issues/:issueId/costs` | затраты задачи по агентам (`CostAggregate`); модель без цены — токены есть, `costUsd = null` | журнал LiteLLM (I14) | FR-150 |
| `GET /me/agent-summary` | сводка: в работе, в очереди, время, токены и $; журнал недоступен — сводка без затрат с пометкой | `agent_run`, журнал LiteLLM | FR-152 |
| `GET /projects/:projectKey/analytics/agent-run-stats` | статистика запусков за период | `agent_run`, `run_event` | FR-152 |

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-get">GET</span> | ICPlan → Сводка и статистика | <span class="st st-ok">✅ есть</span> | аналитика агентов, сводка, чат запуска | Пользователь, администратор · сессия | US-OBS-01, US-OBS-05 | FR-152 | I20 |
