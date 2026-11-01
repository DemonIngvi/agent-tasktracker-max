# Deploy: ICPlan (форк)

← компонент · методология

**Что разворачивается:** web, api, worker, bot форка ICPlan с доработками платформы (модуль Platform, автоподхват, протокол раннера). Развёртывание — чарт форка `charts/itsaplan`; «как в форке» сверено с кодом `DemonIngvi/itsaplan-app` (13.10.2026: `charts/itsaplan`, `.env.example`, `apps/*`, `packages/db/src/migrate.ts`, `backup.ts`), «нужно» — доработка в [задаче 4.6](..\..\..\..\source\tasks\4.6-k8s-helm-ingress.md).

**Встроенные компоненты** (работают в образе api): [Platform module](..\..\platform-module\docs\techspec.md) — модуль api; [Observability](..\..\observability\docs\techspec.md) — в MVP без своего сервиса, события и сводка в ICPlan; [MCP itsaplan-core](..\..\mcp-tools\docs\techspec.md) — `POST /mcp` (I24).

## Образы

| Образ | База | Что внутри | Как собирается | Откуда берём | Тег | Пользователь | Порты | Проверка готовности |
|---|---|---|---|---|---|---|---|---|
| api | `oven/bun:1.4.0-alpine` (сборка) → `alpine:3.23` | API, миграции БД (`packages/db`), MCP `itsaplan-core`, модули платформы; `bun install --frozen-lockfile` по `bun.lock`; клиент `postgresql18-client` для дампа перед миграцией | `apps/api/Dockerfile` | `ghcr.io/demoningvi/itsaplan-app-api` | см. «Сборка и поставка» | **как в форке:** в Dockerfile нет `USER` — root; **нужно:** non-root через `securityContext` чарта (ниже) | 3000 | `GET /` (корень api — проверка жизни, `apps/api/src/app.ts`; `/health` в форке нет); чарт: `api.healthcheck.path: /` |
| web | `oven/bun:1.4.0-alpine` → `node:24-alpine` | интерфейс (SSR); разделы `@/cloud` (AD-24) — при сборке с `CLOUD_UI_ENTRY` | `apps/web/Dockerfile` | `ghcr.io/demoningvi/itsaplan-app-web` | см. ниже | как api | 3001 | `GET /login` (чарт: `web.healthcheck.path`) |
| worker | `oven/bun:1.4.0-alpine` | фоновые задачи: уведомления, переходы процесса, очистка | `apps/worker/Dockerfile` | `ghcr.io/demoningvi/itsaplan-app-worker` | см. ниже | как api | — | процесс жив, очередь разбирается |
| bot | `oven/bun:1.4.0-alpine` | Telegram-бот | `apps/bot/Dockerfile` | `ghcr.io/demoningvi/itsaplan-app-bot` | см. ниже | как api | — | процесс жив |

Версия форка: `X.Y.Z` форка ведёт release-please форка; версия upstream, на которой основан выпуск, — в описании выпуска форка.

## Запуск

