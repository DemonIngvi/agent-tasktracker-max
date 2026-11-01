# R&D: Где хранятся определения и настройки агентов

← [Все R&D](README.md) · методология R&D v3.1 · компонент: **[Platform module](../architecture/components/platform-module/README.md)** · решение: [design AD-9, AD-18](..\source\design\define-agent-platform\design.md) · спеки: agent-registry, control-plane

<div class="rnd-hero" markdown>
<div class="rnd-q">Вопрос</div>
Где источник правды для определений агентов и их настроек: в БД [ICPlan](../architecture/components/icplan/README.md), в git или в отдельном сервисе — так, чтобы администратор менял их без git, а изменения можно было ревьюить, откатывать и переносить между окружениями?

<div class="rnd-a">Ответ: БД [ICPlan](../architecture/components/icplan/README.md) — источник правды, у определения есть версии, экспорт и импорт в YAML `agent/v1`. Правила Rego остаются в git. У аналогов (Claude Code, Copilot) берём идею «агент как файл в репозитории» — как импорт, а не второй источник правды.</div>

<span class="rnd-badge adopt">Adopt</span> БД [ICPlan](../architecture/components/icplan/README.md) + YAML · [Platform module](../architecture/components/platform-module/README.md) в форке [ICPlan](../architecture/components/icplan/README.md) · 0 $ · данные 11.10.2026
</div>

```deck
# Покрытие потребностей П1–П7
> БД ICPlan закрывает всё; git удобен разработчикам, но даёт второй источник правды
stack БД ICPlan + YAML: 7 ok, 0 part, 0 no
stack Git (Config Repo): 4 ok, 1 part, 2 no
stack Отдельный Platform API: 5 ok, 1 part, 1 no
stack Агент-файл в репозитории продукта: 3 ok, 2 part, 2 no
# Кто меняет настройки
> администратор работает в ICPlan; git требует PR и конвейер
bar БД ICPlan: 1/1 в интерфейсе ICPlan ok
bar Git: 0/1 через PR no
bar Отдельный API: 1/1 в другом интерфейсе part
# Объём доработки
> три подзадачи, 20 ч из 103 ч задачи 4.4: схема, версии, экспорт и импорт YAML
bar Схема БД модуля и миграции: 8/103 4.4.1 — 8 ч ok
bar Версии агента по хешу определения: 6/103 4.4.5 — 6 ч ok
bar Экспорт и импорт YAML agent/v1: 6/103 4.4.18 — 6 ч ok
# Позиции ролей
side БД ICPlan | Git
pos Администратор: -2 | правлю там, где работаю
pos Архитектор: -1 | один источник правды (AD-9)
pos DevOps: 0 | бэкап БД покрывает всё
pos Безопасность: 0 | журнал изменений есть у обоих
pos Разработчик: 2 | ревью через PR
# Что меняется
> AD-9 подтверждён; импорт агента из репозитория — в бэклог
stack Документы: 3 ok, 0 part, 4 mute
- ✅ бэклог: импорт определения из файла в репозитории (формат как у Claude Code, Copilot)
- ✅ подтверждено: «тулы по умолчанию — нет» вместо «наследовать все»
```

**Почему БД [ICPlan](../architecture/components/icplan/README.md).** Три вывода:

<div class="rnd-grid" markdown>
<div markdown>
**1. Меняет администратор, а не разработчик**

