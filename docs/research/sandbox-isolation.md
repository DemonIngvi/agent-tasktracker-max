# R&D: Изоляция запусков (Sandbox)

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Sandbox](../architecture/components/sandbox/README.md)** · решение: [design AD-18](..\source\design\define-agent-platform\design.md) · спека: agent-sandbox

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
В какой среде исполняется агент, который запускает код и ходит в сеть: как отделить запуски друг от друга и от хоста, не потеряв быстрый старт и простую эксплуатацию на своём сервере?

<div class="rnd-a">Ответ: одноразовый контейнер на каждый запуск плюс тёплый пул, на rootless Docker. Изоляцию ядра усиливаем gVisor (runsc), если он пройдёт проверку в задаче 2.2. MicroVM — позже, при недоверенном внешнем коде.</div>

<span class="rnd-badge adopt">Adopt</span> Docker rootless + runc · <span class="rnd-badge assess">Assess</span> gVisor, Firecracker, agent-sandbox (K8s) · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П9
> контейнер с пулом закрывает всё, кроме сильной границы ядра; gVisor её усиливает без KVM
stack Контейнер + пул (runc): 8 ok, 1 part, 0 no
stack Контейнер + пул + gVisor: 8 ok, 1 part, 0 no
stack Kata Containers: 6 ok, 2 part, 1 no
stack Firecracker: 5 ok, 2 part, 2 no
stack E2B self-host: 5 ok, 1 part, 3 no
stack Контейнер на задачу: 6 ok, 1 part, 2 no
# Объём доработки
> выбранный вариант «контейнер + пул» — задачи 2.2, 4.1, 4.2, 108 ч по подзадачам; у остальных кандидатов оценок задач нет
bar 2.2 одноразовый контейнер, профили, проверка gVisor: 35/108 ч, 8 подзадач ok
bar 4.1 тёплый пул: 25/108 ч, 5 подзадач ok
bar 4.2 egress-прокси, токены и доступ к репозиториям: 48/108 ч, 7 подзадач ok
# Сила границы и цена
> чем сильнее граница, тем больше требований к железу
bar runc: 1/4 ядро общее; namespaces, cgroups part
bar gVisor: 2/4 своё ядро в user space, без KVM info
bar Kata: 3/4 VM на под, нужен KVM info
bar Firecracker: 4/4 microVM, нужен KVM и своя обвязка ok
# Позиции ролей
side Контейнер + пул | microVM
pos DevOps: -2 | KVM на сервере не подтверждён
pos Разработчик: -1 | совместимость git, Python, тестов
pos Архитектор: -1 | провайдер за `SandboxProvider`
pos Владелец продукта: -1 | сроки этапов 2 и 4
pos Безопасность: 1 | агент запускает чужой код
# Что меняется
> AD-18 подтверждён; в задачу 2.2 добавлена проверка gVisor
stack Документы: 6 ok, 0 part, 2 mute
- ✅ задача 2.2: проверка gVisor · ✅ TECHNOLOGIES: gVisor, Daytona архивирован, версия Squid
- ✅ параметр `runtime` профиля: по умолчанию runc, runsc — после проверки 2.2.8
```

**Почему одноразовый контейнер с пулом.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Одноразовость важнее силы границы**

Главный риск — утечка между запусками: файлы, токены, процессы предыдущего агента. Одноразовая среда на каждый запуск закрывает его при любой технологии изоляции. Контейнер на задачу или на агента — нет ([Э9](#e9)).
</div>
<div markdown>
**2. gVisor усиливает границу без нового железа**

У контейнера на runc ядро общее с хостом. gVisor (runsc) перехватывает системные вызовы своим ядром в user space и работает как runtime Docker — без KVM. Kata и Firecracker сильнее, но им нужна аппаратная виртуализация, а на нашем сервере она не подтверждена ([Э7](#e7)).
</div>
<div markdown>
**3. Провайдер заменяем, этап 4 уже виден**

Среда создаётся через интерфейс `SandboxProvider` ([I6](../architecture/components/agent-runner/integrations/I6.yaml) / [I23](../architecture/components/agent-runner/integrations/I23.yaml)). На этапе 4 им может стать kubernetes-sigs/agent-sandbox: тёплый пул как объект K8s и runtime gVisor или Kata через RuntimeClass. Тогда свой код пула не нужен ([Э6](#e6)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- одноразовый контейнер на запуск;
- тёплый пул (`pool.size` 2);
- rootless Docker ([AD-18](../architecture/decisions/AD-18.yaml));
- сеть только через egress-прокси Squid;
- профиль ресурсов.
</div>
<div class="adapt" markdown>
**Адаптируем**

- runtime gVisor (runsc) → параметр профиля после проверки;
- `SandboxWarmPool` (agent-sandbox) → провайдер этапа 4 вместо своего пула;
- снимки и быстрый старт microVM (E2B, Firecracker) → Assess, для внешнего недоверенного кода.
</div>
<div class="drop" markdown>
**Не берём**

- контейнер на задачу или на агента: утечка между запусками;
- облачные песочницы (E2B cloud, Modal): код и данные уходят наружу;
- Daytona: репозиторий архивирован 24.07.2026;
- self-host E2B: тяжёлая инфраструктура под облако.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **Облачные песочницы** — исполнение вне нашего сервера.
- **Daytona** — архивирован.
- **Контейнер на агента** — общий контейнер между задачами.
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Побег из контейнера через ядро — gVisor (проверка в 2.2), rootless, без привилегий.
- Пересмотр: агенты запускают код из внешних источников → microVM (Kata, Firecracker), если KVM есть.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**9 <span class="gate">G2</span></div>
<div markdown>**Э3 Docker**7 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**10 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I6](../architecture/components/agent-runner/integrations/I6.yaml), [I7](../architecture/components/agent-runner/integrations/I7.yaml), [I17](../architecture/components/sandbox/integrations/I17.yaml), [I23](../architecture/components/agent-runner/integrations/I23.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**6 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**8 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** Агент в запуске выполняет код (git, тесты, скрипты) и обращается к сети. Runner создаёт среду через Docker (этапы 1–3) или Kubernetes (этап 4).

**Осложнение.** Сильная изоляция (microVM) требует KVM и своей обвязки. Простой контейнер делит ядро с хостом. Долгоживущий контейнер стартует быстро, но копит следы запусков.

**Вопрос.** Какая среда и какой жизненный цикл у среды запуска?

**Решает:** владелец продукта с ролью «Безопасность». **Не решаем:** egress-прокси ([AD-18](../architecture/decisions/AD-18.yaml): Squid), доступ к репозиториям ([рабочее пространство](agent-workspace.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-18](../architecture/decisions/AD-18.yaml) и требованиями agent-sandbox.

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | своя среда на каждый запуск, без следов предыдущих | [FR-82](../architecture/components/sandbox/prd.md), [FR-84](../architecture/components/sandbox/prd.md) | файлы и токены одного запуска видны другому |
| П2 | старт < 1 с | [FR-83](../architecture/components/sandbox/prd.md) | пользователь ждёт секунды на каждый шаг процесса |
| П3 | граница с хостом для кода агента | [FR-82](../architecture/components/sandbox/prd.md), [AD-18](../architecture/decisions/AD-18.yaml) | побег из среды даёт доступ к узлу |
| П4 | сеть только через allowlist egress-прокси | [FR-87](../architecture/components/sandbox/prd.md), [I17](../architecture/components/sandbox/integrations/I17.yaml) | агент выносит данные или скачивает лишнее |
| П5 | секретов в среде нет | [FR-88](../architecture/components/sandbox/prd.md) | ключи утекают в логи и ответы модели |
| П6 | профиль ресурсов | [FR-86](../architecture/components/sandbox/prd.md) | один запуск съедает узел |
| П7 | рабочее пространство по манифесту | [FR-89](../architecture/components/sandbox/prd.md), [FR-85](../architecture/components/sandbox/prd.md) | агент без кода и файлов задачи |
| П8 | свой сервер: этапы 1–3 на Docker, этап 4 на Kubernetes | [AD-15](../architecture/decisions/AD-15.yaml), `provider` | привязка к облаку или к одному оркестратору |
| П9 | эксплуатация силами одной команды | [AD-15](../architecture/decisions/AD-15.yaml) | отдельная экспертиза под гипервизор |

<span class="gate">G2</span> ✅ у потребностей есть требования и решения.

## Э3. Опорное решение: rootless Docker и одноразовый контейнер {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Namespaces и cgroups | отдельные процессы, сеть, файлы; лимиты CPU и памяти | П1, П6 |
| F2 | Rootless-демон | демон без root; Runner под отдельным пользователем ([AD-18](../architecture/decisions/AD-18.yaml)) | П3 |
| F3 | Контейнер на запуск | создаётся на запуск, удаляется с диском `/workspace` | П1 |
| F4 | Тёплый пул | заранее созданные контейнеры, каждый — на один запуск | П2 |
| F5 | Сети Docker | доступ только к egress-прокси и сервисам платформы | П4 |
| F6 | Runtime через параметр (`--runtime`) | можно подключить другой OCI runtime (runsc, kata) | П3 |
| F7 | Тома и копирование | папка задачи в `/workspace/task` | П7 |

**Вывод этапа.** Docker закрывает одноразовость, пул, сеть и ресурсы. Слабое место — общее ядро (П3), его закрывает другой runtime через F6.

<span class="gate">G3</span> ✅ функции из документации Docker (Б) и [AD-18](../architecture/decisions/AD-18.yaml) (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub (sandbox, microvm, agent sandbox), CNCF Landscape, документация E2B, Kubernetes SIG. Жизненный цикл (на запуск / на задачу / на агента) рассмотрен вместе с технологией.

| Кандидат | Ключевые функции | Чего нет у опорного | Уровень |
|---|---|---|---|
| **gVisor** (Apache-2.0, 19 632★, release-20261005.0) | своё ядро в user space перехватывает системные вызовы; OCI runtime `runsc` для Docker и K8s; без KVM | своя граница ядра | Б |
| **Kata Containers** (Apache-2.0, 8 916★, 4.2.0) | лёгкая VM на под; OCI runtime; RuntimeClass в K8s; нужен KVM | граница VM | Б |
| **Firecracker** (Apache-2.0, 37 283★, v1.17.0) | microVM, старт ~125 мс, основа Lambda; нужен KVM и своя обвязка | граница VM, снимки | Б |
| **kubernetes-sigs/agent-sandbox** (Apache-2.0, 4 218★, v1.0.6) | CRD [Sandbox](../architecture/components/sandbox/README.md), SandboxTemplate, [SandboxClaim](../architecture/data/model-SandboxClaim.yaml), SandboxWarmPool; изоляция через RuntimeClass (gVisor, Kata); пауза и продолжение; API v1beta1 | пул как объект K8s | Б |
| **E2B** (Apache-2.0; runtime 1 708★) | песочницы для агентов на Firecracker, снимки; self-host — своя инфраструктура под облако | снимки | Б / В |
| **Sysbox** (Apache-2.0, 3 902★, v0.7.1) | контейнеры с вложенным Docker без привилегий | Docker внутри среды | Б |
| **Daytona** (71 572★) | песочницы для агентов; **репозиторий архивирован 24.07.2026**, лицензия API не определена | — | Б |
| **Облачные песочницы** (E2B cloud, Modal) | готовый сервис | — | Б |
| **Контейнер на задачу** (как Codex cloud, Copilot coding agent) | один контейнер на все шаги задачи | файлы между шагами | В |
| **Контейнер на агента** | долгоживущий контейнер | — | — |

**Вывод этапа.** Граница ядра усиливается тремя путями: gVisor без KVM, Kata и Firecracker с KVM. agent-sandbox решает тёплый пул для этапа 4. Daytona выбывает — проект архивирован.

<span class="gate">G4</span> ✅ 10 кандидатов, включая «как есть» и варианты жизненного цикла; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Одноразовая среда на запуск | П1 | следы запуска не переживают его | [FR-82](../architecture/components/sandbox/prd.md) (А); так делают E2B, Firecracker-песочницы (Б) | базовая |
| Тёплый пул | П2 | старт < 1 с без снимков VM | пулы у E2B, Modal, agent-sandbox (Б) | базовая |
| Своё размещение | П8 | код и данные не уходят наружу | ограничение проекта (А) | базовая |
| Граница ядра в user space (gVisor) | П3 | побег через уязвимость ядра хоста труднее | gVisor docs (Б); используется в Google Cloud [Run](../architecture/data/model-Run.yaml), GKE [Sandbox](../architecture/components/sandbox/README.md) (Б) | линейная |
| Граница VM (Kata, Firecracker) | П3 | самая сильная изоляция | Lambda, Fargate на Firecracker (Б) | линейная, требует KVM |
| Пул как объект K8s | П2, П8 | на этапе 4 не нужен свой код пула | agent-sandbox (Б) | привлекательная |
| Снимки microVM | П2 | старт с готовым состоянием | E2B, Firecracker (Б) | привлекательная |
| Вложенный Docker (Sysbox) | — | агент собирает образы | у нас нет такой истории | безразличная |
| Общий контейнер на задачу или агента | П1 | — | утечка между запусками | обратная |

**Вывод этапа.** Базовые функции — одноразовая среда, тёплый пул, своё размещение. Сила границы — линейная: чем сильнее, тем лучше, но цена — требования к железу.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше.

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| Одноразовый контейнер, пул, rootless | брать | как в [AD-18](../architecture/decisions/AD-18.yaml) | задачи 2.2, 4.1 |
| gVisor | адаптировать | проверка в 2.2: образ [Harness](../architecture/components/harness/README.md) под runsc — git, Python, тесты, сеть через Squid, время старта; при успехе — параметр профиля `runtime` | задача 2.2 (подзадача 2.2.8); [FR-86](../architecture/components/sandbox/prd.md) |
| Пул как объект K8s (agent-sandbox) | адаптировать | провайдер этапа 4 | [R&D Kubernetes](kubernetes-runtime.md) |
| Kata, Firecracker, снимки | не брать сейчас | Assess: нужен KVM; вернуться при внешнем недоверенном коде | TECHNOLOGIES |
| Вложенный Docker | не брать | нет истории | — |
| Контейнер на задачу или агента | не брать | П1 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** своё размещение | П8 → базовая | работает на нашем сервере |
| **M2** одноразовая среда на запуск | П1 → базовая | среда не переживает запуск |
| **M3** проект жив | П9 | не архивирован, есть релизы |
| **К1** сила границы | П3 | общее ядро / своё ядро / VM |
| **К2** старт | П2 | с пулом, без пула |
| **К3** требования к железу и эксплуатация | П8, П9 | KVM, новые службы |
| **К4** совместимость с образом [Harness](../architecture/components/harness/README.md) | П7 | git, Python, тесты, сеть через прокси |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 у нас | M2 на запуск | M3 жив | Итог |
|---|---|---|---|---|
| Контейнер + пул (runc) | да | да | да | проходит |
| Контейнер + пул + gVisor | да | да | да | проходит |
| Kata Containers | да | да | да | проходит |
| Firecracker | да | да | да | проходит |
| agent-sandbox (этап 4) | да | да | да | проходит |
| E2B self-host | да | да | да | проходит |
| Контейнер на задачу | да | **нет** | да | ✗ |
| Контейнер на агента | да | **нет** | да | ✗ |
| Daytona | да | да | **нет**: архивирован | ✗ |
| Облачные песочницы | **нет** | да | да | ✗ |

### Как встаёт в схему

```
 Agent Runner ──I6 Docker API (rootless)──▶ контейнер запуска  [runtime: runc | runsc*]
      │         (этап 4: I23 K8s API → Pod / Sandbox* с RuntimeClass)
      └──I7──▶ Harness в контейнере ──I17──▶ Squid (allowlist) ──▶ LiteLLM, MCP, git
                       │ /workspace (S10) — удаляется с контейнером
  * — runtime gVisor после проверки в 2.2; agent-sandbox — кандидат провайдера этапа 4