| | |
|---|---|
| **Namespace** | `itsaplan-core` |
| **Реплики** | api 2, web 1–2, worker 1, bot 1 |
| **Миграции** | init-контейнер `migrate` чарта (`bun run packages/db/src/migrate.ts`) до старта api; реплики ждут друг друга на `pg_advisory_lock`; worker и bot ждут init-контейнером `wait-for-migrations`. **Как в форке:** `migrate.ts` читает `DATABASE_URL`, а init-контейнер берёт Secret по имени релиза (`itsaplan.fullname`), а не `itsaplan.secretName` — при `secrets.existingSecret` под не стартует; **нужно (чарт, 4.6.11):** `secretRef` init-контейнера через `itsaplan.secretName`; в init-контейнере `DATABASE_URL` из ключа `MIGRATION_DATABASE_URL` Secret — прямое подключение к Postgres (сервис `-rw` CloudNativePG), минуя PgBouncer: в режиме transaction сессионная блокировка ненадёжна |
| **Дамп перед миграцией** | **Как в форке:** `migrate.ts` снимает `pg_dump` **всей базы** (`backup.ts`) в `/backups`; при сбое дампа миграция не применяется. В базе `itsaplan` есть чужие схемы `runner`, `harness_ckpt`, `memory` (AD-22): роль `itsaplan` их не читает — дамп падает и останавливает выпуск; а если бы читала, восстановление дампа откатило бы данные Runner и Memory. **Решение:** `SKIP_PRE_MIGRATION_BACKUP=1`, точка восстановления — PITR CloudNativePG (см. «Обновление и откат»); `api.backups.persistence` не включаем. Дамп только своих схем (`-n public -n platform`) — возможная доработка форка, в MVP не делаем |
| **Безопасность** | **как в форке:** `podSecurityContext: {}`, `securityContext: {}`; **нужно (values):** `podSecurityContext: {runAsNonRoot: true, runAsUser: 1000, fsGroup: 1000}`, `securityContext: {allowPrivilegeEscalation: false, capabilities: {drop: [ALL]}, readOnlyRootFilesystem: true, seccompProfile: {type: RuntimeDefault}}`. Запись при read-only rootfs: **как в форке** — томов, кроме `/backups` у api, нет; **нужно (чарт, 4.6.11):** `emptyDir` на `/tmp` у api, web, worker, bot и init-контейнеров (временные файлы Bun и Node) |
| **Вход** | Traefik Ingress: web, api, `/mcp` |
| **Данные** | Postgres (CloudNativePG) через PgBouncer, RustFS (S3) — базы и роли. Встроенные `postgresql` и `minio` (RustFS) чарта **выключены** (`postgresql.enabled: false`, `minio.enabled: false`) |
| **Образы и доступ к реестру** | **как в форке:** `*.image.repository` — upstream `ghcr.io/croffasia/itsaplan-*`, `imagePullSecrets: []`; **нужно (values):** образы форка `ghcr.io/demoningvi/itsaplan-app-<service>`, тег `X.Y.Z-<sha>`, `imagePullSecrets: [{name: ghcr-pull}]` ([Инфраструктура](..\..\infrastructure\docs\techspec.md)) |

## Переменные и секреты

Инвентаризация по `.env.example`, `values.yaml` и шаблонам чарта форка; перечислены переменные, которые задаёт платформа, остальные — по умолчанию форка. Секреты — один Secret `itsaplan-secrets` в namespace `itsaplan-core` (`secrets.existingSecret`, ключи — по комментарию `values.yaml` чарта; создаётся скриптом подзадачи 4.6.5, как в [Инфраструктуре](..\..\infrastructure\docs\techspec.md)); чарт тогда свой Secret не создаёт, секретов нет в values и истории релиза.

**Как в форке:** несекретные переменные идут через ConfigMap чарта с фиксированным набором ключей (`API_URL`, `APP_URL`, `COOKIE_DOMAIN`, `S3_*`, `TELEMETRY_DISABLED`, …); произвольные ключи `api.env` и `worker.env` в под не попадают. **Нужно (чарт, 4.6.11):** `api.extraEnv` и `worker.extraEnv` — переменные ниже с пометкой «extraEnv»; до доработки их можно положить ключами в `itsaplan-secrets` (Secret подключается целиком через `envFrom`).

