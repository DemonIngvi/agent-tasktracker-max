# Tasks

← [proposal](proposal.md) · [ROADMAP](..\..\ROADMAP.md) · [сводная таблица](..\..\TASKS.md)

Задачи по этапам ROADMAP; файл собирается из ROADMAP (`html-view/tasksmd.py`). Подробности, INVEST, оценки и приёмка — в документе задачи. Задачи процесса ICPlan детализированы также в [icplan-agent-autopickup](..\icplan-agent-autopickup\tasks.md).

## 1. Агент работает сам

- [ ] 1.1 Mock-LLM и LiteLLM: Harness нужно разрабатывать и тестировать без платного провайдера и без случайности ответов. Требования: FR-134, FR-135, FR-137, FR-140, FR-141, FR-142 и др.. Подробно: [docs/tasks/1.1-mock-llm-litellm.md](..\..\tasks\1.1-mock-llm-litellm.md)
- [ ] 1.2 Формат определения агента (YAML): Формат YAML — контракт между ICPlan, Harness и экспортом/импортом. Требования: FR-31, FR-53, FR-54, FR-57. Подробно: [docs/tasks/1.2-agent-definition-yaml.md](..\..\tasks\1.2-agent-definition-yaml.md)
- [ ] 1.3 Harness: ядро на LangGraph: Ядро MVP: агентский цикл, собранный из конфига. Требования: FR-19, FR-20, FR-21, FR-24, FR-30, FR-31 и др.. Подробно: [docs/tasks/1.3-harness-core.md](..\..\tasks\1.3-harness-core.md)
- [ ] 1.4 Harness: MCP и тулы: Без тулов агент только отвечает текстом. Требования: FR-29, FR-33, FR-34, FR-176, FR-177, FR-178 и др.. Подробно: [docs/tasks/1.4-harness-mcp-tools.md](..\..\tasks\1.4-harness-mcp-tools.md)
- [ ] 1.5 Harness: hooks и пауза на approve: Approve опасных действий — обязательное требование; механизм паузы и возобновления нужен и для вопросов пользователю. Требования: FR-22, FR-23, FR-32, FR-112. Подробно: [docs/tasks/1.5-harness-hooks-approve.md](..\..\tasks\1.5-harness-hooks-approve.md)
- [ ] 1.6 Harness: лимиты, завершение, контекст: Без лимитов агент может зациклиться и тратить токены; без управления контекстом длинные задачи падают на переполнении окна. Требования: FR-25, FR-26, FR-27, FR-34, FR-118, FR-119 и др.. Подробно: [docs/tasks/1.6-harness-limits-context.md](..\..\tasks\1.6-harness-limits-context.md)
- [x] 1.7 ~~закрыта~~ — закрыта. Подробно: [docs/tasks/1.7-dev-ui.md](..\..\tasks\1.7-dev-ui.md)

## 2. Агент работает из ICPlan

