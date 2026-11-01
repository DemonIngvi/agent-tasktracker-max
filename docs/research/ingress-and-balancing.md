# R&D: Вход и балансировка

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Инфраструктура](../architecture/components/infrastructure/README.md)** · решение: [design AD-15, AD-18](..\source\design\define-agent-platform\design.md) · спека: platform-infrastructure

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Как пользователи и MCP-клиенты попадают в платформу по HTTPS, как запросы распределяются между репликами, а админки остаются закрытыми?

<div class="rnd-a">Ответ: Traefik из k3s — вход и TLS (ACME); маршруты описываем через Gateway API (HTTPRoute), а не Ingress, чтобы не зависеть от контроллера. Балансировку между репликами делает Service; пул соединений с Postgres — PgBouncer.</div>

<span class="rnd-badge adopt">Adopt</span> Traefik v3.7 (в k3s) · Gateway API v1.6 · PgBouncer 1.26 · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П6
> Traefik закрывает всё и уже стоит в k3s; Gateway API делает маршруты переносимыми
stack Traefik + Gateway API: 6 ok, 0 part, 0 no
stack Envoy Gateway: 5 ok, 1 part, 0 no
stack NGINX Gateway Fabric: 4 ok, 2 part, 0 no
stack HAProxy Ingress: 4 ok, 2 part, 0 no
# Что ставить сверх k3s
> Traefik и ACME уже в k3s; остальным нужен контроллер и cert-manager
bar Traefik: 0/2 ничего ok
bar Envoy Gateway: 2/2 контроллер + cert-manager part
bar HAProxy Ingress: 2/2 контроллер + cert-manager part
# Объём доработки
> у Traefik вход — одна подзадача 4.6.3 из 55 ч задачи 4.6; у остальных кандидатов оценок задач нет
bar 4.6.3 Traefik, TLS ACME, маршруты HTTPRoute: 4/55 ч ok
# Позиции ролей
side Traefik | Envoy Gateway
pos DevOps: -2 | уже в k3s, ACME встроен
pos Архитектор: -1 | Gateway API — переносимые маршруты
pos Безопасность: 0 | админки без маршрутов у обоих
pos Разработчик: 1 | Envoy сильнее в политиках трафика
# Что меняется
> AD-15 подтверждён; маршруты — Gateway API
stack Документы: 3 ok, 0 part, 3 mute
- ✅ задача 4.6: маршруты через HTTPRoute · ✅ TECHNOLOGIES: Gateway API, ingress-nginx архивирован 23.03.2026
```

**Почему Traefik и Gateway API.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Вход уже есть в k3s**

Traefik ставится вместе с k3s и получает сертификаты по ACME сам. Envoy Gateway, NGINX Gateway Fabric и HAProxy Ingress требуют отдельного контроллера и cert-manager. Для одного узла и трёх маршрутов (web, api, mcp) этого хватает ([Э9](#e9)).
</div>
<div markdown>
**2. Маршруты — на стандарте, а не на контроллере**

ingress-nginx архивирован (23.03.2026) — вот цена привязки к контроллеру. Gateway API — стандарт Kubernetes; Traefik поддерживает его в рабочем режиме с v3.1. Маршруты в HTTPRoute переносятся на другой контроллер без переписывания ([Э6](#e6)).
</div>
<div markdown>
**3. Админки — без маршрутов вообще**

LiteLLM UI, OPA и админ-API не получают маршрутов: доступ к ним — через `kubectl port-forward` по SSH. Это проще и надёжнее, чем закрывать их правилами на входе ([Э7](#e7)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- Traefik из k3s, TLS по ACME;
- Service (ClusterIP) для балансировки между репликами;
- PgBouncer в режиме transaction;
- админки без маршрутов.
</div>
<div class="adapt" markdown>
**Адаптируем**

- маршруты Ingress → Gateway API HTTPRoute (Traefik через HelmChartConfig k3s);
- политики трафика Envoy Gateway (лимиты, повторы) → лимиты на входе Traefik middleware при необходимости.
</div>
<div class="drop" markdown>
**Не берём**

- ingress-nginx: архивирован;
- сервисную сеть (mesh) и mTLS до этапа 4 ([AD-18](../architecture/decisions/AD-18.yaml));
- внешний балансировщик: один узел.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **ingress-nginx** — репозиторий архивирован 23.03.2026.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Gateway API в k3s требует CRD и настройки Traefik — проверка в 4.6.3.
- Пересмотр: нужны сложные политики трафика между сервисами → Envoy Gateway.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**6 <span class="gate">G2</span></div>
<div markdown>**Э3 Traefik**5 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**6 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I21](../architecture/integrations/I21.yaml), [I22](../architecture/integrations/I22.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**4 роли <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**6 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** Платформа на k3s ([AD-15](../architecture/decisions/AD-15.yaml)). Наружу смотрят web и api [ICPlan](../architecture/components/icplan/README.md) и MCP [ICPlan](../architecture/components/icplan/README.md); у api и LiteLLM по две реплики.

**Осложнение.** ingress-nginx, самый распространённый контроллер, архивирован. Стандарт Gateway API вытесняет Ingress.

**Вопрос.** Чем принимать вход и как описывать маршруты?

**Решает:** владелец продукта с DevOps. **Не решаем:** кластер ([Kubernetes](kubernetes-runtime.md)), Postgres ([хранилища](data-stores.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml).

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | HTTPS с автоматическими сертификатами | [FR-161](../architecture/components/infrastructure/prd.md) | ручное продление, просроченный сертификат |
| П2 | маршруты web, api, mcp | [FR-161](../architecture/components/infrastructure/prd.md) | пользователи и MCP-клиенты не попадают |
| П3 | распределение по репликам | [FR-162](../architecture/components/infrastructure/prd.md) | одна реплика держит всю нагрузку |
| П4 | админки закрыты | [FR-161](../architecture/components/infrastructure/prd.md), [AD-18](../architecture/decisions/AD-18.yaml) | LiteLLM и OPA доступны снаружи |
| П5 | живой проект контроллера | — | вход без обновлений безопасности |
| П6 | без лишних компонентов на одном узле | [AD-15](../architecture/decisions/AD-15.yaml) | ещё контроллеры |

<span class="gate">G2</span> ✅ у потребностей есть требования.

## Э3. Опорное решение: Traefik из k3s {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Контроллер в составе k3s | вход без установки | П6 |
| F2 | ACME | сертификаты автоматически | П1 |
| F3 | Ingress и Gateway API | маршруты | П2 |
| F4 | Middleware | лимиты, заголовки | — |
| F5 | Service (ClusterIP) в Kubernetes | балансировка между репликами | П3 |

**Вывод этапа.** Traefik закрывает П1–П6; вопрос — в каком формате описывать маршруты.

<span class="gate">G3</span> ✅ функции из документации Traefik и k3s (Б).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub, документация Traefik, Gateway API.

| Кандидат | Ключевые функции | Чего нет у опорного | Уровень |
|---|---|---|---|
| **Envoy Gateway** (Apache-2.0, 3 073★, v1.9.2) | Gateway API на Envoy; политики трафика (лимиты, повторы, авторизация) | богатые политики | Б |
| **NGINX Gateway Fabric** (Apache-2.0, 1 175★, v2.7.2) | Gateway API на nginx | — | Б |
| **HAProxy Ingress** (Apache-2.0, 869★, v3.2.16) | ingress на HAProxy | тонкая балансировка | Б |
| **ingress-nginx** (19 454★) | ingress на nginx; **архивирован 23.03.2026** | — | Б |
| **Gateway API** (стандарт, v1.6.3) | HTTPRoute, GRPCRoute; переносимость между контроллерами | стандарт маршрутов | Б |
| **cert-manager** (Apache-2.0, 14 107★) | сертификаты для любых контроллеров | — | Б |

**Вывод этапа.** Контроллеры на Gateway API различаются политиками трафика; стандарт маршрутов у них общий.

<span class="gate">G4</span> ✅ 6 кандидатов; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| ACME | П1 | сертификат не истекает | Traefik (Б); cert-manager (Б) | базовая |
| Живой проект | П5 | обновления безопасности | ingress-nginx архивирован (Б) | базовая |
| Без установки на k3s | П6 | меньше компонентов | k3s (Б) | базовая |
| Маршруты на стандарте | П2 | смена контроллера без переписывания | Gateway API; Traefik — рабочий режим с v3.1 (Б) | линейная |
| Политики трафика | — | лимиты и авторизация на входе | Envoy Gateway (Б) | привлекательная |

**Вывод этапа.** Базовые функции есть у Traefik; переносимость маршрутов даёт Gateway API.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| Traefik, ACME, Service, PgBouncer | оставить | [AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml) | [FR-161](../architecture/components/infrastructure/prd.md) – [FR-163](../architecture/components/infrastructure/prd.md) |
| Маршруты Gateway API | адаптировать | HTTPRoute для web, api, mcp; включить провайдер Gateway API в Traefik через HelmChartConfig k3s | подзадача 4.6.3 |
| Политики трафика | не брать сейчас | при необходимости — middleware Traefik | — |
| ingress-nginx, mesh | не брать | Э5, [AD-18](../architecture/decisions/AD-18.yaml) | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** живой проект | П5 → базовая | не архивирован |
| **M2** HTTPS по ACME | П1 → базовая | встроено или cert-manager |
| **M3** работает на k3s | П6 | поддержка |
| **К1** компоненты сверх k3s | П6 | что ставить |
| **К2** стандарт маршрутов | П2 | Gateway API |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

| Кандидат | M1 жив | M2 ACME | M3 k3s | Итог |
|---|---|---|---|---|
| Traefik | да | да: встроено | да | проходит |
| Envoy Gateway | да | да: cert-manager | да | проходит |
| NGINX Gateway Fabric | да | да: cert-manager | да | проходит |
| HAProxy Ingress | да | да: cert-manager | да | проходит |
| ingress-nginx | **нет** | да | да | ✗ |

```
 пользователи, MCP-клиенты ──I21 HTTPS──▶ Traefik (Gateway, ACME) ── HTTPRoute* ──▶ Service web / api / mcp ──▶ реплики
 админки (LiteLLM UI, OPA) — без маршрутов: kubectl port-forward по SSH
 сервисы ──I22──▶ PgBouncer ──▶ Postgres
  * — Gateway API вместо Ingress (4.6.3)
