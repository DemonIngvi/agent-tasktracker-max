# Proposal

## Why

[ICPlan](../../../architecture/components/icplan/README.md) назначает агентов на задачи и должен работать с платформой через стабильный контракт уровня C1, не завися от её внутренней структуры (C2).

## What Changes

- [Agent Runner](../../../architecture/components/agent-runner/README.md) работает как внешний раннер [ICPlan](../../../architecture/components/icplan/README.md) (pull, [AD-8](../../../architecture/decisions/AD-8.yaml)): забирает запуски из очереди агента (`claim`), продлевает аренду (`heartbeat`), передаёт события (AG-UI, [AD-21](../../../architecture/decisions/AD-21.yaml)) и итог (`result`).
- Обратный канал без входящих соединений: отмена, решения пользователя и указания — в ответе heartbeat (доработка форка, [AD-17](../../../architecture/decisions/AD-17.yaml)).
- В задаче — чат запуска: ход работы агента, вопросы и подтверждения, карточка итога ([AD-21](../../../architecture/decisions/AD-21.yaml)); переходы по шагам процесса делает [ICPlan](../../../architecture/components/icplan/README.md) ([AD-17](../../../architecture/decisions/AD-17.yaml)).
- Агент действует в [ICPlan](../../../architecture/components/icplan/README.md) через MCP-сервер `itsaplan-core` (через MCP-прокси Runner, [AD-19](../../../architecture/decisions/AD-19.yaml)).

## Capabilities

### New Capabilities
- `icplan-integration`: контракт взаимодействия [ICPlan](../../../architecture/components/icplan/README.md) с Agent Platform (C1)

### Modified Capabilities
<!-- нет -->

## Impact

- Доработки форка [ICPlan](../../../architecture/components/icplan/README.md): протокол раннера (тело heartbeat, события), чат запуска, процесс задачи, вердикт; опирается на [Agent Runner](../../../architecture/components/agent-runner/README.md), [Harness](../../../architecture/components/harness/README.md), [Observability](../../../architecture/components/observability/README.md) из change `define-agent-platform`.
