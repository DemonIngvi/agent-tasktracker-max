#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Переносит agent-architecture в проект документации новой структуры. Источник только читается.

Запуск: uv run migrate.py <источник> <проект>
Результат: PRD, эпики, Spine, модель системы в docs/architecture и отчёт docs/migration.md.
"""
import collections
import pathlib
import re
import sys

import yaml

SRC, ROOT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
DATE = "2026-11-01"
NAME = "agent-tasktracker-max"
TITLE = "Agent TaskTracker Max"
DATA = SRC / "data"
ARCH = ROOT / "docs" / "architecture"
PLAN = ROOT / "_bmad-output" / "planning-artifacts"
SPECS = sorted(p for p in (SRC / "openspec" / "changes").rglob("spec.md") if "archive" not in p.parts)
SPEC_COMPONENT = {
    "agent-harness": "harness", "agent-memory": "memory", "agent-registry": "platform-module", "agent-runner": "agent-runner",
    "agent-sandbox": "sandbox", "control-plane": "platform-module", "guardrails": "guardrails", "llm-gateway": "llm-gateway",
    "observability": "observability", "platform-infrastructure": "infrastructure", "tool-integration": "mcp-tools",
    "icplan-integration": "icplan", "icplan-agent-autopickup": "icplan",
}
OWN = {"common": {"owner": "владелец платформы", "lifecycle": "planned", "criticality": "medium"}}
TR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя", "a b v g d e e zh z i y k l m n o p r s t u f h ts ch sh sch _ y _ e yu ya".split()))
report = collections.Counter()
lost = collections.defaultdict(list)


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def slug(text):
    out = "".join(TR.get(c, c) for c in text.lower()).replace("_", "")
    out = re.sub(r"[^a-z0-9]+", "-", out).strip("-")
    return out if out and out[0].isalpha() else f"x-{out}"


def write(rel, unit):
    path = ARCH / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(unit, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8", newline="\n")
    report[rel.split("/")[0]] += 1


def obj(folder, key, title, **fields):
    write(f"{folder}/{key}.yaml", {"id": key, "title": title, **OWN["common"], **fields})


def text_or(value, default="не задано", limit=200):
    """Прочерк в таблице источника значит, что значения нет."""
    value = (value or "").strip()
    return default if value in ("", "—", "-") else line(value, limit)


def units(folder):
    return {p.stem: load(p) for p in sorted((DATA / folder).glob("*.yaml")) if p.name != "_order.yaml"}


def parse_spec(path):
    text = path.read_text(encoding="utf-8")
    purpose = re.search(r"## Purpose\s+(.*?)\n\n", text, re.S)
    found = []
    for block in re.split(r"^### Requirement: ", text, flags=re.M)[1:]:
        title, _, body = block.partition("\n")
        code = re.search(r"\*\*ID:\*\* `(R-[A-Z]+-\d+)`", body)
        task = re.search(r"Реализует задача:\*\* \[([\d.]+)\]", body)
        first = re.split(r"\n#### |\n\*\*ID", body, maxsplit=1)[0].strip()
        first = re.sub(r"<a id=.*?</a>", "", first).strip()
        cases = re.findall(r"#### Scenario: (.+?)\n- \*\*WHEN\*\* (.+?)\n- \*\*THEN\*\* (.+?)(?:\n|$)", body)
        found.append({"title": title.strip(), "text": first, "cases": cases, "code": code.group(1) if code else None, "task": task.group(1) if task else None})
    return (purpose.group(1).strip() if purpose else ""), found


SPEC_DATA = {path.parent.name: parse_spec(path) for path in SPECS}
CODES, FR_LIST, NFR_LIST, BY_TITLE = {}, [], [], {}
for spec, (_, reqs) in SPEC_DATA.items():
    for req in reqs:
        is_nfr = re.search(r"нагрузк|производительност", req["title"], re.I)
        pool = NFR_LIST if is_nfr else FR_LIST
        code = f"{'NFR' if is_nfr else 'FR'}-{len(pool) + 1}"
        pool.append({**req, "id": code, "spec": spec})
        BY_TITLE[(spec, req["title"])] = code
        if req["code"]:
            CODES[req["code"]] = code


def clean(text):
    """Заменяет старые коды новыми и убирает ссылки на файлы исходного сайта."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\bR-[A-Z]+-\d+\b", lambda m: CODES.get(m.group(0), m.group(0)), text)
    return re.sub(r"(?<![\w-])D(\d+)\b", r"AD-\1", text).replace("|", "/").strip()


def line(text, limit=600):
    text = re.sub(r"\s+", " ", clean(text))
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + " …"


