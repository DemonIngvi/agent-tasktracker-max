# Memory

> Файл собирается командой `arch.py assemble` из единиц компонента.

Память агента: чтобы следующий этап продолжал работу, а не начинал заново, и агент учился на прошлых запусках.

## Что делает

- Уровни M0–M6 по видам знания
- Сама пишет переписку (M1) и итоги запусков (M2)
- Принимает от агента состояние задачи (M3)
- Подаёт нужную память в контекст запуска
- Следит за правами и сроками хранения

## Входы

- [I11](../harness/integrations/I11.yaml): Harness, запись и чтение M3, контекст памяти

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Данные](data)
- [Хранилища](stores)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [agent-memory-architecture](docs/agent-memory-architecture.md)
- [agent-memory-interfaces](docs/agent-memory-interfaces.md)
- [findings](docs/findings.md)
- [how](docs/how.md)
- [techspec](docs/techspec.md)