```

| Стык | runc | gVisor | Kata | Firecracker | agent-sandbox | E2B self-host |
|---|---|---|---|---|---|---|
| [I6](../architecture/components/agent-runner/integrations/I6.yaml) / [I23](../architecture/components/agent-runner/integrations/I23.yaml) создание среды | И2 | И2: `--runtime=runsc` | И1: RuntimeClass, KVM | И1: своя обвязка | И1: CRD, только K8s | И1: свой API |
| [I7](../architecture/components/agent-runner/integrations/I7.yaml) Runner ↔ [Harness](../architecture/components/harness/README.md) | И2 | И2 | И2 | И1: сеть VM | И2 | И1 |
| [I17](../architecture/components/sandbox/integrations/I17.yaml) egress через Squid | И2 | И1: сетевой стек gVisor с прокси — проверить | И2 | И1 | И2 | И1 |
| S10 `/workspace` | И2 | И2 | И2 | И1: диск VM | И2 | И1 |

**Изменения у соседей:**

| Кандидат | Что меняется |
|---|---|
| runc | ничего |
| gVisor | установка runsc на узле (техспека [Sandbox](../architecture/components/sandbox/README.md), инфраструктура); параметр `runtime` в профиле (спека [Sandbox](../architecture/components/sandbox/README.md), [Platform module](../architecture/components/platform-module/README.md)) |
| Kata, Firecracker | KVM на сервере (инфраструктура); для Firecracker — свой провайдер, сеть и диски VM |
| agent-sandbox | этап 4: CRD в кластере; Runner создаёт [`SandboxClaim`](../architecture/data/model-SandboxClaim.yaml) вместо Pod |
| E2B self-host | отдельная инфраструктура песочниц, новый I-код |

**Вывод этапа.** ==gVisor — единственный способ усилить границу без нового железа и без смены провайдера; меняется только параметр профиля и установка runsc.== Стык с Squid под gVisor надо проверить.

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — «Безопасность» за microVM, «адвокат дьявола» атакует контейнер.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| DevOps 🤖 | контейнер + пул | Docker уже в стеке; KVM на сервере не подтверждён | runsc — ещё один компонент узла | установка runsc описана в техспеке |
| Разработчик 🤖 | контейнер + пул | образ [Harness](../architecture/components/harness/README.md) проверен на runc | совместимость под gVisor | проверка 2.2.8 |
| Архитектор 🤖 | контейнер + пул | провайдер за `SandboxProvider`, смена без переделки Runner | — | — |
| Владелец продукта 🤖 | контейнер + пул | сроки этапов 2 и 4 | — | — |
| Тестировщик 🤖 | нейтрально | тесты изоляции одинаковы для всех | — | тест «два запуска не видят файлы» на каждом runtime |
| Безопасность 🤖 (оппонент) | microVM | агент запускает код, который пишет модель; ядро общее | побег через уязвимость ядра | gVisor на этапе 2, microVM — при внешнем коде |

| Спор | Разрешение |
|---|---|
| Безопасность: «общее ядро — недопустимо» | ✅ **внесено:** проверка gVisor в 2.2.8; параметр `runtime` в профиле |
| Адвокат дьявола: «пул держит ресурсы впустую» | **условие:** `pool.size` 2 при `global_max` 4; 0 — без пула (параметр уже есть) |
| DevOps: «а если runsc сломает сеть через Squid?» | **условие:** проверка [I17](../architecture/components/sandbox/integrations/I17.yaml) в 2.2.8; при провале — runc + seccomp-профиль по умолчанию |

**Вывод этапа.** Спор «контейнер против microVM» разрешён промежуточным шагом — gVisor, без смены железа. Решение по нему — после проверки.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | runc + пул | gVisor + пул | Kata | Firecracker | E2B self-host |
|---|---|---|---|---|---|
| П1 одноразовая среда | закрывает | закрывает | закрывает | закрывает | закрывает |
| П2 старт < 1 с | закрывает: пул | закрывает: пул | частично: старт VM | закрывает: снимки | закрывает |
| П3 граница с хостом | частично: общее ядро | закрывает: своё ядро | закрывает: VM | закрывает: VM | закрывает |
| П4 сеть через Squid | закрывает | с доработкой: проверить | закрывает | с доработкой | не закрывает: своя сеть |
| П5 без секретов | закрывает | закрывает | закрывает | закрывает | закрывает |
| П6 профиль ресурсов | закрывает | закрывает | закрывает | закрывает | закрывает |
| П7 рабочее пространство | закрывает | закрывает | закрывает | с доработкой: диски VM | частично |
| П8 Docker → K8s | закрывает | закрывает | частично: KVM | не закрывает: своя обвязка | не закрывает |
| П9 одна команда | закрывает | закрывает | частично | не закрывает | не закрывает |

- **Утверждение.** Одноразовый контейнер на запуск с тёплым пулом на rootless Docker ([AD-18](../architecture/decisions/AD-18.yaml)). gVisor — Assess до проверки в 2.2.
- **Основания.** Одноразовость закрывает главный риск — утечку между запусками. Пул даёт старт < 1 с. gVisor усиливает границу ядра без KVM и без смены провайдера.
- **Связка.** Сильнее граница — больше требований к железу и эксплуатации. На этапах 1–3 агент работает с кодом своей команды, поэтому шаг «runc → gVisor» соразмерен риску.
- **Опровержение.** Вывод неверен:
  - если агенты начнут запускать код из внешних источников — тогда нужна microVM (Kata при наличии KVM);
  - если проверка gVisor провалится по совместимости — тогда остаётся runc с seccomp.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Проверка gVisor: образ [Harness](../architecture/components/harness/README.md) под runsc, сеть через Squid, время старта | [задача 2.2](..\source\tasks\2.2-sandbox-docker-oneshot.md) (подзадача 2.2.8) | ✅ внесено |
| gVisor — Assess; Daytona архивирован (не используем) | [TECHNOLOGIES](..\source\TECHNOLOGIES.md) | ✅ внесено |
| Версия Squid: TECHNOLOGIES 7.7 против образа `ubuntu/squid:6` в техспеке | TECHNOLOGIES, [техспека Sandbox](..\architecture\components\sandbox\docs\techspec.md) | ✅ внесено: в TECHNOLOGIES — образ `ubuntu/squid` 6.x (upstream 7.7) |
| Параметр профиля `runtime`: runc / runsc | [interfaces agent-sandbox](..\architecture\components\sandbox\docs\agent-sandbox-interfaces.md), [FR-86](../architecture/components/sandbox/prd.md) | ✅ внесено: по умолчанию runc; значение по умолчанию пересматривается после 2.2.8 |
| agent-sandbox (пул как объект K8s) — провайдер этапа 4 | [R&D Kubernetes](kubernetes-runtime.md) | ✅ учтено при переводе R&D Kubernetes |
| Решение [AD-18](../architecture/decisions/AD-18.yaml) (rootless Docker, Squid) | design | ✅ подтверждено, без изменений |
| Стыки [I6](../architecture/components/agent-runner/integrations/I6.yaml), [I7](../architecture/components/agent-runner/integrations/I7.yaml), [I17](../architecture/components/sandbox/integrations/I17.yaml), [I23](../architecture/components/agent-runner/integrations/I23.yaml) | спека agent-sandbox, [поток Sandbox](..\architecture\components\sandbox\docs\how.md) | — не требуется |
| Тёплый пул | [задача 4.1](..\source\tasks\4.1-sandbox-warm-pool.md) | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов и ориентиры</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| Firecracker | Apache-2.0 | 37 283 | v1.17.0 | 09.10.2026 |
| gVisor | Apache-2.0 | 19 632 | release-20261005.0 | 10.10.2026 |
| Kata Containers | Apache-2.0 | 8 916 | 4.2.0 | 11.10.2026 |
| agent-sandbox | Apache-2.0 | 4 218 | v1.0.6 | 09.10.2026 |
| Sysbox | Apache-2.0 | 3 902 | v0.7.1 | 15.09.2026 |
| E2B runtime | Apache-2.0 | 1 708 | 2026.30 | 11.10.2026 |
| Daytona | не определена | 71 572 | v0.190.0 | **архивирован**, 24.07.2026 |

Ориентиры: [Harness](../architecture/components/harness/README.md) 150–300 МБ, агент-разработчик 0,5–2 ГБ; 80–95% времени — ожидание LLM. Старт: контейнер Docker 0,5–2 с, под 2–10 с, microVM 0,1–0,3 с (Firecracker ~125 мс).
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- [gVisor](https://github.com/google/gvisor) (Б) · [Kata Containers](https://github.com/kata-containers/kata-containers) (Б) · [Firecracker](https://github.com/firecracker-microvm/firecracker) (Б)
- [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) (Б)
- [E2B](https://github.com/e2b-dev/E2B) (Б) · [Sysbox](https://github.com/nestybox/sysbox) (Б) · [Daytona — архивирован](https://github.com/daytonaio/daytona) (Б)
- Решение [AD-18: rootless Docker, Squid](..\source\design\define-agent-platform\design.md) (А) · [техспека Sandbox](..\architecture\components\sandbox\docs\techspec.md) (А)
