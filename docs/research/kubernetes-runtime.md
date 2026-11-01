# R&D: Kubernetes и упаковка платформы

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Инфраструктура](../architecture/components/infrastructure/README.md)** · решение: [design AD-15, AD-16, AD-18](..\source\design\define-agent-platform\design.md) · спека: platform-infrastructure

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
На чём запускать платформу на своём сервере: какой Kubernetes, как упаковывать, как изолировать агентов — и что из этого нужно уже на этапах 1–3, а что на этапе 4?

<div class="rnd-a">Ответ: k3s на одном узле + Helm-чарты, локально — k3d; на этапах 1–2 — docker compose. Защиту узла берём из CIS-рекомендаций (как в RKE2). На этапе 4 Runner создаёт среды через K8s API — для этого добавлена недостающая подзадача, кандидат провайдера — agent-sandbox.</div>

<span class="rnd-badge adopt">Adopt</span> k3s v1.37.1, Helm v4.3.0, k3d v5.9.0 · <span class="rnd-badge assess">Assess</span> agent-sandbox, Kueue · <span class="rnd-badge hold">Hold</span> ArgoCD · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П8
> k3s закрывает один узел и простую эксплуатацию; RKE2 и Talos сильнее в защите, но тяжелее
stack k3s + Helm: 7 ok, 1 part, 0 no
stack RKE2: 6 ok, 2 part, 0 no
stack k0s: 6 ok, 2 part, 0 no
stack Talos: 5 ok, 2 part, 1 no
stack kubeadm: 4 ok, 3 part, 1 no
stack Docker Compose: 3 ok, 1 part, 4 no
# Этап 4: что нужно поверх кластера
> провайдер sandbox для K8s не был запланирован — теперь подзадача 4.6.8
bar Кластер, чарты, сеть: 1/1 задача 4.6 ok
bar Провайдер sandbox в K8s: 1/1 добавлен — 4.6.8 part
bar Ёмкость узлов (Kueue): 0/1 не нужно на одном узле info
# Объём доработки
> k3s: кластер, провайдер sandbox и CIS-проверка — 15 ч по подзадачам задачи 4.6; у остальных кандидатов оценок задач нет
bar 4.6.1 k3s, namespaces, ServiceAccount: 4/15 ч ok
bar 4.6.8 провайдер сред в K8s (I23): 8/15 ч part
bar 4.6.9 CIS-проверка узла (kube-bench): 3/15 ч ok
# Позиции ролей
side k3s | RKE2
pos DevOps: -2 | один бинарник, порог эксплуатации низкий
pos Владелец продукта: -1 | сроки этапа 4
pos Архитектор: -1 | всё, что нужно, есть: NetworkPolicy, SA, RuntimeClass
pos Безопасность: 2 | RKE2 защищён по CIS из коробки
# Что меняется
> AD-15 и AD-16 подтверждены; провайдер sandbox для K8s добавлен в 4.6
stack Документы: 5 ok, 0 part, 3 mute
- ✅ задача 4.6: провайдер sandbox (Pod или agent-sandbox, RuntimeClass) · ✅ CIS-проверка узла
- ✅ TECHNOLOGIES: RKE2, Talos, Kueue — Assess · ✅ FR-159: сценарий CIS
```

**Почему k3s.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Один узел — один бинарник**

На этапах 1–3 сервер один ([AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml)). k3s поставляется одним бинарником с Traefik, хранилищем томов и встроенной БД кластера. kubeadm и облачный Kubernetes рассчитаны на несколько узлов. Всё нужное агентам есть: NetworkPolicy, ServiceAccount, RuntimeClass ([Э9](#e9)).
</div>
<div markdown>
**2. Защиту узла берём у RKE2, не меняя дистрибутив**

RKE2 закрывает рекомендации CIS из коробки. У k3s есть руководство по CIS-защите, и его можно применить к нашему узлу. Talos ещё строже (ОС без SSH, управление через API), но требует отдельной ОС на сервере. Поэтому берём функцию, а не продукт ([Э6](#e6)).
</div>
<div markdown>
**3. Встраивание вскрыло пропуск в задачах**

На этапе 4 Runner создаёт среды через K8s API ([I23](../architecture/components/agent-runner/integrations/I23.yaml), `provider: k8s`), но ни одна задача этого не делала. Добавлена подзадача 4.6.8. В ней — выбор между своим Pod и agent-sandbox (тёплый пул как объект K8s, RuntimeClass gVisor), который пришёл из [R&D изоляции](sandbox-isolation.md) ([Э7](#e7)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- k3s на одном узле, k3d локально;
- Helm-чарты с `existingSecret`;
- namespaces `itsaplan-core`, `-data`, `-agents`, `-platform`;
- NetworkPolicy по [I1](../architecture/components/agent-runner/integrations/I1.yaml)–[I23](../architecture/components/agent-runner/integrations/I23.yaml);
- ServiceAccount Runner только на `itsaplan-agents`.
</div>
<div class="adapt" markdown>
**Адаптируем**

- CIS-профиль (RKE2) → проверка узла k3s по CIS (kube-bench);
- тёплый пул как объект K8s (agent-sandbox) → кандидат провайдера в 4.6.8;
- RuntimeClass gVisor → после проверки 2.2.8;
- ёмкость по квотам (Kueue) → только при нескольких узлах.
</div>
<div class="drop" markdown>
**Не берём**

- облачный Kubernetes: своё железо ([AD-18](../architecture/decisions/AD-18.yaml));
- Talos: отдельная ОС на сервере;
- ArgoCD и Flux на этапах 1–4: деплой скриптами и Helm, GitOps — бэклог;
- HA на этапах 1–3.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **Облачный Kubernetes** — своё размещение ([AD-18](../architecture/decisions/AD-18.yaml)).
- **Docker Compose для этапа 4** — нет NetworkPolicy и ServiceAccount; остаётся для этапов 1–2.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Один узел — единая точка отказа; HA — после этапа 4.
- Пересмотр: второй узел или требования CIS-аудита → RKE2 (та же модель, что у k3s).
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**8 <span class="gate">G2</span></div>
<div markdown>**Э3 k3s + Helm**7 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**10 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I21](../architecture/integrations/I21.yaml), [I23](../architecture/components/agent-runner/integrations/I23.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**5 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**8 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** Платформа разворачивается на своём сервере ([AD-18](../architecture/decisions/AD-18.yaml)). Проект AI-агент принял k3s, k3d и чарты с `existingSecret` (решения 7.11–7.14).

**Осложнение.** Лёгких дистрибутивов несколько (k3s, k0s, MicroK8s), есть защищённые (RKE2, Talos). Агенты исполняют код, поэтому изоляцию задают и кластер, и узел.

**Вопрос.** Какой Kubernetes и какая упаковка?

**Решает:** владелец продукта с DevOps. **Не решаем:** вход и балансировку ([ingress](ingress-and-balancing.md)), хранилища ([хранилища](data-stores.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-15](../architecture/decisions/AD-15.yaml), [AD-16](../architecture/decisions/AD-16.yaml), [AD-18](../architecture/decisions/AD-18.yaml).

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | один узел на этапах 1–3 | [AD-15](../architecture/decisions/AD-15.yaml), [AD-18](../architecture/decisions/AD-18.yaml) | лишние узлы и затраты |
| П2 | сетевая изоляция между namespace и агентами | [FR-167](../architecture/components/infrastructure/prd.md) | агенты ходят к БД и админкам |
| П3 | ServiceAccount Runner только на namespace агентов | [AD-18](../architecture/decisions/AD-18.yaml), [I23](../architecture/components/agent-runner/integrations/I23.yaml) | Runner управляет всем кластером |
| П4 | упаковка с секретами вне git | [FR-160](../architecture/components/infrastructure/prd.md), [FR-166](../architecture/components/infrastructure/prd.md) | секреты в чартах |
| П5 | своё железо | [AD-18](../architecture/decisions/AD-18.yaml) | облако |
| П6 | эксплуатация одной командой | [AD-15](../architecture/decisions/AD-15.yaml) | экспертиза под тяжёлый кластер |
| П7 | локальная среда как прод | [FR-169](../architecture/components/infrastructure/prd.md) | «у меня работает» |
| П8 | на этапе 4 Runner создаёт среды через K8s API | [FR-90](../architecture/components/sandbox/prd.md) (`provider`), [I23](../architecture/components/agent-runner/integrations/I23.yaml) | этап 4 без провайдера |

<span class="gate">G2</span> ✅ у потребностей есть требования и решения.

## Э3. Опорное решение: k3s + Helm {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Один бинарник, встроенная БД кластера | кластер на одном узле | П1, П6 |
| F2 | Traefik, хранилище томов в комплекте | вход и тома без установки | П6 |
| F3 | NetworkPolicy (встроенный контроллер) | изоляция трафика | П2 |
| F4 | ServiceAccount и RBAC | права Runner на namespace | П3 |
| F5 | RuntimeClass | подключение gVisor или Kata | П8 |
| F6 | Helm-чарты с `existingSecret` | секреты вне git | П4 |
| F7 | k3d | k3s в Docker локально | П7 |

**Вывод этапа.** k3s закрывает П1–П7. П8 — частично: платформа даёт API, но провайдера среды в задачах нет.

<span class="gate">G3</span> ✅ функции из документации k3s (Б) и [AD-15](../architecture/decisions/AD-15.yaml) (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub, CNCF Landscape (дистрибутивы, планировщики), документация.

| Кандидат | Ключевые функции | Чего нет у опорного | Уровень |
|---|---|---|---|
| **RKE2** (Apache-2.0, 2 366★, v1.37.1+rke2r1) | дистрибутив Rancher с защитой по CIS из коробки, FIPS, SELinux; та же линия версий, что у k3s | CIS по умолчанию | Б |
| **k0s** (6 523★, v1.36.4+k0s.1) | один бинарник без зависимостей | — | Б |
| **Talos** (MPL-2.0, 11 336★, v1.14.2) | неизменяемая ОС для Kubernetes, без SSH, управление через API | защищённая ОС узла | Б |
| **MicroK8s** (Apache-2.0, 9 383★, v1.36) | snap-пакет, дополнения командой | — | Б |
| **kubeadm** | полный Kubernetes | — | Б |
| **Облачный Kubernetes** | кластер провайдера, HA | HA | Б |
| **Docker Compose** | без оркестратора | — | А |
| **agent-sandbox** (Apache-2.0, 4 218★, v1.0.6) | CRD [Sandbox](../architecture/components/sandbox/README.md), SandboxWarmPool, RuntimeClass | тёплый пул как объект K8s | Б |
| **Kueue** (Apache-2.0, 3 051★, v0.20.1) | квоты ресурсов, допуск Job, справедливая доля | ёмкость кластера | Б |
| **ArgoCD, Flux** (24 363★, 8 443★) | GitOps-доставка | — | Б |

**Вывод этапа.** Лёгкие дистрибутивы равны по функциям; RKE2 и Talos дают защиту узла. Поверх кластера на этапе 4 нужны провайдер сред (agent-sandbox или свой Pod) и, при нескольких узлах, планирование ёмкости (Kueue).

<span class="gate">G4</span> ✅ 10 кандидатов, включая «как есть»; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Кластер на одном узле | П1 | без лишнего железа | k3s, k0s, MicroK8s (Б) | базовая |
| NetworkPolicy, ServiceAccount | П2, П3 | изоляция агентов | все дистрибутивы (Б) | базовая |
| Своё железо | П5 | [AD-18](../architecture/decisions/AD-18.yaml) | (А) | базовая |
| Низкий порог эксплуатации | П6 | одна команда | k3s (Б) | базовая |
| CIS-защита узла | П2 | меньше поверхность атаки | RKE2 (Б); руководство CIS для k3s (Б) | линейная |
| Неизменяемая ОС без SSH | П2 | ещё меньше поверхность | Talos (Б) | привлекательная |
| Провайдер сред в K8s | П8 | этап 4 работает | agent-sandbox (Б); [I23](../architecture/components/agent-runner/integrations/I23.yaml) (А) | базовая для этапа 4 |
| Ёмкость по квотам | — | несколько узлов | Kueue (Б) | безразличная на одном узле |
| GitOps | — | доставка из git | ArgoCD, Flux (Б) | привлекательная, бэклог |

**Вывод этапа.** Базовые функции у лёгких дистрибутивов одинаковы. CIS-защита — линейная функция, её можно применить к k3s. Провайдер сред — базовый для этапа 4, и его в задачах не было.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| k3s, Helm, k3d, namespaces, NetworkPolicy, SA | оставить | [AD-15](../architecture/decisions/AD-15.yaml), [AD-16](../architecture/decisions/AD-16.yaml) | задача 4.6 |
| CIS-защита | адаптировать | проверка узла k3s по CIS (kube-bench), исправления по руководству k3s | подзадача 4.6.9; [FR-159](../architecture/components/infrastructure/prd.md) |
| Провайдер сред в K8s | брать | Runner создаёт Pod или [`SandboxClaim`](../architecture/data/model-SandboxClaim.yaml) (agent-sandbox) через [I23](../architecture/components/agent-runner/integrations/I23.yaml); RuntimeClass после 2.2.8 | подзадача 4.6.8 |
| Kueue | не брать сейчас | один узел, ёмкость держат слоты Runner | [R&D Runner](runner-and-scheduling.md) |
| Talos, облако, HA | не брать | Э5 | — |
| GitOps | не брать сейчас | бэклог | [BACKLOG](..\source\BACKLOG.md) |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** один узел | П1 → базовая | официально поддерживается |
| **M2** изоляция: NetworkPolicy, SA | П2, П3 → базовая | есть |
| **M3** своё железо | П5 → базовая | без облака |
| **К1** порог эксплуатации | П6 | компоненты, ОС |
| **К2** защита узла | П2 | CIS |
| **К3** локальная среда | П7 | k3d или аналог |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 один узел | M2 изоляция | M3 своё железо | Итог |
|---|---|---|---|---|
| k3s | да | да | да | проходит |
| RKE2 | да | да | да | проходит |
| k0s | да | да | да | проходит |
| MicroK8s | да | да | да | проходит |
| Talos | да | да | да: своя ОС | проходит |
| kubeadm | частично | да | да | проходит |
| Облачный Kubernetes | **нет** | да | **нет** | ✗ |
| Docker Compose (этап 4) | да | **нет** | да | ✗ (этапы 1–2) |

### Как встаёт в схему

```
 узел (k3s, CIS-проверка*) ┬ itsaplan-core: web, api ICPlan, MCP      ◀──I21── Traefik ◀── пользователи
                           ├ itsaplan-data: Postgres (CNPG), RustFS
                           ├ itsaplan-platform: Runner, OPA, Memory, LiteLLM, Squid
                           └ itsaplan-agents: среды запусков (Pod / Sandbox*) ◀──I23── Runner (SA только на этот namespace)
  * — подзадачи 4.6.8 (провайдер сред) и 4.6.9 (CIS-проверка)
