# Tasks

← [proposal](proposal.md) · спека · [ROADMAP](..\..\ROADMAP.md)

Задачи ROADMAP, закрывающие требования `R-ICP-*`; файл собирается из ROADMAP (`html-view/tasksmd.py`). Общий список — [define-agent-platform](..\define-agent-platform\tasks.md).

## 2. Агент работает из ICPlan

- [ ] 2.1 Agent Runner как внешний раннер ICPlan: Первая связь с ICPlan: задачи из очереди ICPlan выполняет наш Harness, а не CLI на машине оператора. Требования: FR-1, FR-2, FR-3, FR-4, FR-7, FR-9 и др.. Подробно: [docs/tasks/2.1-runner-external.md](..\..\tasks\2.1-runner-external.md)
- [ ] 2.3 Конфиг агента из ICPlan + YAML: Пользователь настраивает агента в UI ICPlan; Harness должен брать модель, инструкцию и тулы оттуда, а недостающее (лимиты, approve) — из YAML до появления Platform module. Требования: FR-8, FR-54, FR-55, FR-58, FR-59, FR-60 и др.. Подробно: [docs/tasks/2.3-config-from-icplan.md](..\..\tasks\2.3-config-from-icplan.md)
- [ ] 2.6 E2E: от задачи до итога: Фиксирует, что этап 2 работает целиком и не ломается при следующих доработках. Требования: FR-17, FR-73, FR-80. Подробно: [docs/tasks/2.6-e2e-icplan.md](..\..\tasks\2.6-e2e-icplan.md)
- [ ] 2.7 Планировщик запусков (слоты, режимы): Агентов несколько, они делят модели и могут работать параллельно или только по одному. Требования: FR-3, FR-67, FR-68, FR-69, FR-70, FR-71 и др.. Подробно: [docs/tasks/2.7-runner-scheduler.md](..\..\tasks\2.7-runner-scheduler.md)

## 3. ICPlan ведёт процесс

- [ ] 3.3 События запуска и чат запуска в задаче: Пользователь хочет видеть в задаче, что делает агент и почему: реплики, рассуждения, действия, вопросы и итог — чат запуска (AD-21, R&D, поток). Требования: FR-4, FR-125, FR-146, FR-147, FR-148, FR-149 и др.. Подробно: [docs/tasks/3.3-run-events-timeline.md](..\..\tasks\3.3-run-events-timeline.md)
- [ ] 3.4 ICPlan: approve в задаче: Пауза на approve из 1.5 должна управляться из задачи ICPlan, иначе опасные действия блокируют работу. Требования: FR-5, FR-6, FR-117. Подробно: [docs/tasks/3.4-icplan-approve-ui.md](..\..\tasks\3.4-icplan-approve-ui.md)
- [ ] 3.8 Чат с агентом, указания во время работы, выключение агента: Пользователь поправляет агента без перезапуска, администратор проверяет агента в чате до подключения к процессу и временно выключает агента. Требования: FR-10, FR-11, FR-12, FR-28. Подробно: [docs/tasks/3.8-agent-chat-control.md](..\..\tasks\3.8-agent-chat-control.md)

## 4. После MVP

- [ ] 4.6 Kubernetes: k3s, Helm, namespaces, Traefik, сетевые политики: Платформа должна разворачиваться воспроизводимо на сервере: кластер, чарты, вход по HTTPS, изоляция namespaces, секреты вне git. Требования: FR-18, FR-35, FR-52, FR-63, FR-81, FR-94 и др.. Подробно: [docs/tasks/4.6-k8s-helm-ingress.md](..\..\tasks\4.6-k8s-helm-ingress.md)
- [ ] 4.7 Postgres (CloudNativePG), PgBouncer, RustFS, бэкап вне узла: Одна СУБД обслуживает ICPlan, платформу и LiteLLM — нужны пул соединений, бэкапы вне узла и проверка восстановления (риск X5 ревью). Требования: FR-163, FR-164, FR-165, FR-171, FR-173, FR-13. Подробно: [docs/tasks/4.7-postgres-storage-backup.md](..\..\tasks\4.7-postgres-storage-backup.md)
- [ ] 4.8 Нагрузочный тест и подтверждение профиля: Профиль нагрузки — гипотеза; без замера нельзя выпускать в продуктив и настраивать лимиты. Требования: NFR-1, NFR-2, NFR-3, NFR-4, NFR-5, NFR-6 и др.. Подробно: [docs/tasks/4.8-load-test.md](..\..\tasks\4.8-load-test.md)

## Архивация

Change архивируется (`openspec archive`) после реализации и приёмки его задач — тогда спеки становятся действующими в `openspec/specs/` (правило).
