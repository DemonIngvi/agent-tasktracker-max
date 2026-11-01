# Harness

> Файл собирается командой `arch.py assemble` из единиц компонента.

Агентский цикл: делает из модели агента и заставляет его работать по правилам платформы.

## Что делает

- Собирает агента из определения: промпт, навыки, тулы, лимиты
- Крутит цикл контекст → модель → тулы
- Проверяет действия через hooks (G2)
- Останавливается на approve и продолжает с того же шага
- Соблюдает лимиты, сжимает историю, стримит шаги

## Входы

- [I7](../agent-runner/integrations/I7.yaml): Agent Runner, Runner вызывает Harness: задание, подтверждения, указания и отмена → Harness; события и итог ← Harness

## Выходы

- [I10](integrations/I10.yaml): Guardrails, проверка действия G2 (для MCP — повторно в Runner)
- [I11](integrations/I11.yaml): Memory, запись и чтение M3, контекст памяти
- [I12](integrations/I12.yaml): Agent Runner, checkpoint цикла
- [I8](integrations/I8.yaml): LiteLLM gateway, вызов модели
- [I9](integrations/I9.yaml): MCP / Tools, вызов тулов MCP через MCP-прокси Runner (AD-19)

## Из чего состоит

- [Требования](prd.md)
- [Истории](stories)
- [Процессы](processes)
- [Блоки](blocks)
- [Функции](functions)
- [Интеграции](integrations)
- [Потоки](flows)
- [Сценарии](sequences)
- [Эндпоинты](endpoints.yaml)
- [Подтверждения](approvals.yaml)
- [agent-harness-architecture](docs/agent-harness-architecture.md)
- [agent-harness-interfaces](docs/agent-harness-interfaces.md)
- [how](docs/how.md)
- [techspec](docs/techspec.md)