```

| Стык | k3s | RKE2 | Talos |
|---|---|---|---|
| [I21](../architecture/integrations/I21.yaml) Traefik | И2: в комплекте | И1: свой ingress-nginx, Traefik ставится | И1 |
| [I23](../architecture/components/agent-runner/integrations/I23.yaml) Runner → K8s API | И1: провайдер не написан → 4.6.8 | И1 | И1 |
| Узел и ОС | И2: обычная ОС | И2 | И0: отдельная ОС на сервере |

**Изменения у соседей:** выбор дистрибутива меняет только техспеку инфраструктуры. Провайдер сред меняет Runner (код провайдера) и спеку [Sandbox](../architecture/components/sandbox/README.md) — параметр `provider` уже описан.

**Вывод этапа.** ==Сам кластер встаёт без изменений; пропущенным оказался стык [I23](../architecture/components/agent-runner/integrations/I23.yaml) — создание сред в K8s.==

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — «Безопасность» за RKE2, «адвокат дьявола» атакует один узел.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| DevOps 🤖 | k3s | один бинарник, Traefik в комплекте | — | — |
| Владелец продукта 🤖 | k3s | сроки этапа 4 | — | — |
| Архитектор 🤖 | k3s | всё нужное агентам есть | пропущен провайдер сред | подзадача 4.6.8 |
| Разработчик 🤖 | нейтрально | k3d локально = прод | — | — |
| Безопасность 🤖 (оппонент) | RKE2 | CIS из коробки | узел без защиты | CIS-проверка k3s в 4.6.9 |

| Спор | Разрешение |
|---|---|
| Безопасность: «k3s без CIS» | ✅ **внесено:** подзадача 4.6.9 — kube-bench и исправления; **условие:** требование CIS-аудита → RKE2 |
| Архитектор: «нет провайдера сред» | ✅ **внесено:** подзадача 4.6.8 |
| Адвокат дьявола: «один узел — единая точка отказа» | **условие:** HA после этапа 4; бэкапы вне узла ([AD-18](../architecture/decisions/AD-18.yaml)) |

**Вывод этапа.** Спор о защите сведён к проверке CIS без смены дистрибутива. Встраивание выявило пропущенную подзадачу.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | k3s | RKE2 | k0s | Talos | kubeadm | Compose |
|---|---|---|---|---|---|---|
| П1 один узел | закрывает | закрывает | закрывает | закрывает | частично | закрывает |
| П2 изоляция | закрывает | закрывает | закрывает | закрывает | закрывает | не закрывает |
| П3 SA на namespace | закрывает | закрывает | закрывает | закрывает | закрывает | не закрывает |
| П4 секреты вне git | закрывает | закрывает | закрывает | закрывает | закрывает | частично |
| П5 своё железо | закрывает | закрывает | закрывает | закрывает | закрывает | закрывает |
| П6 одна команда | закрывает | частично | закрывает | частично: своя ОС | частично | закрывает |
| П7 локально как прод | закрывает: k3d | частично | закрывает | частично | частично | не закрывает |
| П8 провайдер сред | с доработкой: 4.6.8 | с доработкой | с доработкой | не закрывает до своей ОС | с доработкой | не закрывает |

- **Утверждение.** k3s + Helm на одном узле, k3d локально ([AD-15](../architecture/decisions/AD-15.yaml), [AD-16](../architecture/decisions/AD-16.yaml)); CIS-проверка узла; провайдер сред — 4.6.8.
- **Основания.** k3s закрывает 7 из 8 потребностей, П8 — с доработкой, как и у всех.
- **Связка.** Базовые функции у лёгких дистрибутивов равны, а решает порог эксплуатации; защиту узла добираем проверкой.
- **Опровержение.** Вывод неверен, если понадобится CIS-аудит или второй узел. Тогда — RKE2: та же модель, что у k3s.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Провайдер сред в K8s: Pod или agent-sandbox ([`SandboxClaim`](../architecture/data/model-SandboxClaim.yaml)), RuntimeClass после 2.2.8 | [задача 4.6](..\source\tasks\4.6-k8s-helm-ingress.md) (подзадача 4.6.8) | ✅ внесено |
| CIS-проверка узла k3s (kube-bench) | задача 4.6 (подзадача 4.6.9) | ✅ внесено |
| RKE2, Talos, Kueue — Assess | [TECHNOLOGIES](..\source\TECHNOLOGIES.md) | ✅ внесено |
| CIS-профиль узла как требование | [FR-159](../architecture/components/infrastructure/prd.md) | ✅ внесено: сценарий «Защита узла» |
| Решения [AD-15](../architecture/decisions/AD-15.yaml), [AD-16](../architecture/decisions/AD-16.yaml), [AD-18](../architecture/decisions/AD-18.yaml) | design | ✅ подтверждено, без изменений |
| Стыки [I21](../architecture/integrations/I21.yaml), [I23](../architecture/components/agent-runner/integrations/I23.yaml) | спека platform-infrastructure | — не требуется |
| Техспека инфраструктуры | [техспека](..\architecture\components\infrastructure\docs\techspec.md) | — не требуется до 4.6.8 |
| Поток инфраструктуры | [поток](..\architecture\components\infrastructure\docs\how.md) | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| k3s | Apache-2.0 | 34 168 | v1.37.1+k3s1 | 10.10.2026 |
| Helm | Apache-2.0 | 30 308 | v4.3.0 | 06.10.2026 |
| ArgoCD | Apache-2.0 | 24 363 | v3.5.4 | 11.10.2026 |
| Talos | MPL-2.0 | 11 336 | v1.14.2 | 11.10.2026 |
| MicroK8s | Apache-2.0 | 9 383 | v1.36 | 10.10.2026 |
| Flux | Apache-2.0 | 8 443 | v2.9.6 | 09.10.2026 |
| k3d | MIT | 6 589 | v5.9.0 | 11.10.2026 |
| k0s | не определена API | 6 523 | v1.36.4+k0s.1 | 10.10.2026 |
| agent-sandbox | Apache-2.0 | 4 218 | v1.0.6 | 09.10.2026 |
| Kueue | Apache-2.0 | 3 051 | v0.20.1 | 09.10.2026 |
| RKE2 | Apache-2.0 | 2 366 | v1.37.1+rke2r1 | 10.10.2026 |
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- [k3s](https://github.com/k3s-io/k3s) (Б) · [RKE2](https://github.com/rancher/rke2) (Б) · [k0s](https://github.com/k0sproject/k0s) (Б) · [Talos](https://github.com/siderolabs/talos) (Б) · [MicroK8s](https://github.com/canonical/microk8s) (Б)
- [Helm](https://github.com/helm/helm) (Б) · [k3d](https://github.com/k3d-io/k3d) (Б) · [ArgoCD](https://github.com/argoproj/argo-cd) (Б) · [Flux](https://github.com/fluxcd/flux2) (Б)
- [agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) (Б) · [Kueue](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue) (Б)
- Наши: [AD-15, AD-16, AD-18](..\source\design\define-agent-platform\design.md) (А); проект AI-агент: решения 7.11–7.14 (А)