- [ ] 2.1 Agent Runner как внешний раннер ICPlan: Первая связь с ICPlan: задачи из очереди ICPlan выполняет наш Harness, а не CLI на машине оператора. Требования: FR-1, FR-2, FR-3, FR-4, FR-7, FR-9 и др.. Подробно: [docs/tasks/2.1-runner-external.md](..\..\tasks\2.1-runner-external.md)
- [ ] 2.2 Harness в Docker-контейнере на запуск: Изоляция запусков с первого дня интеграции; тёплый пул — оптимизация позже (4.1). Требования: FR-75, FR-82, FR-84, FR-86, FR-89, FR-90 и др.. Подробно: [docs/tasks/2.2-sandbox-docker-oneshot.md](..\..\tasks\2.2-sandbox-docker-oneshot.md)
- [ ] 2.3 Конфиг агента из ICPlan + YAML: Пользователь настраивает агента в UI ICPlan; Harness должен брать модель, инструкцию и тулы оттуда, а недостающее (лимиты, approve) — из YAML до появления Platform module. Требования: FR-8, FR-54, FR-55, FR-58, FR-59, FR-60 и др.. Подробно: [docs/tasks/2.3-config-from-icplan.md](..\..\tasks\2.3-config-from-icplan.md)
- [ ] 2.4 MCP `itsaplan-core` для агента: Агент должен читать задачу, писать комментарии и менять статус — иначе процесс между этапами не работает. Требования: FR-179, FR-182, FR-185. Подробно: [docs/tasks/2.4-mcp-itsaplan-core.md](..\..\tasks\2.4-mcp-itsaplan-core.md)
- [ ] 2.5 Память M1–M3: контекст, управление: Агент следующего этапа должен продолжать работу, а не начинать с нуля. Требования: FR-36, FR-37, FR-39, FR-40, FR-42, FR-43 и др.. Подробно: [docs/tasks/2.5-memory-m2-m3.md](..\..\tasks\2.5-memory-m2-m3.md)
- [ ] 2.6 E2E: от задачи до итога: Фиксирует, что этап 2 работает целиком и не ломается при следующих доработках. Требования: FR-17, FR-73, FR-80. Подробно: [docs/tasks/2.6-e2e-icplan.md](..\..\tasks\2.6-e2e-icplan.md)
- [ ] 2.7 Планировщик запусков (слоты, режимы): Агентов несколько, они делят модели и могут работать параллельно или только по одному. Требования: FR-3, FR-67, FR-68, FR-69, FR-70, FR-71 и др.. Подробно: [docs/tasks/2.7-runner-scheduler.md](..\..\tasks\2.7-runner-scheduler.md)
- [ ] 2.8 Общий резолвер конфигурации L0–L3: Пять модулей получают параметры запуска через `RunBundle` от Runner. Требования: FR-31, FR-48, FR-77, FR-90, FR-183. Подробно: [docs/tasks/2.8-config-storage-interfaces-fmea.md](..\..\tasks\2.8-config-storage-interfaces-fmea.md)

## 3. ICPlan ведёт процесс

- [ ] 3.1 ICPlan: процесс типа задачи и агент шага: Тип задачи задаёт процесс, шаг процесса — колонку и агента. Требования: FR-188, FR-189, FR-191, FR-192, FR-195, FR-196 и др.. Подробно: [docs/tasks/3.1-icplan-process-step-agent.md](..\..\tasks\3.1-icplan-process-step-agent.md)
- [ ] 3.2 ICPlan: передача между агентами: Следующий агент должен получать итог предыдущего, а пользователь — понимать, почему агент начал работу. Требования: FR-193, FR-194, FR-26. Подробно: [docs/tasks/3.2-icplan-handoff.md](..\..\tasks\3.2-icplan-handoff.md)
- [ ] 3.3 События запуска и чат запуска в задаче: Пользователь хочет видеть в задаче, что делает агент и почему: реплики, рассуждения, действия, вопросы и итог — чат запуска (AD-21, R&D, поток). Требования: FR-4, FR-125, FR-146, FR-147, FR-148, FR-149 и др.. Подробно: [docs/tasks/3.3-run-events-timeline.md](..\..\tasks\3.3-run-events-timeline.md)
- [ ] 3.4 ICPlan: approve в задаче: Пауза на approve из 1.5 должна управляться из задачи ICPlan, иначе опасные действия блокируют работу. Требования: FR-5, FR-6, FR-117. Подробно: [docs/tasks/3.4-icplan-approve-ui.md](..\..\tasks\3.4-icplan-approve-ui.md)
- [ ] 3.5 ICPlan: эффект Действия, затраты: Расширение автоматизации (произвольные условия Действий) и видимость стоимости задачи. Требования: FR-135, FR-150, FR-190. Подробно: [docs/tasks/3.5-icplan-type-actions-cost.md](..\..\tasks\3.5-icplan-type-actions-cost.md)
- [ ] 3.6 ICPlan: переходы по итогу запуска и очередь агента: Задача сама проходит процесс: переход делает ICPlan по итогу запуска, а не агент по своему усмотрению. Требования: FR-197, FR-198, FR-205, FR-206. Подробно: [docs/tasks/3.6-icplan-process-engine.md](..\..\tasks\3.6-icplan-process-engine.md)
- [ ] 3.7 ICPlan: управление ходом задачи: Пользователь управляет ходом задачи: проверяет результат перед переходом, возвращает с заметкой, останавливает и возобновляет процесс, повторяет шаг. Требования: FR-199, FR-200, FR-201, FR-202, FR-203, FR-207. Подробно: [docs/tasks/3.7-icplan-task-control.md](..\..\tasks\3.7-icplan-task-control.md)
- [ ] 3.8 Чат с агентом, указания во время работы, выключение агента: Пользователь поправляет агента без перезапуска, администратор проверяет агента в чате до подключения к процессу и временно выключает агента. Требования: FR-10, FR-11, FR-12, FR-28. Подробно: [docs/tasks/3.8-agent-chat-control.md](..\..\tasks\3.8-agent-chat-control.md)
- [ ] 3.9 Сводка задач с агентами и статистика агентов: Пользователь видит, что выполняется, сколько это идёт и стоит; администратор и владелец продукта — какой агент полезен. Требования: FR-152, FR-153. Подробно: [docs/tasks/3.9-agent-summary-stats.md](..\..\tasks\3.9-agent-summary-stats.md)