def table_rows(text, first):
    """Строки таблиц, заголовок которых начинается с first."""
    lines, rows = text.split("\n"), []
    for index, row in enumerate(lines[:-1]):
        if row.startswith(first) and lines[index + 1].startswith("|--"):
            head = [c.strip() for c in row.strip("|").split("|")]
            for item in lines[index + 2:]:
                if not item.startswith("|"):
                    break
                rows.append(dict(zip(head, [c.strip() for c in re.split(r"(?<!\\)\|", item.strip().strip("|"))])))
    return rows


def plain(value):
    return re.sub(r"`", "", value or "").strip()


COMPONENTS = units("components")
TITLE_TO_COMPONENT = {unit["name"]: key for key, unit in COMPONENTS.items()}
EXTERNAL = {"«git-провайдер»": ("git-provider", "Git-провайдер"), "«внешние хосты»": ("external-hosts", "Внешние хосты"),
            "«пользователи»": ("icplan-users", "Пользователи"), "«провайдеры моделей / mock»": ("llm-providers", "Провайдеры моделей"),
            "«сервисы»": ("platform-services", "Сервисы платформы")}
PERSONAS = load(DATA / "personas.yaml")
ROLE_ID = {code: slug(name) for code, name in PERSONAS["roles"].items()}


def write_model():
    (ARCH / "types.yaml").write_text("""system_kind: [own, external, vendor]
integration_type: [sync-api, async-queue, webhook, event-stream, file, shared-db, ui, unknown]
flow_type: [command, query, event, replication, batch]
data_class: [reference, master, transactional, event, derived, contract]
sensitivity: [public, internal, personal, secret]
""", encoding="utf-8", newline="\n")
    for code, name in PERSONAS["roles"].items():
        obj("actors", ROLE_ID[code], name, kind="role")
    obj("systems", "agent-platform", "Agent Platform", kind="own")
    obj("systems", "icplan", "ICPlan", kind="own")
    for key, title in EXTERNAL.values():
        obj("systems", key, title, kind="external")
    hosts = {row["owner"]: row["host"] for row in load(DATA / "hosts.yaml") if "block" not in row}
    for key, unit in COMPONENTS.items():
        extra = {"host": hosts[key]} if key in hosts else {}
        does = (unit.get("about") or {}).get("purpose") or unit.get("desc", "")
        obj("components", key, unit["name"], system="icplan" if key == "icplan" else "agent-platform", responsibility=line(does), **extra)

    tables = units("tables")
    table_ids = {}
    store_tables = collections.defaultdict(list)
    for name, unit in tables.items():
        key = name.replace("_", "-")
        table_ids[name] = key
        sensitivity = "secret" if re.search(r"key|secret|token", name) else "personal" if name in ("user", "users") else "internal"
        attributes = [{"name": c["name"], "type": str(c.get("type", "?"))} for c in unit.get("columns", [])]
        obj("data", key, f"Таблица {name}", **{"class": "master"}, sensitivity=sensitivity, attributes=attributes)
        store_tables[unit.get("store") or "S1"].append(name)
        if not unit.get("store"):
            lost["таблица без кода хранилища, отнесена к S1"].append(name)
    for domain in load(DATA / "datamodel.yaml").get("s1_domains", []):
        for name in domain["tables"]:
            if name not in table_ids:
                table_ids[name] = name.replace("_", "-")
                obj("data", table_ids[name], f"Таблица {name}", **{"class": "master"}, sensitivity="internal", attributes=[], states=[])
                store_tables["S1"].append(name)
                report["таблиц форка без описания колонок"] += 1
    models = units("models")
    for name, unit in models.items():
        attributes = [{"name": f["name"], "type": str(f.get("type", "?"))} for f in unit.get("fields", [])]
        write(f"data/model-{name}.yaml", {"id": name, "title": line(unit.get("purpose", name), 150), **OWN["common"], "class": "contract",
                                          "sensitivity": "internal", "attributes": attributes})

    stores, channels, params, fmea = {}, {}, {}, []
    for path in sorted(p for p in (SRC / "openspec" / "changes").rglob("interfaces.md") if "archive" not in p.parts):
        text = path.read_text(encoding="utf-8")
        for row in table_rows(text, "| ID | Хранилище"):
            stores.setdefault(row["ID"], row)
        for row in table_rows(text, "| ID | От → к"):
            channels.setdefault(row["ID"], row)
        for row in table_rows(text, "| Параметр |"):
            params.setdefault(plain(row["Параметр"]), row)
        fmea += [{**row, "spec": path.parent.name} for row in table_rows(text, "| Отказ |")]

    for code, row in stores.items():
        owner = TITLE_TO_COMPONENT.get(plain(row.get("Владелец")), "infrastructure")
        names = store_tables.get(code, [])
        retention = text_or(row.get("Резервирование / срок"))
        obj("stores", code, line(row["Хранилище"], 120), **{"owner": owner}, objects=[table_ids[n] for n in names], tables=names, writes=[owner], reads=[owner],
            deletes=owner, delete_trigger=retention, backup=retention)
    for code in set(store_tables) - set(stores):
        lost["хранилище из таблиц без описания"].append(code)

    source = load(DATA / "integrations.yaml")
    known_data = set(models) | set(table_ids.values())
    flows = 0
    for code, unit in source.items():
        ends = [EXTERNAL.get(unit[side], (unit[side],))[0] for side in ("from", "to")]
        row = channels.get(code, {})
        idem = plain(row.get("Идемпотентность")).lower()
        decided = None if idem in ("", "—", "-") else not idem.startswith("нет")
        kind = "unknown"
        text = (row.get("Протокол", "") + " " + row.get("Режим", "")).lower()
        if "webhook" in text:
            kind = "webhook"
        elif re.search(r"http|rest|grpc|mcp", text):
            kind = "sync-api"
        elif re.search(r"очеред|nats|redis|stream|sse", text):
            kind = "event-stream"
        obj("integrations", code, line(unit["what"], 120), **{"from": ends[0], "to": ends[1]}, purpose=line(unit["what"]), integration_type=kind,
            protocol=text_or(row.get("Протокол"), "не задан"), format=text_or(row.get("Формат"), "не задан"), auth=text_or(row.get("Аутентификация"), "не задан"),
            timeout=text_or(row.get("Таймаут"), "не задан", 120), retry=text_or(row.get("Повтор"), "не задан"), idempotent=decided)
        names = [m for m in unit.get("models", []) if m in known_data]
        lost["модель интеграции без описания"] += [f"{code}: {m}" for m in unit.get("models", []) if m not in known_data]
        if names:
            flows += 1
            obj("flows", f"F-{code}", line(unit["what"], 120), **{"from": ends[0], "to": ends[1]}, objects=names, trigger=line(unit["what"], 200),
                flow_type="query" if unit.get("data_in_response") else "command", over=code)
            if unit.get("data_in_response"):
                obj("flows", f"F-{code}-reply", "Ответ: " + line(unit["what"], 110), **{"from": ends[1], "to": ends[0]}, objects=names, trigger="ответ на запрос", flow_type="query", over=code)
    for code in set(channels) - set(source):
        lost["интерфейс есть в спеке, нет в integrations.yaml"].append(code)

    rows = []
    for row in fmea:
        marks = re.findall(r"\b([IS]\d+)\b", " ".join(row.values()))
        target = next((m for m in marks if m in source or m in stores), SPEC_COMPONENT.get(row["spec"], "infrastructure"))
        rows.append({"target": target, "failure": line(row["Отказ"], 200), "detection": text_or(row.get("Обнаружение")),
                     "behavior": text_or(row.get("Поведение"), limit=300), "recovery": text_or(row.get("Восстановление"))})
    write("fmea.yaml", {"rows": rows})
    return tables, table_ids, models, params


