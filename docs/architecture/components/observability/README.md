# Observability

> Файл собирается командой `arch.py assemble` из единиц компонента.

Прозрачность: что агент делал по шагам и сколько это стоило.

## Что делает

- Пишет события каждого запуска
- Строит чат запуска в задаче ICPlan
- Считает затраты по запуску, задаче, агенту, модели
- Хранит аудит guardrails
- Удаляет старые события по сроку

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Данные](data)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [findings](docs/findings.md)
- [how](docs/how.md)
- [observability-architecture](docs/observability-architecture.md)
- [observability-interfaces](docs/observability-interfaces.md)
- [techspec](docs/techspec.md)