Агентов, их тулы и проекты настраивает администратор в интерфейсе [ICPlan](../architecture/components/icplan/README.md) (истории US-ICP). Git требует PR и конвейер применения, отдельный сервис — второй интерфейс. Версии и откат есть в БД ([FR-55](../architecture/components/platform-module/prd.md)), ревью и перенос — через YAML ([Э9](#e9)).
</div>
<div markdown>
**2. Один источник правды**

Если агенты живут и в БД, и в git, они расходятся при первой правке в интерфейсе. [AD-9](../architecture/decisions/AD-9.yaml) запрещает два источника: YAML — это экспорт и импорт, а не синхронизация. Правила Rego — код, они в git с тестами ([Э7](#e7)).
</div>
<div markdown>
**3. Агент-файл в репозитории — как импорт**

Claude Code и Copilot хранят агентов файлами Markdown с YAML-шапкой в репозитории. Это удобно разработчикам, и мы берём идею как импорт по запросу. Не берём их умолчание «тулы не указаны — доступны все»: у нас по умолчанию тулов нет ([Э6](#e6)).
</div>
</div>

<div class="rnd-grid" markdown>
<div class="take" markdown>
**Берём**

- БД [ICPlan](../architecture/components/icplan/README.md) (S1, S2) как источник правды;
- версии определения;
- экспорт и импорт YAML `agent/v1`;
- Rego в git с тестами.
</div>
<div class="adapt" markdown>
**Адаптируем**

- агент как файл Markdown + YAML в репозитории (Claude Code, Copilot) → импорт по запросу;
- приоритет «проект над пользователем» (Claude Code) → уровни L0–L3 уже работают так;
- переносимый формат агента (Agent File, Letta) → сверка полей при экспорте.
</div>
<div class="drop" markdown>
**Не берём**

- синхронизацию git ↔ БД: два источника правды;
- умолчание «нет списка тулов — все тулы»;
- отдельный сервис настроек.
</div>
</div>

<div class="rnd-grid" markdown>
<div class="no" markdown>
**Отсеяны до сравнения**

- **Синхронизация git ↔ БД** — два источника правды ([AD-9](../architecture/decisions/AD-9.yaml)).
</div>
<div class="risk" markdown>
**Риски и пересмотр**

- Ошибочная правка в интерфейсе — версии и откат ([FR-55](../architecture/components/platform-module/prd.md)), журнал изменений.
- Пересмотр: агентов начнут создавать разработчики в репозиториях чаще, чем администраторы в интерфейсе.
</div>
</div>

<div class="rnd-chain" markdown>
<div markdown>**Э1 Вопрос**<span class="gate">G1</span></div>
<div markdown>**Э2 Потребности**7 <span class="gate">G2</span></div>
<div markdown>**Э3 БД [ICPlan](../architecture/components/icplan/README.md)**5 функций <span class="gate">G3</span></div>
<div markdown>**Э4 Альтернативы**6 <span class="gate">G4</span></div>
<div markdown>**Э5 Ценность**<span class="gate">G5</span></div>
<div markdown>**Э6 Перенос**3 MUST <span class="gate">G6</span></div>
<div markdown>**Э7 Встраивание**[I4](../architecture/components/agent-runner/integrations/I4.yaml), [I16](../architecture/components/platform-module/integrations/I16.yaml), [I20](../architecture/components/icplan/integrations/I20.yaml) <span class="gate">G7</span></div>
<div markdown>**Э8 Спор**5 ролей <span class="gate">G8</span></div>
<div markdown>**Э9 Выбор**<span class="gate">G9</span></div>
<div markdown>**Э10 Последствия**7 <span class="gate">G10</span></div>
</div>

---

Дальше — как получен ответ, этап за этапом.

## Э1. Вопрос {#e1}

**Ситуация.** Определение агента — модель, инструкция, тулы, навыки, MCP-серверы, проекты. Настройки — лимиты, бюджеты, профили. Их читают Runner ([I4](../architecture/components/agent-runner/integrations/I4.yaml)) и [Harness](../architecture/components/harness/README.md) (через [`RunBundle`](../architecture/data/model-RunBundle.yaml)).

**Осложнение.** Проект AI-агент хранил всё в git (Config Repo); [ICPlan](../architecture/components/icplan/README.md) хранит агентов в своей БД. Аналоги (Claude Code, Copilot) держат агентов файлами в репозитории.

**Вопрос.** Где источник правды определений и настроек?

**Решает:** владелец продукта. **Не решаем:** уровни параметров L0–L3 (задача 2.8), правила Rego ([guardrails](guardrails-engine.md)).

<span class="gate">G1</span> ✅ вопрос — выбор; есть владелец; связан с [AD-9](../architecture/decisions/AD-9.yaml), [AD-18](../architecture/decisions/AD-18.yaml).

## Э2. Потребности {#e2}

| # | Потребность | Откуда | Что ломается без неё |
|---|---|---|---|
| П1 | администратор меняет агента в интерфейсе [ICPlan](../architecture/components/icplan/README.md) | US-ICP (администратор), [FR-54](../architecture/components/platform-module/prd.md) | правка агента требует разработчика |
| П2 | версии и откат | [FR-55](../architecture/components/platform-module/prd.md) | ошибочную правку не вернуть |
| П3 | один источник правды | [FR-56](../architecture/components/platform-module/prd.md), [AD-9](../architecture/decisions/AD-9.yaml) | БД и файлы расходятся |
| П4 | ревью и перенос между окружениями | [FR-56](../architecture/components/platform-module/prd.md) | нельзя показать изменение и перенести в prod |
| П5 | проверка связей (модель, тулы, навыки) при сохранении | [FR-57](../architecture/components/platform-module/prd.md) | агент ссылается на несуществующий тул |
| П6 | запуск идёт по версии на момент старта | `agent.version`, [FR-98](../architecture/components/platform-module/prd.md) | правка ломает идущий запуск |
| П7 | без нового сервиса | [AD-15](../architecture/decisions/AD-15.yaml) | ещё одна система |

<span class="gate">G2</span> ✅ у потребностей есть требования и решения.

## Э3. Опорное решение: БД ICPlan + YAML {#e3}

| # | Функция | Что делает | Потребность |
|---|---|---|---|
| F1 | Агенты в БД [ICPlan](../architecture/components/icplan/README.md) (S1) и настройки [Platform module](../architecture/components/platform-module/README.md) (S2) | правка в интерфейсе | П1, П7 |
| F2 | Версии определения | каждая правка — новая версия, откат | П2, П6 |
| F3 | Экспорт и импорт YAML `agent/v1` | ревью и перенос | П4 |
| F4 | Валидация при сохранении | связи с каталогом | П5 |
| F5 | Rego в git | правила — код с тестами | — |

**Вывод этапа.** Опорное решение закрывает все потребности функциями [ICPlan](../architecture/components/icplan/README.md) и [Platform module](../architecture/components/platform-module/README.md).

<span class="gate">G3</span> ✅ функции из спек и [AD-9](../architecture/decisions/AD-9.yaml) (А).

## Э4. Альтернативы и их ключевые функции {#e4}

Поиск 11.10.2026: документация Claude Code, GitHub Copilot, Letta; решения проекта AI-агент.

| Кандидат | Ключевые функции | Чего нет у опорного | Уровень |
|---|---|---|---|
| **Git (Config Repo, проект AI-агент)** | определения файлами, ревью через PR, история git, конвейер применения | ревью через PR | А |
| **Агент-файл в репозитории продукта** (Claude Code: `.claude/agents/*.md`; Copilot: `.github/agents/`) | Markdown + YAML-шапка: имя, описание, тулы, модель; тело — системный промпт; проект важнее пользователя; в Claude Code без списка тулов — все тулы | агент рядом с кодом | Б (Claude Code), В (Copilot) |
| **Agent File** (Letta, Apache-2.0, 1 204★, v1.0.0-alpha11) | переносимый формат агента: инструкции, память, тулы | переносимость между системами | Б |
| **Отдельный Platform API** | свой сервис настроек и БД | — | — |
| **Синхронизация git ↔ БД** | правки в двух местах | — | — |
| **Только конфиг деплоя** (values.yaml) | настройки в Helm | — | — |

**Вывод этапа.** Git и файлы в репозитории удобны разработчикам: ревью через PR, агент рядом с кодом. Интерфейс и версии в БД удобны администратору.

<span class="gate">G4</span> ✅ 6 кандидатов, включая «как есть»; источники трёх видов; дата есть.

## Э5. Ценность функций {#e5}

| Функция | Потребность | Почему ценна | Доказательство | Класс |
|---|---|---|---|---|
| Правка в интерфейсе | П1 | администратор не зависит от разработчика | истории [ICPlan](../architecture/components/icplan/README.md) (А); Linear, Jira — агенты настраиваются админом в интерфейсе (Б) | базовая |
| Один источник правды | П3 | нет расхождений | [AD-9](../architecture/decisions/AD-9.yaml) (А) | базовая |
| Версии и откат | П2, П6 | правка не ломает запуск | [FR-55](../architecture/components/platform-module/prd.md) (А); история git (Б) | базовая |
| Ревью через PR | П4 | изменения видны до применения | git (Б) | линейная: у нас — экспорт YAML и diff |
| Агент рядом с кодом | — | разработчик держит агента в репозитории | Claude Code, Copilot (Б, В) | привлекательная |
| Переносимый формат | П4 | агент переносится в другие системы | Agent File (Б, альфа) | привлекательная |
| «Без списка тулов — все тулы» | — | — | противоречит наименьшим правам ([FR-177](../architecture/components/mcp-tools/prd.md)) | обратная |

**Вывод этапа.** Базовые функции у БД [ICPlan](../architecture/components/icplan/README.md) есть. Агент-файл в репозитории — привлекательная функция для разработчиков, если не создаёт второй источник правды.

<span class="gate">G5</span> ✅ у функций есть доказательство уровня Б и выше (Copilot — В, берём как идею).

## Э6. Перенос и критерии {#e6}

| Функция | Решение | Как | Где |
|---|---|---|---|
| БД, версии, YAML, валидация | оставить | [AD-9](../architecture/decisions/AD-9.yaml) | [FR-53](../architecture/components/platform-module/prd.md) – [FR-57](../architecture/components/platform-module/prd.md) |
| Агент-файл в репозитории | адаптировать | импорт по запросу из файла Markdown + YAML в версию агента; БД остаётся источником правды | [BACKLOG](..\source\BACKLOG.md) |
| Переносимый формат | не брать сейчас | сверка полей `agent/v1` с Agent File при выходе версии 1.0 | [BACKLOG](..\source\BACKLOG.md) |
| «Без списка — все тулы» | не брать | по умолчанию тулов нет | `agent.tools` (уже) |
| Синхронизация git ↔ БД, отдельный сервис | не брать | П3, П7 | — |

**Критерии:**

| Критерий | Цепочка | Как проверяем |
|---|---|---|
| **M1** один источник правды | П3 → базовая | одно место записи |
| **M2** правка без git | П1 → базовая | интерфейс |
| **M3** версии | П2 → базовая | откат |
| **К1** ревью и перенос | П4 | экспорт, diff |
| **К2** новые сервисы | П7 | что ставить |
| **К3** удобство разработчикам | — | файл рядом с кодом |

<span class="gate">G6</span> ✅ у функций есть решения; критерии с цепочкой.

## Э7. Отсев и встраивание {#e7}

### Отсев по MUST

| Кандидат | M1 один источник | M2 без git | M3 версии | Итог |
|---|---|---|---|---|
| БД [ICPlan](../architecture/components/icplan/README.md) + YAML | да | да | да | проходит |
| Git (Config Repo) | да | **нет** | да | ✗ |
| Агент-файл в репозитории как источник | да | **нет** | да | ✗ (→ импорт) |
| Отдельный Platform API | да | да | да | проходит |
| Синхронизация git ↔ БД | **нет** | да | да | ✗ |
| Только конфиг деплоя | да | **нет** | частично | ✗ |

### Как встаёт в схему

```
 Администратор ──I20──▶ ICPlan UI / API ──▶ S1 агенты, S2 настройки (Platform module, версии)
                                     │  ▲ импорт / экспорт YAML agent/v1 (импорт из файла в репозитории*)
 Agent Runner ──I4 AgentSettings (версия запуска)──┘
 Platform module ──I16 данные правил──▶ OPA ◀── git: Rego (S8)
  * — импорт по запросу, бэклог
```

| Стык | БД [ICPlan](../architecture/components/icplan/README.md) | Отдельный Platform API |
|---|---|---|
| [I20](../architecture/components/icplan/integrations/I20.yaml) интерфейс администратора | И4: [ICPlan](../architecture/components/icplan/README.md) | И1: свой интерфейс |
| [I4](../architecture/components/agent-runner/integrations/I4.yaml) Runner читает настройки | И2: [Platform module](../architecture/components/platform-module/README.md) в api [ICPlan](../architecture/components/icplan/README.md) | И1: новый сервис |
| [I16](../architecture/components/platform-module/integrations/I16.yaml) данные правил в OPA | И2 | И1 |
| S1 / S2 | И4 / И2 | И1: своя БД |

**Изменения у соседей:** у БД [ICPlan](../architecture/components/icplan/README.md) — нет; у отдельного API — Runner ([I4](../architecture/components/agent-runner/integrations/I4.yaml)), [ICPlan](../architecture/components/icplan/README.md) UI (ссылки на агентов), OPA ([I16](../architecture/components/platform-module/integrations/I16.yaml)), инфраструктура.

**Вывод этапа.** ==БД [ICPlan](../architecture/components/icplan/README.md) уже стоит в схеме; любой другой вариант добавляет второй интерфейс или второй источник правды.==

<span class="gate">G7</span> ✅ отсев; готовность стыков; изменения у соседей.

## Э8. Спор ролей {#e8}

Роли 🤖. Оппонент — Разработчик за git, «адвокат дьявола» атакует БД.

| Роль | За | Довод | Опасение | Согласится, если |
|---|---|---|---|---|
| Администратор 🤖 | БД [ICPlan](../architecture/components/icplan/README.md) | правлю там, где работаю | — | — |
| Архитектор 🤖 | БД [ICPlan](../architecture/components/icplan/README.md) | один источник правды ([AD-9](../architecture/decisions/AD-9.yaml)) | — | — |
| DevOps 🤖 | нейтрально | бэкап БД покрывает агентов | перенос между окружениями | экспорт и импорт YAML |
| Безопасность 🤖 | нейтрально | журнал изменений есть | — | — |
| Разработчик 🤖 (оппонент) | git | ревью через PR, агент рядом с кодом | правки в интерфейсе без ревью | diff версий в интерфейсе; импорт из файла |

| Спор | Разрешение |
|---|---|
| Разработчик: «хочу агента в репозитории» | ✅ **внесено в бэклог:** импорт определения из файла в репозитории |
| Адвокат дьявола: «правка в интерфейсе без ревью сломает агента» | **условие:** версии и откат ([FR-55](../architecture/components/platform-module/prd.md)), изменения со следующего запуска ([FR-98](../architecture/components/platform-module/prd.md)) |

**Вывод этапа.** Спор разрешён импортом из файла: разработчик держит агента рядом с кодом, источник правды остаётся один.

<span class="gate">G8</span> ✅ у каждого спора есть разрешение.

## Э9. Выбор {#e9}

| Потребность | БД [ICPlan](../architecture/components/icplan/README.md) + YAML | Git | Отдельный API | Агент-файл как источник |
|---|---|---|---|---|
| П1 правка в интерфейсе | закрывает | не закрывает | частично: другой интерфейс | не закрывает |
| П2 версии | закрывает | закрывает | закрывает | закрывает |
| П3 один источник | закрывает | закрывает | закрывает | частично |
| П4 ревью и перенос | закрывает: YAML | закрывает | закрывает | закрывает |
| П5 валидация | закрывает | с доработкой: в конвейере | закрывает | частично |
| П6 версия запуска | закрывает | закрывает | закрывает | частично |
| П7 без нового сервиса | закрывает | не закрывает: конвейер | не закрывает | закрывает |

- **Утверждение.** БД [ICPlan](../architecture/components/icplan/README.md) — источник правды, версии, YAML ([AD-9](../architecture/decisions/AD-9.yaml)).
- **Основания.** Закрывает все 7 потребностей; стоит в схеме без изменений у соседей.
- **Связка.** Определения меняют администраторы; удобство разработчиков закрывается импортом из файла без второго источника правды.
- **Опровержение.** Вывод неверен, если агентов начнут создавать в основном разработчики в репозиториях. Тогда — git как источник и интерфейс только для просмотра.

<span class="gate">G9</span> ✅ вывод следует из покрытия, встраивания и спора; есть опровержение.

## Э10. Последствия {#e10}

| Изменение | Документ | Статус |
|---|---|---|
| Импорт определения агента из файла Markdown + YAML в репозитории; сверка с Agent File | [BACKLOG](..\source\BACKLOG.md) | ✅ внесено в бэклог |
| «Тулы по умолчанию — нет», а не «все» | `agent.tools` в [interfaces agent-registry](..\architecture\components\platform-module\docs\agent-registry-interfaces.md) | ✅ подтверждено, без изменений |
| Решения [AD-9](../architecture/decisions/AD-9.yaml), [AD-18](../architecture/decisions/AD-18.yaml) | design | ✅ подтверждено, без изменений |
| Стыки [I4](../architecture/components/agent-runner/integrations/I4.yaml), [I16](../architecture/components/platform-module/integrations/I16.yaml), [I20](../architecture/components/icplan/integrations/I20.yaml) | спеки agent-registry, control-plane | — не требуется |
| Поток [Platform module](../architecture/components/platform-module/README.md) | [поток](..\architecture\components\platform-module\docs\how.md) | — не требуется |
| Техспека [Platform module](../architecture/components/platform-module/README.md) | [техспека](..\architecture\components\platform-module\docs\techspec.md) | — не требуется |
| Формат YAML `agent/v1` | [задача 1.2](..\source\tasks\1.2-agent-definition-yaml.md) | — не требуется |

<span class="gate">G10</span> ✅ у каждого изменения есть документ и статус.

## Источники

Поиск и чтение — 11.10.2026; в скобках уровень доказательства.

- Claude Code: [субагенты](https://docs.claude.com/en/docs/claude-code/sub-agents) (Б)
- GitHub Copilot: [о пользовательских агентах](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/agents/cloud-agent/about-custom-agents) (Б), [примеры awesome-copilot](https://mintlify.com/github/awesome-copilot/cookbook/examples/custom-agents) (В)
- [Agent File (Letta)](https://github.com/letta-ai/agent-file) (Б)
- Наши: [AD-9, AD-18](..\source\design\define-agent-platform\design.md), [FR-53](../architecture/components/platform-module/prd.md) – [FR-58](../architecture/components/platform-module/prd.md) (А)