def story_numbers():
    numbers, epics = {}, []
    for number, folder in enumerate(sorted(p for p in (DATA / "stories").iterdir() if p.is_dir()), 1):
        items = []
        for index, path in enumerate(sorted(q for q in folder.glob("US-*.yaml")), 1):
            unit = load(path)
            numbers[path.stem] = f"{number}.{index}"
            items.append((path.stem, f"{number}.{index}", unit))
        epics.append((folder.name, number, items))
    return numbers, epics


def task_titles():
    found = {}
    for path in (SRC / "docs" / "tasks").glob("*.md"):
        head = re.search(r"^# (.+)$", path.read_text(encoding="utf-8"), re.M)
        found[path.name.split("-")[0]] = line(head.group(1) if head else path.stem, 110)
    return found


def add_task_stories():
    """Требование без истории в источнике связано с задачей. Такая связь становится технической историей."""
    covered = {(item.get("spec"), item.get("title")) for _, _, items in EPICS for _, _, unit in items for item in unit.get("reqs", []) if isinstance(item, dict)}
    groups = collections.defaultdict(list)
    for req in FR_LIST:
        if (req["spec"], req["title"]) not in covered:
            groups[(SPEC_COMPONENT[req["spec"]], req["task"] or "без-задачи")].append(req)
    titles = task_titles()
    for (folder, task), reqs in sorted(groups.items(), key=lambda p: (p[0][0], p[0][1])):
        number, items = next((n, i) for f, n, i in EPICS if f == folder)
        story = f"{number}.{len(items) + 1}"
        code = f"TASK-{task}-{folder}".replace(".", "-")
        accept = [f"{w} → {t}" for req in reqs for _, w, t in req["cases"][:2]] or [f"Требование «{req['title']}» выполнено" for req in reqs]
        unit = {"role": "Э", "want": titles.get(task, "выполнить технические требования компонента"), "so_that": "требования без пользовательской истории были реализованы",
                "accept": accept, "reqs": [{"spec": req["spec"], "title": req["title"]} for req in reqs]}
        items.append((code, story, unit))
        STORY[code] = story
        report["технических историй из задач"] += 1