```

| Стык | Traefik | Envoy Gateway | HAProxy Ingress |
|---|---|---|---|
| [I21](../architecture/integrations/I21.yaml) вход | И2: в k3s | И1: контроллер, cert-manager | И1 |
| [I22](../architecture/integrations/I22.yaml) к Postgres | И2: PgBouncer, не зависит от входа | И2 | И2 |

**Изменения у соседей:** нет; Gateway API меняет только манифесты маршрутов в чартах (задача 4.6).

**Вывод этапа.** ==Traefik встаёт без новых компонентов; Gateway API меняет только формат маршрутов.==

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| DevOps 🤖 | Traefik | в k3s, ACME встроен | Gateway API в k3s требует CRD | проверка в 4.6.3 |
| Архитектор 🤖 | Traefik + Gateway API | маршруты переносимы | — | — |
| Безопасность 🤖 | нейтрально | админки без маршрутов в любом варианте | — | — |
| Разработчик 🤖 (оппонент) | Envoy Gateway | политики трафика богаче | лимиты на входе | middleware Traefik |

| Спор | Разрешение |
|---|---|
| Разработчик: «Envoy богаче» | **условие:** пересмотр при сложных политиках между сервисами |
| Адвокат дьявола: «Traefik тоже могут закрыть» | **условие:** маршруты на Gateway API — замена контроллера без переписывания |

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | Traefik + Gateway API | Envoy Gateway | NGINX Gateway Fabric | HAProxy Ingress |
|---|---|---|---|---|
| П1 ACME | закрывает | с доработкой: cert-manager | с доработкой | с доработкой |
| П2 маршруты | закрывает | закрывает | закрывает | закрывает |
| П3 реплики | закрывает | закрывает | закрывает | закрывает |
| П4 админки закрыты | закрывает | закрывает | закрывает | закрывает |
| П5 жив | закрывает | закрывает | закрывает | закрывает |
| П6 без компонентов | закрывает | частично | частично | частично |

- **Утверждение.** Traefik из k3s, маршруты на Gateway API ([AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml)).
- **Основания.** Закрывает все 6 потребностей без новых компонентов.
- **Связка.** Архивация ingress-nginx показала цену привязки к контроллеру; стандарт маршрутов её снимает.
- **Опровержение.** Вывод неверен, если понадобятся политики трафика уровня Envoy. Тогда — Envoy Gateway с теми же HTTPRoute.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Маршруты web, api, mcp — Gateway API HTTPRoute | [задача 4.6](..\source\tasks\4.6-k8s-helm-ingress.md) (подзадача 4.6.3) | ✅ внесено |
| Gateway API — Adopt; ingress-nginx — архивирован 23.03.2026 | [TECHNOLOGIES](..\source\TECHNOLOGIES.md) | ✅ внесено |
| Решения [AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml) | design | ✅ подтверждено, без изменений |
| Стыки [I21](../architecture/integrations/I21.yaml), [I22](../architecture/integrations/I22.yaml) | спека platform-infrastructure | — не требуется |
| Техспека инфраструктуры | [техспека](..\architecture\components\infrastructure\docs\techspec.md) | — не требуется |
| Требование «Ingress и TLS» | [FR-161](../architecture/components/infrastructure/prd.md) | — не требуется: формат маршрутов не задан требованием |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| Traefik | MIT | 65 153 | v3.7.14 | 08.10.2026 |
| ingress-nginx | Apache-2.0 | 19 454 | controller-v1.15.1 | **архивирован**, 23.03.2026 |
| cert-manager | Apache-2.0 | 14 107 | v1.21.2 | 11.10.2026 |
| Envoy Gateway | Apache-2.0 | 3 073 | v1.9.2 | 10.10.2026 |
| Gateway API | Apache-2.0 | 3 016 | v1.6.3 | 09.10.2026 |
| NGINX Gateway Fabric | Apache-2.0 | 1 175 | v2.7.2 | 11.10.2026 |
| HAProxy Ingress | Apache-2.0 | 869 | v3.2.16 | 07.10.2026 |
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- Traefik: [Gateway API](https://doc.traefik.io/traefik/v3.3/reference/routing-configuration/kubernetes/gateway-api/) (Б), [Kubernetes, v3.7](https://doc.traefik.io/traefik/v3.7/getting-started/kubernetes/) (Б), [Gateway API и Traefik (сообщество)](https://community.traefik.io/t/getting-started-with-kubernetes-gateway-api-and-traefik/23601) (В), [k3s + Traefik + Gateway API](https://kodekloud.com/community/t/issues-with-k3s-traefik-gateway-api-tcp-udproute/493601) (В)
- [Gateway API](https://github.com/kubernetes-sigs/gateway-api) (Б) · [Envoy Gateway](https://github.com/envoyproxy/gateway) (Б) · [NGINX Gateway Fabric](https://github.com/nginx/nginx-gateway-fabric) (Б) · [HAProxy Ingress](https://github.com/haproxytech/kubernetes-ingress) (Б) · [ingress-nginx — архивирован](https://github.com/kubernetes/ingress-nginx) (Б)
- Наши: [AD-15, AD-18](..\source\design\define-agent-platform\design.md) (А)
