# Deploy: Agent Runner

← компонент · методология

**Что разворачивается:** Go-сервис: забирает запуски из ICPlan, планирует слоты, поднимает sandbox, связывает с Harness.

## Образы

| Образ | База | Что внутри | Как собирается | Откуда берём | Тег | Пользователь | Порты | Проверка готовности |
|---|---|---|---|---|---|---|---|---|
| agent-runner | `golang:1.2x` (сборка) → `gcr.io/distroless/static:nonroot` | статический бинарник Runner | `runner/Dockerfile` репозитория платформы | `ghcr.io/demoningvi/agent-runner` | semver платформы | nonroot (65532) | 8080 (метрики, health) | `GET /healthz`, `GET /readyz` (ICPlan и Platform module доступны) |

## Запуск

| | |
|---|---|
| **Namespace** | `itsaplan-agents` |
| **Реплики** | 1 (MVP), 2 — с общими слотами |
| **Доступ к контейнерам** | этапы 1–3: rootless Docker на узле (сокет пользователя Runner); этап 4: ServiceAccount на `itsaplan-agents` (I23) |
| **Ресурсы** | requests 0.1 CPU / 128 МиБ, limits 0.5 / 512 МиБ |

## Переменные и секреты

| Переменная | Зачем | Откуда |
|---|---|---|
| `ITSAPLAN_URL`, `ITSAPLAN_AGENT_KEYS` | очередь и ключи агентов | Secret `runner-agents` |
| `PLATFORM_API_URL`, `PLATFORM_TOKEN` | настройки агентов | Secret |
| `DATABASE_URL` | база `itsaplan`, роль `runner` — владелец схем `runner` (слоты, кэш подготовки) и `harness_ckpt` (checkpoint), через PgBouncer (AD-22) | Secret `runner-db` |
| `DOCKER_HOST` | rootless Docker | values |
| `HARNESS_IMAGE` | образ sandbox | values |
| секреты MCP-серверов (`auth.secret_ref`) | MCP-прокси подставляет учётные данные (AD-19) | Secret в `itsaplan-agents`, чтение — ServiceAccount Runner |
| `SETUP_NETWORK` | сеть шага подготовки `sbx-setup` | values |

## Сборка и поставка

1. Сборка в GitHub Actions по тегу `vX.Y.Z` репозитория компонента; базовые образы закреплены по digest
2. `CGO_ENABLED=0 go build -trimpath -ldflags='-s -w'`
3. Копирование бинарника в distroless
4. Многостадийный Dockerfile: стадия сборки → минимальный образ запуска без компиляторов и менеджеров пакетов
5. SBOM (`syft`) и проверка уязвимостей (`trivy`, блокирует выпуск при critical)
6. Публикация в `ghcr.io/demoningvi/<имя>:<версия>` и `:<версия>-<sha>`; тег `latest` не используется
7. Кластер тянет образы с pull-секретом `ghcr-pull` (Secret в namespace)

## Обновление и откат

1. Перед `helm upgrade` — точка восстановления: отметка времени для PITR CloudNativePG (как в Deploy ICPlan); данные Runner — схемы `runner` (`scheduler_slot`, `setup_cache`) и `harness_ckpt` (`run_checkpoint`) базы `itsaplan` (AD-22).
2. Вывод старой реплики (US-RUN-06): режим «не брать новые» — Poller перестаёт брать запуски, активные доделываются; по таймауту вывода оставшиеся запуски возвращаются в очередь ICPlan по истечении аренды, слоты освобождаются по `lease_until` (FR-71, FR-80 «Runner упал»).
3. `helm upgrade`: `agent-runner` заменяется по одной реплике, работа, начатая на старой версии, доделывается (FR-81 «Обновление»). Миграции схем `runner` и `harness_ckpt` применяет новый Runner при старте, своя таблица версий, только вперёд (`datamodel.MIGRATE`); прямым подключением к Postgres, минуя PgBouncer (AD-18 «PgBouncer transaction»).
4. Откат образа без миграции — `helm rollback`; запуски, взятые новой версией, возвращаются в очередь по истечении аренды и выдаются снова.
5. Откат после миграции — `helm rollback` + схемы `runner` и `harness_ckpt` восстанавливаются на отметку шага 1: PITR в отдельный кластер, оттуда `pg_dump -n runner -n harness_ckpt` → `pg_restore --clean` в рабочую базу; схемы `public`, `platform`, `memory` не трогаем. Данные оперативные: слоты пересчитываются по активным запускам (FMEA «Postgres платформы»), кэш подготовки после отметки теряется — шаг подготовки выполняется заново, checkpoint после отметки теряется — повторно выданный запуск продолжает с последней сохранённой до отметки итерации.
6. Секреты (`runner-agents`, `runner-db`, секреты MCP-серверов) при откате не меняются; ключей шифрования данных у Runner нет.

## Проверка после развёртывания

- [ ] Runner «в сети» в ICPlan
- [ ] Тестовый запуск на mock-LLM доходит до итога

## Пример конфигурации

Как настройки лежат в развёртывании. Значения и границы параметров — в `interfaces.md` спеки (здесь новых не вводится); поля контрактов — в Модели данных.

Параметры уровня L0 (S9, `values.yaml` в git, без секретов; ключи агентов — в Secret `runner-agents`):

```yaml
agentRunner:
  poll_interval_ms: 3000        # 1000–30000
  retry: 0                      # 0–3, без повтора по умолчанию
  scheduling:
    mode: parallel              # sequential | parallel
    global_max: 4
    per_issue: 1
    order: fifo                 # fifo | priority
    aging_s: 600                # 60–3600, действует при order: priority
    models:
      team-default: { max: 3 }
  guardrails: { g1: { enabled: true } }
  on_engine_error: deny
  setup: { cache_ttl_h: 168 }
  provider: docker              # docker | k8s
  events: { level: "всё" }       # итоги | всё
  # agents — ключи из Secret runner-agents (ITSAPLAN_AGENT_KEYS), не в values
```