STORY, EPICS = story_numbers()
add_task_stories()


def story_reqs(unit):
    found, missing = [], []
    for item in unit.get("reqs", []):
        code = BY_TITLE.get((item.get("spec"), item.get("title"))) if isinstance(item, dict) else CODES.get(item)
        (found if code else missing).append(code or str(item))
    return found, missing


def write_blocks(table_ids, params):
    extra_params, cards = {}, {}
    for folder in sorted(p for p in (DATA / "blocks").iterdir() if p.is_dir()):
        for path in sorted(folder.glob("*.yaml")):
            if path.name == "_order.yaml":
                continue
            unit = load(path)
            key = f"{folder.name}-{path.stem}"
            reqs = [CODES[r] for r in unit.get("reqs", []) if r in CODES]
            lost["требование карточки без соответствия"] += [f"{key}: {r}" for r in unit.get("reqs", []) if r not in CODES]
            if not reqs:
                lost["блок без требований, не перенесён"].append(key)
                continue
            kind = {"store": "storage", None: "service"}.get(unit.get("kind"), unit.get("kind"))
            names = unit["params"] if isinstance(unit.get("params"), str) else []
            for item in [] if isinstance(names, str) else unit.get("params") or []:
                names.append(item["name"])
                if item["name"] not in params:
                    extra_params[item["name"]] = item.get("value", "—")
            io = [{"dir": "in" if item.get("dir") == "←" else "out", "with": line(item.get("with", "?"), 120), "what": line(item.get("what", "?"), 200),
                   **({"via": item["via"][0]} if item.get("via") else {})} for item in unit.get("io") or []]
            data = unit["data"] if isinstance(unit.get("data"), str) else [
                {"table": item["table"], "access": item.get("access", "read"), **({"why": line(item["why"], 200)} if item.get("why") else {})}
                for item in unit.get("data") or [] if isinstance(item, dict) and item.get("table")]
            failures = "; ".join(line(f"{f['when']}: {f['then']}", 240) for f in unit.get("failures") or [])
            card = {"id": key, "title": unit["title"], "kind": kind, "does": [line(x, 240) for x in unit.get("does", [])], "tech": plain(unit.get("tech", "")),
                    "stories": [STORY[s] for s in unit.get("stories", []) if s in STORY], "io": io, "data": data, "params": names, "reqs": reqs,
                    "tasks": [str(t) for t in unit.get("tasks", [])], "on_failure": failures or "не задано в источнике", "why": line(unit.get("why", ""), 300)}
            if kind == "ui":
                card["screens"] = [{"path": line(s.get("where", s.get("name", "?")), 160), "shows": line(s.get("what", "?"), 240), "status": s.get("status", "новое"),
                                    **({"operation": line(str(s["api"]), 160)} if s.get("api") else {}), "file": str(s.get("code", "")), "story": STORY.get((s.get("stories") or [""])[0], "")}
                                   for s in unit.get("screens") or []]
            elif kind in ("storage", "config"):
                card["schema_ref"] = line(str(unit.get("schema", "не задано")), 300)
            else:
                card["operations"] = [{"name": line(str(o.get("endpoint") or o.get("op", "?")), 160), "caller": line(str(o.get("who", "?")), 160),
                                       "via": (o.get("via") or ["внутри"])[0]} for o in unit.get("ops") or []]
            path_out = f"blocks/{folder.name}/{path.stem}.yaml"
            write(path_out, card)
            cards[key] = (folder.name, unit, reqs)
    rows = []
    for name, row in params.items():
        rows.append({"name": name, "default": line(row.get("По умолчанию") or "—", 120), "min": line(row.get("Мин") or "—", 80), "max": line(row.get("Макс") or "—", 80), "why": line(row.get("Почему так по умолчанию") or row.get("Что задаёт") or "—", 240)})
    rows += [{"name": n, "default": str(v), "min": "—", "max": "—", "why": "Взято из карточки блока, в таблице параметров спеки нет"} for n, v in extra_params.items()]
    report["params из карточек без строки в спеке"] = len(extra_params)
    write("params.yaml", {"params": rows})
    return cards