| Переменная | Зачем | Откуда |
|---|---|---|
| `DATABASE_URL` | база `itsaplan`, роль `itsaplan` — схемы `public` и `platform` (Platform module, Observability), через PgBouncer (`prepare: false`); AD-22 | Secret `itsaplan-secrets` |
| `MIGRATION_DATABASE_URL` (нужно) | прямое подключение к Postgres для init-контейнера `migrate`; чарт подставляет его в `DATABASE_URL` init-контейнера | Secret `itsaplan-secrets` |
| `LITELLM_READ_URL` (нужно) | база `litellm`, роль `litellm_read` — чтение журнала затрат (Observability); AD-22 | Secret `itsaplan-secrets` |
| `APP_ENCRYPTION_KEY` | шифрует секреты в БД (ключи агентов `ai_agent.api_key_ciphertext`, учётные данные тулов); без него данные из бэкапа не прочитать — хранится вместе с планом восстановления | Secret `itsaplan-secrets` |
| `BETTER_AUTH_SECRET` | подпись сессий пользователей | Secret `itsaplan-secrets` |
| `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` | ключи RustFS (бакет `planner-attachments`) | Secret `itsaplan-secrets` |
| `API_URL`, `APP_URL` | адреса api и web | values `api.env` |
| `S3_ENDPOINT`, `S3_BUCKET`, `S3_REGION`, `S3_FORCE_PATH_STYLE` | RustFS платформы; `S3_ENDPOINT` — из `externalS3.endpoint` | values `externalS3`, `api.env` |
| `TELEMETRY_DISABLED` | `"1"` — телеметрия upstream выключена (в `values.yaml` форка уже стоит) | values |
| `SSRF_ALLOWED_HOSTS` | внутренние хосты, к которым api можно обращаться (LiteLLM, Memory API) | values, extraEnv |
| `SKIP_PRE_MIGRATION_BACKUP` | `1` — дамп всей базы перед миграцией выключен, точка восстановления — PITR CloudNativePG (см. «Запуск») | values, extraEnv |
| `AGENT_RUN_LEASE_SECONDS` | аренда запуска; значение — [interfaces.md интеграции](icplan-integration-interfaces.md) | values, extraEnv |
| `AGENT_RUN_MAX_ATTEMPTS` | выдач запуска без итога, после которых запуск → `failed` (`expireExhaustedRuns`); значение — [interfaces.md интеграции](icplan-integration-interfaces.md) | values, extraEnv |
| `AGENT_RUN_TIMEOUT_MS` | потолок времени запуска внутреннего агента ICPlan (опрос в api); на агентов платформы не действует — их время ограничивает Runner; значение — [interfaces.md интеграции](icplan-integration-interfaces.md) | values, extraEnv |
| `RUNNER_OFFLINE_AFTER_S` (нужно) | api: порог «платформа не в сети» — параметр `runner.offline_after_s` | values, extraEnv |
| `REVIEW_REMINDER_HOURS` (нужно) | worker: напоминание о непроверенном результате — параметр `review_reminder_hours` ([interfaces.md автоподхвата](icplan-agent-autopickup-interfaces.md)) | values, extraEnv |
| `AGENT_RUN_RETENTION_DAYS` (нужно) | worker: срок завершённых запусков `agent_run` — параметр `runs.retention_days`; 0 — не чистить; задача очистки по образцу `cleanupOldDeliveries` / `WEBHOOK_CLEANUP_DAYS` (FR-13, AD-25) | values, extraEnv |
| `AGENT_CHAT_RETENTION_DAYS` (нужно) | worker: срок тредов чата агента — параметр `chat.retention_days`; 0 — не чистить (FR-13, AD-25) | values, extraEnv |

`protocol.version` — не переменная: версию протокола задаёт пакет `@itsaplan/runner` в образе api. Токен Telegram-бота в окружении не задаётся: бот читает его из БД (настройка god mode, `apps/bot/src/config.ts`).

## Сборка и поставка

| Шаг | Как в форке (`.github/workflows`) | Нужно (задача 4.6) |
|---|---|---|
| 1. Код | ветка `main` = upstream + модули `platform_` и миграции форка | — |
| 2. Проверки | `ci.yml`: jobs `quality`, `build`, `test` на push | обязательны перед публикацией |
| 3. Сборка | `publish-images.yml`: четыре образа из `apps/*/Dockerfile`, многостадийно; `@/cloud` web при сборке без `CLOUD_UI_ENTRY` указывает на заглушки `src/ce` (`apps/web/next.config.ts`), `ARG` для него в Dockerfile нет | базы — по digest; web собирается с `CLOUD_UI_ENTRY` = точка входа разделов «Платформа» (AD-24): `ARG CLOUD_UI_ENTRY` в `apps/web/Dockerfile` и `build-args` в `publish-images.yml` (4.6.10); без него разделы настроек Platform module в UI пустые |
| 4. SBOM и уязвимости | нет | `syft` (SBOM), `trivy` — выпуск блокируется при critical |
| 5. Публикация | `ghcr.io/demoningvi/itsaplan-app-<service>:X.Y.Z`; без суффикса пред-релиза двигается `latest`; тега с sha нет | `X.Y.Z` и `X.Y.Z-<sha>`; `latest` не используется |
| 6. Доставка | чарт `charts/itsaplan` | кластер тянет образы с pull-секретом `ghcr-pull` |

## Пример конфигурации

Значения — по `charts/itsaplan/values.yaml` форка и `interfaces.md` спек; новых значений здесь нет.

Ключи `extraEnv` и `extraVolumes` — доработка чарта (4.6.11); остальные ключи есть в чарте форка.

