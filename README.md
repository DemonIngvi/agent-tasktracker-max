# Agent TaskTracker Max

Агентная платформа, которая выполняет задачи трекера ICPlan: забирает запуск, готовит изолированную среду, ведёт агента под контролем проверок и возвращает итог в задачу.

Документация перенесена из [agent-architecture](https://github.com/DemonIngvi/agent-architecture) в новую структуру и дальше правится здесь. Исходный репозиторий не менялся.

## Где что лежит

| Папка | Что внутри |
| --- | --- |
| `_bmad-output/planning-artifacts/prds/` | PRD |
| `_bmad-output/planning-artifacts/epics.md` | Эпики и истории |
| `_bmad-output/planning-artifacts/architecture/` | Architecture Spine, собирается из YAML |
| `docs/architecture/` | Источник архитектуры: решения и модель системы |
| `docs/migration.md` | Что перенеслось и что требует разбора |
| `docs/requirements-map.yaml` | Соответствие кодов `R-XXX-NN` и `FR-n` |
| `_quality/check-report.yaml` | Результат проверок |
| `tools/migrate.py` | Скрипт переноса |

## Как работать

```
python ../doc-kit/tools/kit.py sync --root .
uv run .doc-kit/doc-gates/tools/check.py --root .
uv run .doc-kit/doc-architecture/tools/arch.py check docs/architecture --spine <путь к Spine>
```

Spine вручную не правится: меняйте YAML и выполняйте `build`. Правила заполнения находятся в навыке `doc-arch`, порядок работы описан в [doc-rules](https://github.com/DemonIngvi/doc-rules/blob/main/docs/new-project.md).

## Состояние

Проект перенесён автоматически и ещё не вычитан. Открытые проверки показывают реальную работу на ближайшее время, разбор начинается с `docs/migration.md`.