def write_functions(cards, table_ids):
    by_story = collections.defaultdict(lambda: {"reads": set(), "writes": set()})
    for folder, unit, _ in cards.values():
        for story in unit.get("stories", []):
            for item in [] if isinstance(unit.get("data"), str) else unit.get("data") or []:
                table = table_ids.get(item.get("table")) if isinstance(item, dict) else None
                if table and item.get("access") in ("read", "write", "read-write"):
                    by_story[story]["writes" if "write" in item["access"] else "reads"].add(table)
    names = {}
    for folder, _, items in EPICS:
        for code, number, unit in items:
            reqs, missing = story_reqs(unit)
            lost["требование истории без соответствия"] += [f"{code}: {m}" for m in missing]
            key = code.lower()
            names[code] = key
            if not reqs:
                lost["история без требований"].append(code)
            obj("functions", key, line(unit["want"], 150), system="icplan" if folder == "icplan" else "agent-platform", reqs=reqs,
                reads=sorted(by_story[code]["reads"]), writes=sorted(by_story[code]["writes"]))
    return names


def write_processes(names, models):
    journeys, number = [], 0
    for path in sorted((DATA / "processes").glob("*.yaml")):
        for process in load(path).get("processes", []):
            number += 1
            lanes = []
            for lane in process.get("lanes", []):
                component = TITLE_TO_COMPONENT.get(lane)
                if component:
                    lanes.append("icplan" if component == "icplan" else "agent-platform")
                else:
                    role = next((ROLE_ID[c] for c, n in PERSONAS["roles"].items() if n == lane), None)
                    if not role:
                        role = slug(lane)
                        if not (ARCH / f"actors/{role}.yaml").exists():
                            obj("actors", role, lane, kind="role")
                    lanes.append(role)
            steps, outputs = [], []
            artifacts = process.get("artifacts", {})
            for step in process.get("steps", []):
                if step.get("type") != "task":
                    continue
                made = [a for a in artifacts.get(step["id"], []) if a in models]
                outputs += [a for a in made if a not in outputs]
                steps.append({"title": line(step["label"], 160), "actor": lanes[step.get("lane", 0)], "inputs": [], "outputs": made})
            if not steps:
                continue
            first = next((s["label"] for s in process["steps"] if s.get("type") == "start"), process["title"])
            key = f"{path.stem}-{slug(process['title'])[:40]}".strip("-")
            actors = sorted({s["actor"] for s in steps if (ARCH / f"actors/{s['actor']}.yaml").exists()})
            obj("processes", key, line(process["title"], 150), trigger=line(first, 200), actors=actors, inputs=[], outputs=outputs, journeys=[f"UJ-{number}"], steps=steps)
            journeys.append((number, process["title"], first))
    return journeys


def write_quality(names):
    rows, services = [], collections.defaultdict(list)
    for index, req in enumerate(NFR_LIST, 1):
        case = req["cases"][0] if req["cases"] else ("нагрузка по профилю", "требование выполнено", "требование выполнено")
        rows.append({"id": f"Q-{index}", "nfr": req["id"], "attribute": "Производительность", "priority": "M", "stimulus": line(case[1], 240),
                     "response": line(case[2], 240), "response_measure": line(case[2], 240), "fitness": "нагрузочный тест, способ уточнить"})
        services[SPEC_COMPONENT[req["spec"]]].append({"text": line(case[2], 160), "quality": f"Q-{index}"})
    write("quality.yaml", {"scenarios": rows})
    story_folder = {"icplan": "icplan"}
    for component, objectives in services.items():
        functions = [names[code] for folder, _, items in EPICS if folder == component for code, _, _ in items]
        system = "icplan" if component == "icplan" else "agent-platform"
        if functions:
            obj("services", f"svc-{component}", f"Сервис {COMPONENTS[component]['name']}", consumers=[ROLE_ID["П"], ROLE_ID["А"]], provider=system, functions=functions, objectives=objectives)
    obj("nodes", "k3s-node", "Узел k3s", environment="production", runs=[k for k in COMPONENTS], tech="k3s")
    (ARCH / "domains.yaml").write_text("""domains:
- {domain: аутентификация, status: decided, rule: AD-7}
- {domain: права, status: decided, rule: AD-6}
- {domain: данные, status: decided, rule: AD-4}
- {domain: ошибки, status: question, note: 'При переносе нет единого решения, правила разбросаны по спекам'}
- {domain: логи, status: decided, rule: AD-12}
- {domain: настройки, status: decided, rule: AD-9}
- {domain: развёртывание, status: decided, rule: AD-15}
- {domain: резервное копирование, status: question, note: 'Описано по хранилищам, единого решения нет'}
- {domain: наблюдаемость, status: decided, rule: AD-12}
- {domain: миграции, status: decided, rule: AD-22}
""", encoding="utf-8", newline="\n")


def write_tasks():
    ids = sorted({p.name.split("-")[0] for p in (SRC / "docs" / "tasks").glob("*.md")})
    write("tasks.yaml", {"tasks": ids})
    report["tasks.yaml"] -= 1
    report["задач"] = len(ids)