```yaml
imagePullSecrets: [{ name: ghcr-pull }]
podSecurityContext: { runAsNonRoot: true, runAsUser: 1000, fsGroup: 1000 }
securityContext:
  allowPrivilegeEscalation: false
  capabilities: { drop: [ALL] }
  readOnlyRootFilesystem: true
  seccompProfile: { type: RuntimeDefault }
extraVolumes: [{ name: tmp, emptyDir: {}, mountPath: /tmp }]   # api, web, worker, bot, init-контейнеры (4.6.11)
secrets:
  existingSecret: itsaplan-secrets   # DATABASE_URL, MIGRATION_DATABASE_URL, LITELLM_READ_URL, BETTER_AUTH_SECRET, APP_ENCRYPTION_KEY, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY
postgresql: { enabled: false }       # общий Postgres CloudNativePG
minio: { enabled: false }            # общий RustFS
externalDatabase: { url: "" }        # не задаём: при existingSecret DATABASE_URL берётся из Secret
externalS3: { endpoint: http://rustfs.itsaplan-data:9000 }
api:
  replicaCount: 2
  image: { repository: ghcr.io/demoningvi/itsaplan-app-api, tag: "X.Y.Z-<sha>" }
  env: { API_URL: "https://<api-хост>", APP_URL: "https://<web-хост>", S3_BUCKET: planner-attachments, TELEMETRY_DISABLED: "1" }
  extraEnv:
    SKIP_PRE_MIGRATION_BACKUP: "1"   # точка восстановления — PITR CloudNativePG
    SSRF_ALLOWED_HOSTS: "<хосты LiteLLM и Memory API в кластере>"
    AGENT_RUN_LEASE_SECONDS: "<interfaces.md>"
    AGENT_RUN_MAX_ATTEMPTS: "<interfaces.md>"
    AGENT_RUN_TIMEOUT_MS: "<interfaces.md>"
    RUNNER_OFFLINE_AFTER_S: "<interfaces.md>"
  backups: { persistence: { enabled: false } }
web:
  image: { repository: ghcr.io/demoningvi/itsaplan-app-web, tag: "X.Y.Z-<sha>" }
worker:
  image: { repository: ghcr.io/demoningvi/itsaplan-app-worker, tag: "X.Y.Z-<sha>" }
  extraEnv:
    AGENT_RUN_RETENTION_DAYS: "<runs.retention_days>"
    AGENT_CHAT_RETENTION_DAYS: "<chat.retention_days>"
    REVIEW_REMINDER_HOURS: "<review_reminder_hours>"
bot:
  image: { repository: ghcr.io/demoningvi/itsaplan-app-bot, tag: "X.Y.Z-<sha>" }
```

## Обновление и откат

1. Перед `helm upgrade` — точка восстановления: отметка времени для PITR CloudNativePG (дамп init-контейнера выключен, `SKIP_PRE_MIGRATION_BACKUP=1`, см. «Запуск»).
2. `helm upgrade`: init-контейнер `migrate` применяет миграции (только вперёд), затем стартуют api; worker и bot ждут миграций.
3. Откат образа без миграций — `helm rollback`.
4. Откат после миграции — `helm rollback` + восстановление схем ICPlan на отметку шага 1. PITR CloudNativePG восстанавливает кластер целиком, вместе со схемами Runner и Memory (AD-22), поэтому восстанавливаем **в отдельный кластер**, оттуда переносим только `public` и `platform` (`pg_dump -n public -n platform` → `pg_restore --clean` в рабочую базу); схемы `runner`, `harness_ckpt`, `memory` не трогаем. Запуски, созданные после отметки, пропадут из очереди ICPlan; их heartbeat получит 404, и Runner их остановит. Вложения RustFS не откатываются: восстановленная база может ссылаться на файлы, загруженные позже, — они остаются, недостающих нет.
5. Ключ `APP_ENCRYPTION_KEY` не меняется при откате: без того же ключа зашифрованные данные не читаются.

## Проверка после развёртывания

- [ ] `GET /` api = 200, `GET /login` web = 200
- [ ] Образы — из `ghcr.io/demoningvi`, встроенных `postgresql` и `minio` в релизе нет
- [ ] В web есть разделы «Платформа» (сборка с `CLOUD_UI_ENTRY`)
- [ ] Вход в web
- [ ] Создать задачу и делегировать агенту → запуск в очереди
- [ ] Поды запущены не от root (`runAsNonRoot`)
