# ICPlan

> Файл собирается командой `arch.py assemble` из единиц компонента.

Рабочее место людей: задачи, доска и процесс. Отсюда агенты получают работу и сюда возвращают результат.

## Что делает

- Доска и статусы — процесс, который пользователь настраивает сам
- Настройка агентов (Control Plane UI) и их каталог (Registry)
- Процесс задачи: шаг = колонка + агент + переход по итогу запуска (AD-17) — доработка
- Очередь запусков и протокол внешнего раннера
- Показ хода работы агента, approve и затрат в задаче

## Входы

- [I21](../../integrations/I21.yaml): icplan-users, вход по HTTPS через Traefik: web, api, mcp
- [I1](../agent-runner/integrations/I1.yaml): Agent Runner, Runner забирает запуск из очереди (`POST /agent-runs/claim`, pull, аренда 300 с); в ответе — `Run`
- [I2](../agent-runner/integrations/I2.yaml): Agent Runner, шаги запуска и итог
- [I24](../agent-runner/integrations/I24.yaml): Agent Runner, MCP-прокси Runner вызывает MCP-сервер itsaplan-core в api ICPlan (`POST /mcp`) с ключом агента из Secret (AD-19); дальше I9 — к Harness
- [I3](../agent-runner/integrations/I3.yaml): Agent Runner, Runner продлевает аренду (`POST /agent-runs/:runId/heartbeat`); сейчас ответ 204 без тела, отмена — ответом 404; после доработки (FR-10) в ответе — отмена, решения по approve и указания пользователя
- [I20](integrations/I20.yaml): ICPlan, интерфейс ICPlan ↔ API (в том числе экраны Platform module, чат запуска, сводка)

## Выходы

- [I20](integrations/I20.yaml): ICPlan, интерфейс ICPlan ↔ API (в том числе экраны Platform module, чат запуска, сводка)

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
- [findings](docs/findings.md)
- [how](docs/how.md)
- [icplan-agent-autopickup-architecture](docs/icplan-agent-autopickup-architecture.md)
- [icplan-agent-autopickup-interfaces](docs/icplan-agent-autopickup-interfaces.md)
- [icplan-integration-architecture](docs/icplan-integration-architecture.md)
- [icplan-integration-interfaces](docs/icplan-integration-interfaces.md)
- [techspec](docs/techspec.md)
