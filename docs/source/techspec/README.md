# Техническая спецификация

← Справка · правило и роль

Как собираются, откуда берутся и как запускаются образы и сервисы каждого компонента. Заполняет **инженер сборки и поставки** по правилу; значения параметров — в `interfaces.md` спек, здесь — техника поставки.

| Компонент | Что разворачивается |
|---|---|
| ICPlan (форк) | web, api, worker, bot форка ICPlan с доработками платформы (модуль Platform, автоподхват, протокол раннера) |
| Platform module | модуль внутри api форка ICPlan: настройки агентов, бюджеты, профили, политики |
| Agent Runner | Go-сервис: забирает запуски из ICPlan, планирует слоты, поднимает sandbox, связывает с Harness |
| Sandbox | одноразовый контейнер запуска на образе Harness; тёплый пул; сеть только через egress-прокси |
| Harness | Python-процесс агентского цикла (LangGraph) внутри sandbox |
| Memory | Memory API: чтение M1–M3, запись M3 с проверками, очистка по срокам |
| MCP / Tools | MCP-серверы: `itsaplan-core` в api ICPlan; внешние — отдельные образы; клиент MCP — в Harness |
| Guardrails | OPA рядом с Runner и Harness; правила Rego из git; данные из Platform module |
| LiteLLM gateway | LiteLLM Proxy: алиасы, бюджеты, учёт; mock-LLM для разработки |
| Observability | в MVP — без своего сервиса: события в БД ICPlan, затраты из LiteLLM, сводка в ICPlan |
| Инфраструктура | k3s на одном узле, Helm-чарты, Traefik, CloudNativePG + PgBouncer, RustFS, бэкапы вне площадки |
