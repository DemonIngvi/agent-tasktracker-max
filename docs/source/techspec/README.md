# Техническая спецификация

← Справка · правило и роль

Как собираются, откуда берутся и как запускаются образы и сервисы каждого компонента. Заполняет **инженер сборки и поставки** по правилу; значения параметров — в `interfaces.md` спек, здесь — техника поставки.

| Компонент | Что разворачивается |
|---|---|
| [ICPlan (форк)](..\..\architecture\components\icplan\docs\techspec.md) | web, api, worker, bot форка ICPlan с доработками платформы (модуль Platform, автоподхват, протокол раннера) |
| [Platform module](..\..\architecture\components\platform-module\docs\techspec.md) | модуль внутри api форка ICPlan: настройки агентов, бюджеты, профили, политики |
| [Agent Runner](..\..\architecture\components\agent-runner\docs\techspec.md) | Go-сервис: забирает запуски из ICPlan, планирует слоты, поднимает sandbox, связывает с Harness |
| [Sandbox](..\..\architecture\components\sandbox\docs\techspec.md) | одноразовый контейнер запуска на образе Harness; тёплый пул; сеть только через egress-прокси |
| [Harness](..\..\architecture\components\harness\docs\techspec.md) | Python-процесс агентского цикла (LangGraph) внутри sandbox |
| [Memory](..\..\architecture\components\memory\docs\techspec.md) | Memory API: чтение M1–M3, запись M3 с проверками, очистка по срокам |
| [MCP / Tools](..\..\architecture\components\mcp-tools\docs\techspec.md) | MCP-серверы: `itsaplan-core` в api ICPlan; внешние — отдельные образы; клиент MCP — в Harness |
| [Guardrails](..\..\architecture\components\guardrails\docs\techspec.md) | OPA рядом с Runner и Harness; правила Rego из git; данные из Platform module |
| [LiteLLM gateway](..\..\architecture\components\llm-gateway\docs\techspec.md) | LiteLLM Proxy: алиасы, бюджеты, учёт; mock-LLM для разработки |
| [Observability](..\..\architecture\components\observability\docs\techspec.md) | в MVP — без своего сервиса: события в БД ICPlan, затраты из LiteLLM, сводка в ICPlan |
| [Инфраструктура](..\..\architecture\components\infrastructure\docs\techspec.md) | k3s на одном узле, Helm-чарты, Traefik, CloudNativePG + PgBouncer, RustFS, бэкапы вне площадки |