def write_prd(journeys):
    parts = [f"---\ntitle: {TITLE}\nstatus: draft\ncreated: {DATE}\nupdated: {DATE}\n---\n\n# PRD: {TITLE}\n\n> Перенесено из `agent-architecture` скриптом `tools/migrate.py`. Код требования в исходных спеках указан у каждого FR.\n\n## 0. Document Purpose\n\nДокумент для владельца продукта, архитектора и разработчиков. Требования сгруппированы по исходным спекам и пронумерованы сквозным образом.\n"]
    proposal = (SRC / "openspec/changes/define-agent-platform/proposal.md").read_text(encoding="utf-8")
    why = re.search(r"## Why\s+(.*?)\n## ", proposal, re.S)
    parts.append(f"## 1. Vision\n\n{clean(why.group(1)) if why else 'Агентная платформа выполняет задачи трекера ICPlan.'}\n")
    roles = "\n".join(f"- **{item['name']}:** {clean(item.get('wants', ''))}." for item in PERSONAS["personas"].values())
    paths = "\n".join(f"- **UJ-{n}. {clean(title)}.** Начало: {clean(start)}." for n, title, start in journeys)
    parts.append(f"## 2. Target User\n\n### 2.1 Jobs To Be Done\n\n{roles}\n\n### 2.2 Key User Journeys\n\n{paths}\n")
    terms = [f"- **{u['name']}** — {line(u.get('desc', ''), 240)}" for u in COMPONENTS.values()]
    terms += [f"- **{name}** — {line(unit.get('purpose', ''), 200)}" for name, unit in units("models").items()]
    parts.append("## 3. Glossary\n\n" + "\n".join(terms) + "\n")
    parts.append("## 4. Features\n")
    for index, (spec, (purpose, reqs)) in enumerate(SPEC_DATA.items(), 1):
        parts.append(f"### 4.{index} {spec}\n\n**Description:** {clean(purpose)}\n\n**Functional Requirements:**\n")
        for req in [r for r in FR_LIST if r["spec"] == spec]:
            cases = "\n".join(f"- {clean(n)}: когда {clean(w)}, тогда {clean(t)}." for n, w, t in req["cases"])
            parts.append(f"#### {req['id']}: {clean(req['title'])}\n\n{clean(req['text'])}\n\nКод в исходной спеке: `{req['code'] or 'нет'}`.\n\n**Consequences (testable):**\n{cases}\n")
    questions = []
    for path in sorted(p for p in (SRC / "openspec/changes").rglob("open-questions.md") if "archive" not in p.parts):
        questions += [line(row.get("Вопрос", "")) for row in table_rows(path.read_text(encoding="utf-8"), "| ID |") if row.get("ID") not in ("—", None)]
    numbered = "\n".join(f"{i}. {q.rstrip('?.')}?" for i, q in enumerate(questions, 1)) or "Открытых вопросов в спеках нет."
    nfrs = "\n".join(f"- **{r['id']} {clean(r['title'])} ({r['spec']}):** {clean(r['text'])}" for r in NFR_LIST)
    parts.append(f"## 5. Non-Goals (Explicit)\n\nСм. раздел Deferred архитектуры.\n\n## 6. MVP Scope\n\nСм. `docs/migration.md`.\n\n## 7. Success Metrics\n\nВ исходных спеках метрик продукта в формате SM нет, их нужно задать.\n\n## 8. Cross-Cutting NFRs\n\n{nfrs}\n\n## 9. Open Questions\n\n{numbered}\n\n## 10. Assumptions Index\n\nДопущений в спеках не отмечено.\n")
    path = PLAN / f"prds/prd-{NAME}-{DATE}/prd.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8", newline="\n")


