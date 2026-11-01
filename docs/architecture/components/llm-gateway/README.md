# LiteLLM gateway

> Файл собирается командой `arch.py assemble` из единиц компонента.

Единственная дверь к моделям: смена модели, лимиты и учёт затрат в одном месте.

## Что делает

- Алиасы моделей: смена модели без изменения агентов
- Virtual key на агента, бюджеты и rate limit
- Резервная модель при сбое
- Проверки G4 во входе и ответе
- Журнал токенов и стоимости

## Входы

- [I8](../harness/integrations/I8.yaml): Harness, вызов модели
- [I15](../platform-module/integrations/I15.yaml): Platform module, выдача virtual key, бюджеты

## Выходы

- [I13](integrations/I13.yaml): llm-providers, запросы к моделям
- [I14](integrations/I14.yaml): Инфраструктура, ключи, бюджеты, журнал затрат в БД `litellm`

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
- [findings](docs/findings.md)
- [how](docs/how.md)
- [llm-gateway-architecture](docs/llm-gateway-architecture.md)
- [llm-gateway-interfaces](docs/llm-gateway-interfaces.md)
- [techspec](docs/techspec.md)