## 4. После MVP

- [ ] 4.1 Тёплый пул sandbox: Убрать задержку старта контейнера, не жертвуя изоляцией. Требования: FR-83, FR-93. Подробно: [docs/tasks/4.1-sandbox-warm-pool.md](..\..\tasks\4.1-sandbox-warm-pool.md)
- [ ] 4.2 Egress-прокси и доступ к репозиториям: Агенту-разработчику нужен код, но без утечки секретов и без доступа куда не положено. Требования: FR-84, FR-85, FR-87, FR-88, FR-89, FR-92 и др.. Подробно: [docs/tasks/4.2-egress-repo-access.md](..\..\tasks\4.2-egress-repo-access.md)
- [ ] 4.3 Guardrails: OPA для G1/G2 и включение точек: Правила безопасности в одном месте, проверяемые и отключаемые конфигом. Требования: FR-110, FR-111, FR-112, FR-115, FR-116, FR-117 и др.. Подробно: [docs/tasks/4.3-guardrails-opa.md](..\..\tasks\4.3-guardrails-opa.md)
- [ ] 4.4 Platform module в ICPlan: Перенести настройки из YAML в ICPlan: бюджеты, профили, данные guardrails, версии — с UI. Требования: FR-56, FR-60, FR-95, FR-96, FR-97, FR-98 и др.. Подробно: [docs/tasks/4.4-platform-module.md](..\..\tasks\4.4-platform-module.md)
- [ ] 4.5 LiteLLM: бюджеты, fallback, G4: Контроль трат и устойчивость к сбоям провайдера; базовая защита содержимого. Требования: FR-114, FR-120, FR-123, FR-136, FR-138, FR-139 и др.. Подробно: [docs/tasks/4.5-litellm-budgets-fallback-g4.md](..\..\tasks\4.5-litellm-budgets-fallback-g4.md)
- [ ] 4.6 Kubernetes: k3s, Helm, namespaces, Traefik, сетевые политики: Платформа должна разворачиваться воспроизводимо на сервере: кластер, чарты, вход по HTTPS, изоляция namespaces, секреты вне git. Требования: FR-18, FR-35, FR-52, FR-63, FR-81, FR-94 и др.. Подробно: [docs/tasks/4.6-k8s-helm-ingress.md](..\..\tasks\4.6-k8s-helm-ingress.md)
- [ ] 4.7 Postgres (CloudNativePG), PgBouncer, RustFS, бэкап вне узла: Одна СУБД обслуживает ICPlan, платформу и LiteLLM — нужны пул соединений, бэкапы вне узла и проверка восстановления (риск X5 ревью). Требования: FR-163, FR-164, FR-165, FR-171, FR-173, FR-13. Подробно: [docs/tasks/4.7-postgres-storage-backup.md](..\..\tasks\4.7-postgres-storage-backup.md)
- [ ] 4.8 Нагрузочный тест и подтверждение профиля: Профиль нагрузки — гипотеза; без замера нельзя выпускать в продуктив и настраивать лимиты. Требования: NFR-1, NFR-2, NFR-3, NFR-4, NFR-5, NFR-6 и др.. Подробно: [docs/tasks/4.8-load-test.md](..\..\tasks\4.8-load-test.md)

## Архивация

Change архивируется (`openspec archive`) после реализации и приёмки его задач — тогда спеки становятся действующими в `openspec/specs/` (правило).