def write_epics():
    coverage, parts = [], []
    for folder, number, items in EPICS:
        title = COMPONENTS.get(folder, {}).get("name", folder)
        parts.append(f"## Epic {number}: {title}\n\n{line(COMPONENTS.get(folder, {}).get('desc', ''))}\n")
        spec_nfrs = [r["id"] for r in NFR_LIST if SPEC_COMPONENT[r["spec"]] == folder]
        for position, (code, story, unit) in enumerate(items):
            reqs, _ = story_reqs(unit)
            coverage += [(req, story) for req in reqs]
            nfr = f"\nНагрузка: {', '.join(spec_nfrs)}.\n" if spec_nfrs and position == 0 else ""
            role = PERSONAS["roles"].get(unit.get("role"), unit.get("role", "пользователь"))
            criteria = []
            for item in unit.get("accept", []):
                given, sep, then = clean(str(item)).partition("→")
                criteria.append(f"**Given** {given.strip()}\n**When** выполняется сценарий\n**Then** {then.strip()}" if sep else f"**Given** работает {title}\n**When** выполняется сценарий\n**Then** {given.strip()}")
            joined = "\n\n".join(criteria)
            parts.append(f"### Story {story}: {line(unit['want'], 120)}\n\nAs a {role},\nI want {clean(unit['want'])},\nSo that {clean(unit.get('so_that', ''))}.\n\nКод в источнике: {code}. Требования: {', '.join(reqs) or 'нет'}.{nfr}\n**Acceptance Criteria:**\n\n{joined}\n")
    table = "\n".join(f"| {k} | {v} |" for k, v in sorted(set(coverage), key=lambda p: (int(p[0].split("-")[1]), p[1])) if k.startswith("FR-"))
    text = f"---\nstatus: draft\n---\n\n# {TITLE} - Epic Breakdown\n\n## Overview\n\nИстории перенесены из `data/stories`, эпик соответствует компоненту.\n\n## Requirements Inventory\n\nFR-1 — FR-{len(FR_LIST)}, формулировки в PRD.\n\n### FR Coverage Map\n\n| FR | История |\n| --- | --- |\n{table}\n\n## Epic List\n\n" + "\n".join(f"{n}. {COMPONENTS.get(f, {}).get('name', f)}" for f, n, _ in EPICS) + "\n\n" + "\n".join(parts)
    (PLAN / "epics.md").write_text(text, encoding="utf-8", newline="\n")
    report["FR без истории"] = len(FR_LIST) - len({k for k, _ in coverage if k.startswith("FR-")})


def decisions():
    text = (SRC / "openspec/changes/define-agent-platform/design.md").read_text(encoding="utf-8")
    found = []
    for match in re.finditer(r"^### D(\d+)\. (.+?)\n(.*?)(?=^##+ |\Z)", text, re.M | re.S):
        found.append((int(match.group(1)), match.group(2), match.group(3)))
    return sorted(found)


def write_spine():
    items = []
    for number, title, body in decisions():
        codes = sorted({CODES[c] for c in re.findall(r"\bR-[A-Z]+-\d+\b", body) if c in CODES}, key=lambda x: (x[0], int(x.split("-")[1])))
        rule = line(body, 700) or line(title)
        items.append(f"### AD-{number} — {clean(title)}\n\n- **Binds:** {', '.join(codes) or 'all'}\n- **Prevents:** отход реализации от решения «{clean(title)}»\n- **Rule:** {rule}\n")
    source = load(DATA / "integrations.yaml")
    edges = sorted({(u["from"], u["to"]) for u in source.values() if u["from"] in COMPONENTS and u["to"] in COMPONENTS})
    graph = "\n".join(f"  {a} --> {b}" for a, b in edges)
    stack = []
    for row in table_rows((SRC / "docs/TECHNOLOGIES.md").read_text(encoding="utf-8"), "| Технология |"):
        name, version = clean(row.get("Технология", "")), clean(row.get("Версия", ""))
        if name and version:
            stack.append(f"| {name} | {version} |")
    stack = list(dict.fromkeys(stack))
    binds = ", ".join(r["id"] for r in FR_LIST + NFR_LIST)
    rows = []
    for spec in SPEC_DATA:
        reqs = [r["id"] for r in FR_LIST + NFR_LIST if r["spec"] == spec]
        if reqs:
            rows.append(f"| {', '.join(reqs)} | `{SPEC_COMPONENT[spec]}` | см. решения AD |")
    design = (SRC / "openspec/changes/define-agent-platform/design.md").read_text(encoding="utf-8")
    goals = re.search(r"\*\*Non-Goals:?\*\*(.*?)(?=\n## )", design, re.S)
    deferred = [clean(x) for x in re.findall(r"^- (.+)$", goals.group(1), re.M)] if goals else []
    deferred = deferred or ["Единое решение по ошибкам и резервному копированию: см. таблицу доменов."]
    naming = line(load(DATA / "datamodel.yaml").get("naming", ""), 300)
    text = f"""---
name: '{TITLE}'
type: architecture-spine
purpose: build-substrate
altitude: feature
paradigm: 'платформа агентов рядом с трекером ICPlan, запуск в одноразовой изолированной среде'
scope: 'Agent Platform и её интеграция с ICPlan'
status: final
created: '{DATE}'
updated: '{DATE}'
binds: [{binds}]
sources:
  - _bmad-output/planning-artifacts/prds/prd-{NAME}-{DATE}/prd.md
companions: []
---

# Architecture Spine — {TITLE}

> Перенесено из `agent-architecture`. Источник правды теперь YAML в `docs/architecture`.

## Design Paradigm

ICPlan хранит задачи и процесс. Agent Runner забирает запуск, готовит изолированную среду, Harness ведёт цикл агента, Guardrails проверяют действия, итог возвращается в задачу.

## Invariants & Rules

```mermaid
graph TD
{graph}
```

Стрелка значит «может обращаться». Связи взяты из реестра интеграций.

{chr(10).join(items)}
## Consistency Conventions

| Concern | Convention |
| --- | --- |
| Именование | {naming} |

## Stack

| Name | Version |
| --- | --- |
{chr(10).join(stack)}

## Structural Seed

Контейнеры и хранилища описаны в модели системы, см. `docs/architecture`.

## Capability → Architecture Map

| Capability / Area | Lives in | Governed by |
| --- | --- | --- |
{chr(10).join(rows)}

## Deferred

{chr(10).join('- ' + d for d in deferred)}
"""
    path = PLAN / f"architecture/architecture-{NAME}-{DATE}/ARCHITECTURE-SPINE.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_docmost():
    views = [("Панель готовности", "readiness"), ("C1: система и окружение", "c1"), ("C2: контейнеры", "c2"), ("C3: блоки", "c3"), ("Как работает", "how"),
             ("Карточки блоков", "cards"), ("Данные", "data"), ("Реестры", "registers"), ("Матрица покрытия", "coverage")]
    tree = [{"title": "Как читать проект", "source": "docs/index.md"}, {"title": "Обзор системы", "children": [{"title": t, "view": v} for t, v in views]},
            {"title": "Документы", "children": [{"title": "PRD", "source": f"_bmad-output/planning-artifacts/prds/prd-{NAME}-{DATE}/prd.md"},
                                               {"title": "Architecture Spine", "source": f"_bmad-output/planning-artifacts/architecture/architecture-{NAME}-{DATE}/ARCHITECTURE-SPINE.md"},
                                               {"title": "Эпики и истории", "source": "_bmad-output/planning-artifacts/epics.md"}, {"title": "Отчёт о переносе", "source": "docs/migration.md"}]}]
    config = {"url": "http://localhost:3100", "credentials": "../docmost-stack/admin-credentials.txt",
              "space": {"name": TITLE, "slug": "agent-tasktracker-max", "description": "Агентная платформа в новой структуре документации"}, "tree": tree}
    (ROOT / "docmost.yaml").write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")


