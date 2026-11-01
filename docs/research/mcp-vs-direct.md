# R&D: Тулы агента — MCP, прямые вызовы, нативные тулы

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[MCP / Tools](../architecture/components/mcp-tools/README.md)** · решение: [design AD-2, AD-7](..\source\design\define-agent-platform\design.md) · спека: tool-integration · потоки: [MCP / Tools](..\architecture\components\mcp-tools\docs\how.md)

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Как агент получает тулы: что подключать через MCP, что вызывать напрямую, что делать нативным тулом — так, чтобы система подключалась без кода, описания тулов не съедали контекст, а агент не мог выйти за свой список?

<div class="rnd-a">Ответ: гибрид по правилам [FR-179](../architecture/components/mcp-tools/prd.md) остаётся. Встраивание вскрыло дыру — allowlist и G2 проверялись внутри недоверенного sandbox. Её закрывает решение [AD-19](../architecture/decisions/AD-19.yaml): MCP-прокси в [Agent Runner](../architecture/components/agent-runner/README.md), без нового сервиса.</div>

<span class="rnd-badge adopt">Adopt</span> гибрид [FR-179](../architecture/components/mcp-tools/prd.md) · <span class="rnd-badge adopt">Adopt</span> MCP-прокси Runner ([AD-19](../architecture/decisions/AD-19.yaml)) · <span class="rnd-badge assess">Assess</span> ContextForge, agentgateway, поиск тулов · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П8
> проверку вне sandbox закрывают шлюз и прокси Runner; прокси — без нового сервиса
stack Гибрид + прокси Runner (AD-19): 7 ok, 1 part, 0 no
stack Гибрид + MCP-шлюз: 7 ok, 1 part, 0 no
stack Гибрид (как сейчас): 6 ok, 1 part, 1 no
stack Всё через MCP: 4 ok, 2 part, 2 no
stack Исполнение кода поверх MCP: 4 ok, 2 part, 2 no
stack Только нативные тулы: 3 ok, 1 part, 4 no
# Объём доработки
> выбранный вариант «гибрид + прокси Runner» — 58 ч по подзадачам; у остальных кандидатов оценок задач нет
bar 1.4 MCP-адаптер Harness, allowlist, таймауты, обрезка: 33/58 ч, 8 подзадач ok
bar 2.4 MCP itsaplan-core, ключ агента вне контекста: 11/58 ч, 4 подзадачи ok
bar 2.1.9 MCP-прокси Runner (AD-19): 8/58 ч, 1 подзадача ok
bar 4.2.5 MCP git-провайдера: 6/58 ч, 1 подзадача ok
# Где проверяется список тулов
> было — внутри sandbox, где исполняется код агента; стало — в Runner
bar Было: 0/2 allowlist и G2 вне sandbox no
bar Прокси Runner (AD-19): 2/2 allowlist и G2 вне sandbox ok
- код агента может вызвать MCP через прокси, который подставит ключ агента
# Позиции ролей
side Прокси Runner | Гибрид как есть
pos Безопасность: -2 | проверка внутри недоверенной среды — не проверка
pos Архитектор: -1 | один вход к MCP, секреты вне sandbox
pos Администратор: -1 | список тулов в одном месте
pos DevOps: -1 | нового сервиса нет
pos Владелец продукта: 0 | +8 ч в задаче 2.1
# Что меняется
> решение AD-19 внесено по всей цепочке; ленивые тулы и исполнение кода — в бэклог
stack Документы: 7 ok, 0 part, 3 mute
- ✅ AD-19: FR-177, FR-87, FR-88, FR-112, FR-79, I9, задачи 2.1.9, 4.2.7, 1.4.8
- ✅ бэклог: ленивые тулы и скиллы, исполнение кода поверх MCP
```

**Что показал разбор.** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Правила [FR-179](../architecture/components/mcp-tools/prd.md) подтверждены**

Внутренние вызовы платформы — напрямую, без лишнего прыжка. Действия, которые выбирает модель, — тулы. Тул для нескольких агентов или с секретом — MCP-сервер. Стабильный тул только для [Harness](../architecture/components/harness/README.md) — нативный. Аналоги делают так же: MCP — для внешних систем ([Э5](#e5)).
</div>
<div markdown>
**2. Список тулов проверяется не там**

Allowlist ([FR-177](../architecture/components/mcp-tools/prd.md)) и G2 ([FR-112](../architecture/components/guardrails/prd.md)) исполняются в [Harness](../architecture/components/harness/README.md) — внутри sandbox, где исполняется код агента. Egress-прокси подставляет ключ агента к разрешённым MCP-хостам. Поэтому `curl` из bash-тула может вызвать любой тул MCP-сервера в обход [Harness](../architecture/components/harness/README.md) ([Э7](#e7)).
</div>
<div markdown>
**3. Дыру закрывает прокси в Runner**

Шлюз вне sandbox (ContextForge, agentgateway) закрыл бы её ценой нового сервиса и настройки на каждый запуск. У Runner уже есть манифест запуска, токен, подтверждения и клиент OPA, а для Go есть официальный MCP SDK. Поэтому Runner стал MCP-прокси: фильтрует тулы, проверяет G2, подставляет учётные данные ([AD-19](../architecture/decisions/AD-19.yaml), [Э9](#e9)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- правила [FR-179](../architecture/components/mcp-tools/prd.md);
- MCP Streamable HTTP для внешних систем;
- allowlist и обрезку ответа (64 КБ);
- скиллы как пакет инструкций и тулов.
</div>
<div class="adapt" markdown>
**Адаптируем**

- виртуальный сервер из разрешённых тулов (ContextForge) → MCP-прокси Runner по манифесту запуска ([AD-19](../architecture/decisions/AD-19.yaml));
- поиск тулов и ленивая загрузка описаний → бэклог: при большом числе тулов;
- постепенное раскрытие скиллов (Agent Skills, SKILL.md) → бэклог: инструкции скилла по запросу.
</div>
<div class="drop" markdown>
**Не берём сейчас**

- исполнение кода поверх MCP: экономит до 98,7% токенов, но вызовы из кода обходят G2 на тул;
- «всё через MCP»: лишний прыжок для внутренних вызовов;
- UTCP: молодой протокол, MCP — стандарт у аналогов.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **Только нативные тулы** — подключение каждой системы кодом [Harness](../architecture/components/harness/README.md).
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Runner на пути каждого вызова MCP — таймаут 30 с, отказ сервера — ошибка тула (FMEA Runner).
- Пересмотр: число тулов агента > 30 — включить поиск тулов.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**8 <span class="gate">G2</span></div>
<div markdown>**Э3 Гибрид**6 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**9 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I9](../architecture/components/harness/integrations/I9.yaml), [I10](../architecture/components/harness/integrations/I10.yaml), [I17](../architecture/components/sandbox/integrations/I17.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**6 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**8 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** Агентам нужны тулы: [ICPlan](../architecture/components/icplan/README.md), git, память, внешние системы. MCP стал стандартом для тулов, которые выбирает модель.

**Осложнение.** Описания тулов MCP занимают контекст, вызов через модель медленнее прямого, а секреты MCP-серверов нельзя отдавать в sandbox. Плюс в 2025–2026 годах появились новые способы: исполнение кода поверх MCP, поиск тулов и MCP-шлюзы.

**Вопрос.** По каким правилам подключать тулы и где проверять, какие тулы агенту можно?

**Решает:** владелец продукта с ролью «Безопасность». **Не решаем:** движок правил ([guardrails](guardrails-engine.md)), изоляцию ([Sandbox](sandbox-isolation.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [FR-176](../architecture/components/mcp-tools/prd.md) – [FR-179](../architecture/components/mcp-tools/prd.md).

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | подключить систему без кода [Harness](../architecture/components/harness/README.md) | [FR-176](../architecture/components/mcp-tools/prd.md), [US-MCP-01](../architecture/components/mcp-tools/stories/us-mcp-01.yaml) | каждая система — релиз [Harness](../architecture/components/harness/README.md) |
| П2 | агент видит и вызывает только свои тулы | [FR-177](../architecture/components/mcp-tools/prd.md) | агент делает то, что ему не разрешено |
| П3 | внутренние вызовы без лишней задержки | [FR-179](../architecture/components/mcp-tools/prd.md) | прыжок через MCP на каждом шаге |
| П4 | секреты MCP-серверов не попадают в sandbox | [FR-88](../architecture/components/sandbox/prd.md), [AD-7](../architecture/decisions/AD-7.yaml) | ключи в контексте агента |
| П5 | проверка G2 на каждый вызов тула | [FR-112](../architecture/components/guardrails/prd.md) | действие без политики |
| П6 | описания тулов не съедают контекст | [FR-30](../architecture/components/harness/prd.md) | десятки тулов = тысячи токенов |
| П7 | таймауты и обрезка ответов | [FR-178](../architecture/components/mcp-tools/prd.md) | тул вешает запуск или заливает контекст |
| П8 | скиллы: инструкции и тулы пакетом | [FR-181](../architecture/components/mcp-tools/prd.md) | инструкции разносятся вручную |

<span class="gate">G2</span> ✅ у потребностей есть требования и решения.

## Э3. Опорное решение: гибрид по FR-179 {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Правила выбора типа интеграции | прямой вызов / тул / MCP-сервер / нативный тул | П1, П3 |
| F2 | MCP Streamable HTTP | внешние системы и [ICPlan](../architecture/components/icplan/README.md) (`itsaplan-core`) как MCP-серверы | П1 |
| F3 | Allowlist тулов в определении агента | [Harness](../architecture/components/harness/README.md) фильтрует `tools/list` и отклоняет вызов вне списка | П2 |
| F4 | Подстановка ключа egress-прокси | ключ агента добавляется к запросу к MCP-хосту, агент его не видит | П4 |
| F5 | G2 из [Harness](../architecture/components/harness/README.md) | OPA перед вызовом тула ([I10](../architecture/components/harness/integrations/I10.yaml)) | П5 |
| F6 | Таймаут 30 с, обрезка 64 КБ | защита запуска и контекста | П7 |

**Вывод этапа.** Опорное решение закрывает подключение, задержку и защиту контекста. П2 и П5 закрыты только при условии, что вызов идёт через [Harness](../architecture/components/harness/README.md).

<span class="gate">G3</span> ✅ функции из спеки и потоков (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: GitHub (mcp gateway, tool calling), блог Anthropic Engineering, обзоры «MCP context bloat 2026».

| Кандидат | Ключевые функции | Чего нет в опорном | Уровень |
|---|---|---|---|
| **MCP-шлюз ContextForge** (IBM, Apache-2.0, 4 597★, v1.0.11) | один вход к многим MCP и REST; **виртуальный сервер** из выбранных тулов со своим endpoint; JWT; REST → MCP-тулы; плагины | проверка списка вне sandbox, секреты в шлюзе | Б |
| **agentgateway** (Linux Foundation, Apache-2.0, 5 278★, v1.6.0) | шлюз для агентов и MCP; отдельный бинарник или Docker; правила доступа к тулам — не подтверждено в прочитанном | — | Б / В |
| **Docker MCP Gateway** (MIT, 1 591★) | MCP-серверы в контейнерах за одним шлюзом | — | Б |
| **Исполнение кода поверх MCP** (Anthropic, 04.11.2025) | тулы как файлы кода; агент загружает только нужные определения; пример: 150 тыс. → 2 тыс. токенов (−98,7%) | экономия контекста | Б |
| **Поиск тулов** (tool search, `defer_loading`) | описания тулов скрыты, модель ищет нужный | экономия контекста | В |
| **Agent Skills** (SKILL.md) | постепенное раскрытие: сначала краткое описание скилла, инструкции по запросу | ленивые скиллы | Б |
| **UTCP** | прямой вызов тула по его родному протоколу без MCP-сервера | — | В |
| **Всё через MCP** | любой тул — MCP-сервер, включая внутренние | — | А |
| **Только нативные тулы** | тулы — код [Harness](../architecture/components/harness/README.md) | — | А |

**Вывод этапа.** Новые подходы решают две вещи: **контекст** (исполнение кода, поиск тулов, ленивые скиллы) и **место проверки** (шлюзы). Второе — то, чего нет в опорном решении.

<span class="gate">G4</span> ✅ 9 кандидатов; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| MCP для внешних систем | П1 | подключение без кода | стандарт у Linear, Copilot, Claude, [ICPlan](../architecture/components/icplan/README.md) (Б) | базовая |
| Прямые внутренние вызовы | П3 | нет лишнего прыжка | [FR-179](../architecture/components/mcp-tools/prd.md) (А) | базовая |
| Проверка списка тулов **вне** исполняемой среды | П2, П5 | код агента не обходит проверку | виртуальные серверы ContextForge (Б); принцип «не доверять sandbox» ([AD-18](../architecture/decisions/AD-18.yaml), А) | базовая |
| Секреты в шлюзе, а не в прокси | П4 | ключ не подставляется любому процессу sandbox | ContextForge, JWT (Б) | линейная |
| Ленивая загрузка описаний тулов | П6 | меньше токенов при многих тулах | исполнение кода −98,7% (Б); поиск тулов (В) | линейная |
| Ленивые скиллы | П6, П8 | инструкции скилла — только когда нужен | Agent Skills (Б) | привлекательная |
| Исполнение кода поверх MCP | П6 | огромная экономия | Б; но вызовы из кода не проходят G2 на каждый тул | привлекательная, конфликт с П5 |
| MCP для внутренних вызовов | П3 | — | лишний прыжок | обратная |

**Вывод этапа.** Базовая функция, которой у нас нет, — проверка списка тулов вне sandbox. Экономия контекста — линейная: нужна, когда тулов много.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше (поиск тулов — В, берём как идею).

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| Правила [FR-179](../architecture/components/mcp-tools/prd.md), MCP, обрезка, таймауты | оставить | как в спеке | [FR-176](../architecture/components/mcp-tools/prd.md) – [FR-179](../architecture/components/mcp-tools/prd.md) |
| Проверка вне sandbox | адаптировать | MCP-прокси Runner: фильтр `tools/list` по манифесту, allowlist и G2 на `tools/call`, учётные данные из Secret; egress-прокси ключ агента к MCP не подставляет | [design AD-19](..\source\design\define-agent-platform\design.md), [FR-177](../architecture/components/mcp-tools/prd.md), задача 2.1.9 |
| Ленивая загрузка описаний | не брать сейчас | allowlist по умолчанию минимальный, порог (описания > 10% окна) на MVP не достигается | [BACKLOG](..\source\BACKLOG.md) |
| Ленивые скиллы | не брать сейчас | скиллов на MVP мало; краткое описание в промпте, инструкции по запросу — при росте | [BACKLOG](..\source\BACKLOG.md) |
| Исполнение кода поверх MCP | не брать сейчас | конфликт с G2 на вызов; вернуться, когда проверка будет в шлюзе | [BACKLOG](..\source\BACKLOG.md) |
| UTCP, «всё через MCP», только нативные | не брать | Э5 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** подключение без кода | П1 → базовая | новая система — настройка |
| **M2** внутреннее — без MCP | П3 → базовая | прямой вызов |
| **M3** открытый стандарт или проект | — | лицензия, сообщество |
| **К1** где проверяется список тулов и G2 | П2, П5 | внутри или вне sandbox |
| **К2** где секреты | П4 | прокси, шлюз, сервер |
| **К3** расход контекста | П6 | токены на описания |
| **К4** новая инфраструктура | — | сервисы |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 без кода | M2 внутреннее напрямую | M3 открытый | Итог |
|---|---|---|---|---|
| Гибрид (как сейчас) | да | да | да | проходит |
| Гибрид + MCP-шлюз | да | да | да | проходит |
| Исполнение кода поверх MCP | да | да | да | проходит |
| Всё через MCP | да | **нет** | да | ✗ |
| Только нативные тулы | **нет** | да | да | ✗ |

### Как встаёт в схему

Сейчас:

```
 sandbox ┌──────────────────────────────────────────────┐
         │ Harness: allowlist + G2 ──I10──▶ OPA          │
         │    └─ tools/call ─┐                           │
         │ код агента (bash) ─┼─ curl ──▶ Squid* ──I9──▶ MCP itsaplan-core, git
         └────────────────────┴──────────────────────────┘    * подставляет ключ агента любому процессу
