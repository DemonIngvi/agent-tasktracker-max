# Agent Runner

> Файл собирается командой `arch.py assemble` из единиц компонента.

Исполнитель: превращает запуск из очереди ICPlan в работу агента в изолированной среде и возвращает итог.

## Что делает

- Забирает запуск из очереди ICPlan
- Планирует старт по слотам: агент, модель, задача, глобально; режим sequential / parallel
- Проверяет допуск, бюджет и лимиты (G1)
- Выдаёт sandbox из тёплого пула и токены репозиториев
- Запускает Harness, транслирует шаги в ICPlan, следит за таймаутом и отменой
- Проксирует вызовы MCP: allowlist и G2 вне sandbox, ключи серверов (AD-19)
- Выполняет шаг подготовки среды: зависимости проекта (AD-19)
- Пишет итог в задачу и уничтожает sandbox

## Входы

- [I12](../harness/integrations/I12.yaml): Harness, checkpoint цикла

## Выходы

- [I1](integrations/I1.yaml): ICPlan, Runner забирает запуск из очереди (`POST /agent-runs/claim`, pull, аренда 300 с); в ответе — `Run`
- [I18](integrations/I18.yaml): git-provider, короткоживущие токены репозиториев
- [I19](integrations/I19.yaml): Инфраструктура, файлы задачи и артефакты в RustFS (S3 API)
- [I2](integrations/I2.yaml): ICPlan, шаги запуска и итог
- [I23](integrations/I23.yaml): Sandbox, среды запусков через Kubernetes API (этап 4)
- [I24](integrations/I24.yaml): ICPlan, MCP-прокси Runner вызывает MCP-сервер itsaplan-core в api ICPlan (`POST /mcp`) с ключом агента из Secret (AD-19); дальше I9 — к Harness
- [I3](integrations/I3.yaml): ICPlan, Runner продлевает аренду (`POST /agent-runs/:runId/heartbeat`); сейчас ответ 204 без тела, отмена — ответом 404; после доработки (FR-10) в ответе — отмена, решения по approve и указания пользователя
- [I4](integrations/I4.yaml): Platform module, настройки, определение версии запуска (`GET /platform/runs/:runId/agent`, AD-23), манифест
- [I5](integrations/I5.yaml): Guardrails, допуск запуска G1
- [I6](integrations/I6.yaml): Sandbox, Runner создаёт и уничтожает среду (Docker API) по `SandboxClaim`; `RepoGrant` задаёт правила git-прокси этой среды (какие репозитории и ветки), сам токен в среду не попадает
- [I7](integrations/I7.yaml): Harness, Runner вызывает Harness: задание, подтверждения, указания и отмена → Harness; события и итог ← Harness

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Данные](data)
- [Хранилища](stores)
- [Интеграции](integrations)
- [Потоки](flows)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [agent-runner-architecture](docs/agent-runner-architecture.md)
- [agent-runner-interfaces](docs/agent-runner-interfaces.md)
- [findings](docs/findings.md)
- [how](docs/how.md)
- [techspec](docs/techspec.md)