def write_map():
    rows = {req["code"]: req["id"] for req in FR_LIST + NFR_LIST if req["code"]}
    (ROOT / "docs" / "requirements-map.yaml").write_text(yaml.safe_dump(rows, sort_keys=True), encoding="utf-8", newline="\n")
    counts = "\n".join(f"| {k} | {v} |" for k, v in sorted(report.items()))
    gaps = "\n".join(f"| {k} | {len(v)} | {', '.join(map(str, v[:8]))}{' …' if len(v) > 8 else ''} |" for k, v in sorted(lost.items())) or "| нет | 0 | |"
    (ROOT / "docs" / "migration.md").write_text(f"""# Отчёт о переносе

Источник: `agent-architecture`. Перенос выполнил `tools/migrate.py`. Требований: {len(FR_LIST)} FR и {len(NFR_LIST)} NFR, историй: {len(STORY)}, решений: {len(decisions())}.

## Что получилось

| Что | Сколько |
| --- | --- |
{counts}

## Что не перенеслось чисто

| Что | Сколько | Примеры |
| --- | --- | --- |
{gaps}

## Что создано автоматически и требует разбора

- Поле `prevents` у решений заполнено общей фразой: в источнике его нет.
- Правило решения это начало текста решения из `design.md`.
- Сценарии качества выведены из требований о нагрузке, поле проверки нужно уточнить.
- Домены отмечены по названиям решений.
- Критерии историй приведены к Given, When, Then по стрелке в исходной строке.
- Шаги процессов взяты из задач схем, входы шагов не заполнены.

Соответствие старых и новых кодов лежит в `docs/requirements-map.yaml`.
""", encoding="utf-8", newline="\n")
    (ROOT / "docs" / "index.md").write_text(f"""# Как читать проект

{TITLE}: агентная платформа, которая выполняет задачи трекера ICPlan. Проект перенесён из `agent-architecture` в новую структуру документации и правится здесь.

| Что | Где |
| --- | --- |
| Требования | PRD |
| Решения | Architecture Spine, источник `docs/architecture/decisions` |
| Устройство системы | `docs/architecture` |
| Истории | Эпики |
| Качество | `_quality/check-report.yaml` |
| Что требует разбора | Отчёт о переносе |
""", encoding="utf-8", newline="\n")


tables, table_ids, models, params = write_model()
cards = write_blocks(table_ids, params)
names = write_functions(cards, table_ids)
journeys = write_processes(names, models)
write_quality(names)
write_tasks()
write_prd(journeys)
write_epics()
write_spine()
write_docmost()
write_map()
print(dict(report))
print({k: len(v) for k, v in lost.items()})
