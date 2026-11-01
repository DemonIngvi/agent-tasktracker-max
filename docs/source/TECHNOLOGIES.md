# Сводная таблица технологий

← README · [architecture.md](architecture.md) · [R&D](..\research\README.md)

Какое ПО выбрано, для чего, версия, лицензия, репозиторий и откуда качать. Данные репозиториев — GitHub API на **10.10.2026**. Статус — по Tech Radar: **Adopt** (используем), **Trial** (пробуем в задаче), **Assess** (изучаем), **Hold** (не используем / отложено).

## Платформа

| Технология | Назначение / компонент | Версия | Лицензия | Репозиторий | Откуда качать | Статус | R&D |
|---|---|---|---|---|---|---|---|
| It's a Plan (наш форк) | [ICPlan](../architecture/components/icplan/README.md) — трекер, UI, очередь | upstream v1.4.0 | AGPL-3.0 | [croffasia/itsaplan](https://github.com/croffasia/itsaplan) · форк [DemonIngvi/itsaplan-app](https://github.com/DemonIngvi/itsaplan-app) | `ghcr.io/croffasia/itsaplan-{api,web,worker,bot}`; сборка из форка | Adopt | [трекер](..\research\tracker-choice.md) |
| Bun | рантайм api / worker [ICPlan](../architecture/components/icplan/README.md) | 1.4.x | MIT | [oven-sh/bun](https://github.com/oven-sh/bun) | в образах [ICPlan](../architecture/components/icplan/README.md); [bun.sh](https://bun.sh) | Adopt (в составе [ICPlan](../architecture/components/icplan/README.md)) | — |
| Elysia | HTTP-фреймворк api [ICPlan](../architecture/components/icplan/README.md) | 1.4.x | MIT | [elysiajs/elysia](https://github.com/elysiajs/elysia) | npm `elysia` | Adopt (в составе) | — |
| Next.js | web [ICPlan](../architecture/components/icplan/README.md) | 16.x | MIT | [vercel/next.js](https://github.com/vercel/next.js) | npm `next` | Adopt (в составе) | — |
| Drizzle ORM | ORM [ICPlan](../architecture/components/icplan/README.md), [Platform module](../architecture/components/platform-module/README.md) | 0.45.x | Apache-2.0 | [drizzle-team/drizzle-orm](https://github.com/drizzle-team/drizzle-orm) | npm `drizzle-orm` | Adopt | — |
| Go | [Agent Runner](../architecture/components/agent-runner/README.md) | 1.2x | BSD-3-Clause | [golang/go](https://github.com/golang/go) | [go.dev/dl](https://go.dev/dl/), образ `golang` | Adopt | [Runner](..\research\runner-and-scheduling.md) |
| Python | [Harness](../architecture/components/harness/README.md), [Memory](../architecture/components/memory/README.md) API, mock-LLM | 3.12+ | PSF-2.0 | [python/cpython](https://github.com/python/cpython) | [python.org](https://www.python.org/downloads/), образ `python` | Adopt | — |
| Node.js | [ICPlan](../architecture/components/icplan/README.md) web (SSR) | 24 (образ `node:24-alpine`) | MIT | [nodejs/node](https://github.com/nodejs/node) | образ `node` | Adopt | [техспека ICPlan](..\architecture\components\icplan\docs\techspec.md) |
| FastAPI | [Memory](../architecture/components/memory/README.md) API, mock-LLM | 0.11x | MIT | [fastapi/fastapi](https://github.com/fastapi/fastapi) | PyPI `fastapi` | Adopt | [техспека Memory](..\architecture\components\memory\docs\techspec.md) |
| uv | Сборка Python-образов (`uv.lock`) | 0.x | Apache-2.0 / MIT | [astral-sh/uv](https://github.com/astral-sh/uv) | PyPI `uv` / образ `ghcr.io/astral-sh/uv` | Adopt | [техспека Harness](..\architecture\components\harness\docs\techspec.md) |
| LangGraph | [Harness](../architecture/components/harness/README.md): агентский цикл |  1.2.14 (закреплена, [AD-18](../architecture/decisions/AD-18.yaml)) | MIT | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | PyPI `langgraph` | Trial → Adopt после прототипа AG1–AG5 (задача 1.3.9) | [фреймворк](..\research\harness-framework.md) |
| LangChain MCP (`langchain.mcp`) | Tool Executor: MCP-тулы в LangGraph |  langchain 1.4.4, extra `mcp` (fastmcp ≥ 4.0.11) | MIT | [langchain-ai/langchain](https://github.com/langchain-ai/langchain/tree/master/libs/langchain_v1/langchain/mcp) | PyPI `langchain[mcp]` | Trial | [MCP](..\research\mcp-vs-direct.md) |
| MCP Python SDK | протокол MCP (зависимость `langchain[mcp]`) | v2.3.0 | MIT | [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | PyPI `mcp` | Adopt (косвенно) | [MCP](..\research\mcp-vs-direct.md) |
| ContextForge (IBM) | кандидат MCP-шлюза: виртуальные серверы из разрешённых тулов, JWT | v1.0.11 | Apache-2.0 | [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) | PyPI / образ | Assess (вопрос Q-MCP-01) | [MCP](..\research\mcp-vs-direct.md) |
| agentgateway | кандидат MCP-шлюза (Linux Foundation) | v1.6.0 | Apache-2.0 | [agentgateway/agentgateway](https://github.com/agentgateway/agentgateway) | GitHub Releases | Assess (вопрос Q-MCP-01) | [MCP](..\research\mcp-vs-direct.md) |
| langchain-mcp-adapters | адаптер MCP → LangChain | 0.3.2 | MIT | [langchain-ai/langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) | — | **Hold — архивирован**: перенесён в `langchain[mcp]` ([гайд миграции](https://docs.langchain.com/oss/python/migrate/langchain-mcp-adapters)) | — |
| LiteLLM Proxy | LLM gateway: алиасы, бюджеты, fallback |  v1.104.2 (закреплена, [AD-18](../architecture/decisions/AD-18.yaml)) | MIT ядро + платные enterprise-функции | [BerriAI/litellm](https://github.com/BerriAI/litellm) | `ghcr.io/berriai/litellm` | Adopt | [шлюз](..\research\llm-gateway.md) |
| Open Policy Agent | [Guardrails](../architecture/components/guardrails/README.md) G1 / G2 | v1.21.1 | Apache-2.0 | [open-policy-agent/opa](https://github.com/open-policy-agent/opa) | `openpolicyagent/opa` | Adopt | [движок](..\research\guardrails-engine.md) |
| LlamaFirewall (PurpleLlama) | детекторы для G4 и разбора запусков: PromptGuard 2, AlignmentCheck | — | лицензия Meta (проверить перед использованием) | [meta-llama/PurpleLlama](https://github.com/meta-llama/PurpleLlama) | PyPI `llamafirewall` | Assess | [guardrails](..\research\guardrails-engine.md) |
| Langfuse | LLM-трейсы, evals | v4.56.0 | MIT ядро + EE | [langfuse/langfuse](https://github.com/langfuse/langfuse) | `langfuse/langfuse` | Assess (бэклог) | [наблюдаемость](..\research\observability.md) |
| Phoenix (Arize) | разбор трасс и evals после MVP; Postgres | — | Elastic License 2.0 (по README) | [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) | PyPI / образ | Assess | [observability](..\research\observability.md) |
| Opik (Comet) | трассы, evals, оптимизация промптов после MVP | 2.2.96 | Apache-2.0 | [comet-ml/opik](https://github.com/comet-ml/opik) | образ | Assess | [observability](..\research\observability.md) |
| text-embeddings-inference | эмбеддинги для M4 / RAG | закреплена cpu-1.9.4 | Apache-2.0 | [huggingface/text-embeddings-inference](https://github.com/huggingface/text-embeddings-inference) | `ghcr.io/huggingface/text-embeddings-inference` | Assess (бэклог) | [RAG](..\research\rag.md) |

## Данные

| Технология | Назначение / компонент | Версия | Лицензия | Репозиторий | Откуда качать | Статус | R&D |
|---|---|---|---|---|---|---|---|
| Bifrost | запасной LLM gateway на Go (ключи, бюджеты с периодом) | — | Apache-2.0 | [maximhq/bifrost](https://github.com/maximhq/bifrost) | GitHub Releases | Assess (пилот, если LiteLLM не пройдёт порог 4.8.4) | [шлюз](..\research\llm-gateway.md) |
| TensorZero | LLM gateway с A/B-вариантами | 2026.6.0 | Apache-2.0 | [tensorzero/tensorzero](https://github.com/tensorzero/tensorzero) | — | **Hold — репозиторий архивирован 11.06.2026** | [шлюз](..\research\llm-gateway.md) |
| PostgreSQL | СУБД: [ICPlan](../architecture/components/icplan/README.md), платформа, LiteLLM, checkpoint | 17 | PostgreSQL License | [postgres/postgres](https://github.com/postgres/postgres) (зеркало) | `pgvector/pgvector:pg17` (сейчас); `ghcr.io/cloudnative-pg/postgresql:17` (CNPG) | Adopt | [СУБД](..\research\data-stores.md) |
| Mem0 | реализация адаптера `MemoryStore` по умолчанию ([AD-28](../architecture/decisions/AD-28.yaml)): извлечение фактов, разрешение противоречий | ts-v3.3.1 | Apache-2.0 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | PyPI `mem0ai` | Assess (M4 после MVP) | [память](..\research\memory-model.md) |
| LangMem | кандидат движка M4: память для LangGraph поверх Postgres store | — | MIT | [langchain-ai/langmem](https://github.com/langchain-ai/langmem) | PyPI `langmem` | Assess (M4 после MVP) | [память](..\research\memory-model.md) |
| Graphiti (Zep) | временной граф знаний: срок действия факта | v0.30.2 | Apache-2.0 | [getzep/graphiti](https://github.com/getzep/graphiti) | PyPI `graphiti-core` | Assess (нужна графовая БД — берём только идею срока действия) | [память](..\research\memory-model.md) |
| pgvector | векторы для M4 и адаптера `MemoryStore` (HNSW; [AD-28](../architecture/decisions/AD-28.yaml)) | — | PostgreSQL License | [pgvector/pgvector](https://github.com/pgvector/pgvector) | в образе `pgvector/pgvector:pg17` | Assess | [RAG](..\research\rag.md) |
| DSPy + GEPA | реализация адаптера `PromptOptimizer` ([AD-28](../architecture/decisions/AD-28.yaml)): пакетная оптимизация промптов на отложенном наборе | — | MIT | [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | PyPI `dspy` | Assess (после MVP модулей «факты» и «плейбук») | [цепочка агентов](..\research\agent-chain.md) |
| CloudNativePG | оператор Postgres: бэкап, пулер | v1.30.1 | Apache-2.0 | [cloudnative-pg/cloudnative-pg](https://github.com/cloudnative-pg/cloudnative-pg) | Helm `cloudnative-pg.github.io/charts` | Trial (4.7) | [СУБД](..\research\data-stores.md) |
| PgBouncer | пул соединений Postgres | 1.26.0 | ISC | [pgbouncer/pgbouncer](https://github.com/pgbouncer/pgbouncer) | в составе Pooler CloudNativePG | Adopt | [балансировка](..\research\ingress-and-balancing.md) |
| RustFS | объектное хранилище (S3) | 1.0.x | Apache-2.0 | [rustfs/rustfs](https://github.com/rustfs/rustfs) | `rustfs/rustfs` | Adopt | [СУБД](..\research\data-stores.md) |
| SeaweedFS | запасное S3-хранилище | 4.48 | Apache-2.0 | [seaweedfs/seaweedfs](https://github.com/seaweedfs/seaweedfs) | `chrislusf/seaweedfs` | Assess | [СУБД](..\research\data-stores.md) |
| MinIO | S3-хранилище | 2025-10-15 | AGPL-3.0 | [minio/minio](https://github.com/minio/minio) | — | **Hold — архивирован 24.04.2026** | [СУБД](..\research\data-stores.md) |

## Инфраструктура

| Технология | Назначение / компонент | Версия | Лицензия | Репозиторий | Откуда качать | Статус | R&D |
|---|---|---|---|---|---|---|---|
| k3s | кластер Kubernetes | v1.37.1+k3s1 | Apache-2.0 | [k3s-io/k3s](https://github.com/k3s-io/k3s) | `curl -sfL https://get.k3s.io` | Adopt | [Kubernetes](..\research\kubernetes-runtime.md) |
| k3d | локальный кластер (k3s в Docker) | v5.9.0 | MIT | [k3d-io/k3d](https://github.com/k3d-io/k3d) | GitHub Releases | Adopt | [Kubernetes](..\research\kubernetes-runtime.md) |
| RKE2 | дистрибутив Kubernetes с CIS-защитой — запасной к k3s | v1.37.1+rke2r1 | Apache-2.0 | [rancher/rke2](https://github.com/rancher/rke2) | GitHub Releases | Assess (CIS-аудит или второй узел) | [Kubernetes](..\research\kubernetes-runtime.md) |
| Talos | неизменяемая ОС для Kubernetes без SSH | v1.14.2 | MPL-2.0 | [siderolabs/talos](https://github.com/siderolabs/talos) | образ ОС | Assess | [Kubernetes](..\research\kubernetes-runtime.md) |
| Kueue | квоты и допуск задач в K8s при нескольких узлах | v0.20.1 | Apache-2.0 | [kubernetes-sigs/kueue](https://github.com/kubernetes-sigs/kueue) | Helm | Assess | [Kubernetes](..\research\kubernetes-runtime.md), [Runner](..\research\runner-and-scheduling.md) |
| Helm | упаковка и развёртывание | v4.3.0 | Apache-2.0 | [helm/helm](https://github.com/helm/helm) | [get.helm.sh](https://get.helm.sh) | Adopt | [Kubernetes](..\research\kubernetes-runtime.md) |
| Traefik | ingress, TLS | v3.7 (в составе k3s) | MIT | [traefik/traefik](https://github.com/traefik/traefik) | в составе k3s | Adopt | [ingress](..\research\ingress-and-balancing.md) |
| ingress-nginx | ingress | controller-v1.15.1 | Apache-2.0 | [kubernetes/ingress-nginx](https://github.com/kubernetes/ingress-nginx) | — | **Hold — архивирован 23.03.2026** | [ingress](..\research\ingress-and-balancing.md) |
| Gateway API | стандарт маршрутов Kubernetes (HTTPRoute) для входа через Traefik | v1.6.3 | Apache-2.0 | [kubernetes-sigs/gateway-api](https://github.com/kubernetes-sigs/gateway-api) | CRD | Adopt | [ingress](..\research\ingress-and-balancing.md) |
| Docker Engine (Moby) | контейнеры, sandbox (этапы 1–3) | 29.x | Apache-2.0 | [moby/moby](https://github.com/moby/moby) | [docs.docker.com/engine/install](https://docs.docker.com/engine/install/) | Adopt | [изоляция](..\research\sandbox-isolation.md) |
| Squid | egress-прокси с allowlist доменов (G3) | образ `ubuntu/squid` 6.x (upstream 7.7) | GPL-2.0 (отдельный процесс) | [squid-cache/squid](https://github.com/squid-cache/squid) | пакеты ОС / образ | Trial ([AD-18](../architecture/decisions/AD-18.yaml): Squid; mitmproxy отклонён — расшифровка TLS не нужна и добавляет риск) | [изоляция](..\research\sandbox-isolation.md) |
| gVisor (runsc) | усиленная изоляция ядра контейнера sandbox без KVM | release-20261005.0 | Apache-2.0 | [google/gvisor](https://github.com/google/gvisor) | [gvisor.dev](https://gvisor.dev/docs/user_guide/install/) | Assess (проверка в задаче 2.2.8) | [изоляция](..\research\sandbox-isolation.md) |
| kubernetes-sigs/agent-sandbox | тёплый пул sandbox как объект K8s (этап 4) | v1.0.6 | Apache-2.0 | [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | GitHub Releases | Assess | [изоляция](..\research\sandbox-isolation.md), [Kubernetes](..\research\kubernetes-runtime.md) |
| Daytona | песочницы для агентов | v0.190.0 | не определена | [daytonaio/daytona](https://github.com/daytonaio/daytona) | — | **Hold — репозиторий архивирован 24.07.2026** | [изоляция](..\research\sandbox-isolation.md) |
| Firecracker | microVM — будущий провайдер sandbox | v1.17.0 | Apache-2.0 | [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker) | GitHub Releases | Assess | [изоляция](..\research\sandbox-isolation.md) |
| k6 | нагрузочный тест | v2.3.0 | AGPL-3.0 | [grafana/k6](https://github.com/grafana/k6) | `grafana/k6` | Trial (4.8) | [нагрузка](..\research\load-profile.md) |
| Prometheus | метрики | v3.15.0 | Apache-2.0 | [prometheus/prometheus](https://github.com/prometheus/prometheus) | `prom/prometheus` | Hold (бэклог) | — |
| Grafana | дашборды | v13.2.3 | AGPL-3.0 | [grafana/grafana](https://github.com/grafana/grafana) | `grafana/grafana` | Hold (бэклог) | — |
| Loki | логи | v3.7.8 | AGPL-3.0 | [grafana/loki](https://github.com/grafana/loki) | `grafana/loki` | Hold (бэклог) | — |
| Gitea | git и CI | v28.1.0 | MIT | [go-gitea/gitea](https://github.com/go-gitea/gitea) | `gitea/gitea` | Hold (бэклог) | — |
| Argo CD | GitOps | v3.5.4 | Apache-2.0 | [argoproj/argo-cd](https://github.com/argoproj/argo-cd) | Helm `argoproj.github.io/argo-helm` | Hold (бэклог) | [Kubernetes](..\research\kubernetes-runtime.md) |
| Sealed Secrets | секреты для GitOps | v0.40.0 | Apache-2.0 | [bitnami-labs/sealed-secrets](https://github.com/bitnami-labs/sealed-secrets) | GitHub Releases | Hold (бэклог) | — |
| Trivy | сканирование образов | v0.75.0 | Apache-2.0 | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | `aquasec/trivy` | Hold (бэклог) | — |
| Syft | SBOM образов в CI | 1.x | Apache-2.0 | [anchore/syft](https://github.com/anchore/syft) | релизы GitHub / образ `anchore/syft` | Adopt | правило техспеки |
| distroless | База образа Runner | `static:nonroot` | Apache-2.0 | [GoogleContainerTools/distroless](https://github.com/GoogleContainerTools/distroless) | `gcr.io/distroless/static` | Adopt | [техспека Runner](..\architecture\components\agent-runner\docs\techspec.md) |
| GitHub Container Registry | Реестр образов платформы (`ghcr.io/demoningvi/*`) | — | сервис GitHub | [docs](https://docs.github.com/packages) | ghcr.io | Adopt | правило техспеки |

## Документация

| Технология | Назначение | Версия | Лицензия | Репозиторий | Откуда качать | Статус |
|---|---|---|---|---|---|---|
| OpenSpec | спеки SDD | v1.14.1 | MIT | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | npm `@fission-ai/openspec` | Adopt |
| MkDocs | генератор сайта | 1.6.1 | BSD-2-Clause | [mkdocs/mkdocs](https://github.com/mkdocs/mkdocs) | PyPI `mkdocs` | Adopt (версия закреплена) |
| Material for MkDocs | тема сайта | 9.7.7 | MIT | [squidfunk/mkdocs-material](https://github.com/squidfunk/mkdocs-material) | PyPI `mkdocs-material` | Adopt |

## Лицензионные риски

| Лицензия | Где | Что значит для нас |
|---|---|---|
| AGPL-3.0 | It's a Plan (форк) | доработки форка, доступного пользователям по сети, должны быть открыты — репозиторий форка держим доступным пользователям; сервисы платформы (Runner, [Harness](../architecture/components/harness/README.md), [Memory](../architecture/components/memory/README.md) API) — отдельные программы, код закрыт ([AD-18](../architecture/decisions/AD-18.yaml)) |
| AGPL-3.0 | Grafana, Loki, k6 | используем без изменений — обязательств по раскрытию нет |
| MIT ядро + коммерческие функции | LiteLLM, Langfuse | используем только открытые функции; enterprise — отдельное решение |
| GPL-2.0 | Squid | отдельный процесс без изменений — обязательств нет |

## Архивированные проекты (не использовать)

ingress-nginx → Traefik; MinIO → RustFS; langchain-mcp-adapters → `langchain[mcp]` (официальный перенос в LangChain).