```

С MCP-шлюзом (по решению [AD-19](../architecture/decisions/AD-19.yaml) роль шлюза выполняет MCP-прокси [Agent Runner](../architecture/components/agent-runner/README.md)):

```
 sandbox ┌──────────────────────────────┐
         │ Harness ── токен запуска ─────┼──I9*──▶ MCP-шлюз: виртуальный сервер запуска
         │ код агента ── без ключа ──────┼──✗       ├─ allowlist агента (из Platform module)
         └──────────────────────────────┘          ├─ G2 ──I10*──▶ OPA
                                                    ├─ секреты серверов
                                                    └──▶ MCP itsaplan-core, git
  * — стыки меняются
```

| Стык | Как сейчас | С MCP-шлюзом |
|---|---|---|
| [I9](../architecture/components/harness/integrations/I9.yaml) [Harness](../architecture/components/harness/README.md) → MCP | И2: напрямую через Squid | И1: через шлюз, токен запуска |
| [I10](../architecture/components/harness/integrations/I10.yaml) G2 → OPA | И2: из [Harness](../architecture/components/harness/README.md) | И1: из шлюза для вызовов MCP; из [Harness](../architecture/components/harness/README.md) — для нативных тулов |
| [I17](../architecture/components/sandbox/integrations/I17.yaml) Squid | И2: подставляет ключ агента | И2: к MCP только шлюз, ключ не подставляется |
| [Platform module](../architecture/components/platform-module/README.md) → шлюз | — | И1: allowlist агента и серверы |

**Изменения у соседей (если шлюз):** [Sandbox](../architecture/components/sandbox/README.md) ([FR-87](../architecture/components/sandbox/prd.md) — разрешённые хосты, [FR-88](../architecture/components/sandbox/prd.md) — подстановка ключа), [Guardrails](../architecture/components/guardrails/README.md) ([FR-112](../architecture/components/guardrails/prd.md) — G2 для MCP в шлюзе), [Platform module](../architecture/components/platform-module/README.md) (отдаёт allowlist шлюзу), инфраструктура и техспека (новый сервис), задачи 1.4, 2.4, 4.2.

**Вывод этапа.** ==Сейчас проверка списка тулов и G2 живёт в той же среде, где исполняется код агента, — любая утилита в sandbox может её обойти.== Шлюз переносит проверку наружу ценой нового сервиса и изменения четырёх стыков.

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — DevOps за «как есть», «адвокат дьявола» атакует шлюз.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| Безопасность 🤖 | шлюз | проверка внутри недоверенной среды обходится одним `curl` (Э7) | — | — |
| Архитектор 🤖 | шлюз | один вход к MCP, секреты вне sandbox | новый сервис на пути каждого вызова | шлюз лёгкий, таймауты прежние |
| Администратор 🤖 | шлюз | список тулов агента виден и проверяется в одном месте | — | — |
| Разработчик 🤖 | нейтрально | [Harness](../architecture/components/harness/README.md) почти не меняется: другой адрес и токен | — | — |
| DevOps 🤖 (оппонент) | как есть | ещё один сервис, ещё одна точка отказа | отказ шлюза = агенты без тулов | FMEA и fail-closed |
| Владелец продукта 🤖 | как есть | сроки этапа 2 | — | временная мера до шлюза |

| Спор | Разрешение |
|---|---|
| Безопасность против DevOps: «шлюз или как есть» | ✅ **решено исследованием ([AD-19](../architecture/decisions/AD-19.yaml)):** MCP-прокси в Runner — проверка вне sandbox без нового сервиса; это снимает и довод DevOps |
| Владелец продукта: «сроки этапа 2» | **условие:** +8 ч в задаче 2.1 (2.1.9), оценка 2.1 остаётся в пределах 5,5–7,5 дн |
| Адвокат дьявола: «исполнение кода экономит 98% токенов — почему нет?» | **условие:** вернуться, когда G2 будет в шлюзе; сейчас код обойдёт проверку на каждый тул |

**Вывод этапа.** Спор о шлюзе разрешён исследованием: прокси в Runner даёт проверку вне sandbox без нового сервиса, поэтому возражение DevOps снято.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение или вопрос 📌.

## Э9. Выбор {#e9}

| Потребность | Гибрид как есть | Гибрид + шлюз или прокси Runner | Исполнение кода |
|---|---|---|---|
| П1 без кода | закрывает | закрывает | закрывает |
| П2 только свои тулы | частично: обходится из sandbox | закрывает | частично |
| П3 внутреннее напрямую | закрывает | закрывает | закрывает |
| П4 секреты вне sandbox | закрывает: ключ в прокси | закрывает: ключ в шлюзе | закрывает |
| П5 G2 на каждый вызов | не закрывает для вызовов в обход | закрывает | не закрывает |
| П6 контекст | с доработкой: ленивая загрузка | с доработкой | закрывает |
| П7 таймауты, обрезка | закрывает | закрывает | частично |
| П8 скиллы | закрывает | закрывает | закрывает |

- **Утверждение.** Правила [FR-179](../architecture/components/mcp-tools/prd.md) оставляем; проверка allowlist и G2 для MCP — в MCP-прокси [Agent Runner](../architecture/components/agent-runner/README.md) вне sandbox ([AD-19](../architecture/decisions/AD-19.yaml)).
- **Основания.** Гибрид закрывает подключение, задержку и секреты. Но П2 и П5 нарушаются любым процессом в sandbox, а прокси вне sandbox их закрывает. У Runner уже есть манифест, токен, подтверждения и клиент OPA; MCP SDK для Go — официальный (v1.8.0).
- **Связка.** [Sandbox](../architecture/components/sandbox/README.md) по [AD-18](../architecture/decisions/AD-18.yaml) — недоверенная среда. Проверка в ней — не проверка.
- **Опровержение.** Отдельный шлюз нужен, если MCP-серверов станет много и понадобятся общие политики, кэш и каталог вне запуска. Тогда — agentgateway или ContextForge перед Runner.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Проверка allowlist и G2 для MCP вне sandbox — MCP-прокси Runner | [design AD-19](..\source\design\define-agent-platform\design.md) | ✅ решено: [AD-19](../architecture/decisions/AD-19.yaml) |
| [FR-177](../architecture/components/mcp-tools/prd.md), [FR-87](../architecture/components/sandbox/prd.md), [FR-88](../architecture/components/sandbox/prd.md), [FR-112](../architecture/components/guardrails/prd.md), [FR-79](../architecture/components/agent-runner/prd.md); стыки [I9](../architecture/components/harness/integrations/I9.yaml), [I10](../architecture/components/harness/integrations/I10.yaml), [I17](../architecture/components/sandbox/integrations/I17.yaml); потоки, API, техспеки; задачи 2.1.9, 4.2.7, 1.4.8 | спеки tool-integration, agent-sandbox, guardrails, agent-runner | ✅ внесено |
| Ленивая загрузка описаний тулов при большом числе | [FR-30](../architecture/components/harness/prd.md) | ✅ внесено в бэклог: порог на MVP не достигается |
| Ленивые скиллы | [FR-181](../architecture/components/mcp-tools/prd.md) | ✅ внесено в бэклог |
| Исполнение кода поверх MCP | [BACKLOG](..\source\BACKLOG.md) | ✅ внесено в бэклог |
| ContextForge, agentgateway — Assess | [TECHNOLOGIES](..\source\TECHNOLOGIES.md) | ✅ внесено |
| Правила [FR-179](../architecture/components/mcp-tools/prd.md) | спека tool-integration | — не требуется |
| Потоки MCP | [потоки](..\architecture\components\mcp-tools\docs\how.md) | ✅ внесено: потоки 1–3 через прокси Runner |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

<details markdown>
<summary>Приложение A. Карточки кандидатов</summary>

GitHub API на 11.10.2026.

| Технология | Лицензия | ★ | Релиз | Активность |
|---|---|---|---|---|
| Спецификация MCP | открытая | 9 425 | 2026-07-28 | 11.10.2026 |
| agentgateway | Apache-2.0 | 5 278 | v1.6.0 | 11.10.2026 |
| ContextForge (IBM) | Apache-2.0 | 4 597 | v1.0.11 | 09.10.2026 |
| Docker MCP Gateway | MIT | 1 591 | — | 23.09.2026 |
</details>

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- [Code execution with MCP — Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp) (Б); [обзор AIMultiple](https://research.aimultiple.com/code-execution-with-mcp) (В); [MCP context bloat 2026](https://mcp.directory/blog/mcp-context-bloat-fix-2026-tool-search-code-mode-progressive-disclosure) (В)
- [ContextForge MCP Gateway](https://github.com/IBM/mcp-context-forge) (Б) · [agentgateway](https://agentgateway.dev/docs/) (Б) · [Docker MCP Gateway](https://github.com/docker/mcp-gateway) (Б)
- [Спецификация MCP](https://github.com/modelcontextprotocol/modelcontextprotocol) (Б)
- Наши: [FR-177](../architecture/components/mcp-tools/prd.md), [FR-179](../architecture/components/mcp-tools/prd.md), [FR-87](../architecture/components/sandbox/prd.md), [FR-88](../architecture/components/sandbox/prd.md), [AD-18: Squid, sandbox недоверенный](..\source\design\define-agent-platform\design.md) (А)
