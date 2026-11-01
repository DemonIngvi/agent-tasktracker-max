# Замечания: Sandbox

← компонент · подтверждения документов · правило

## Перепроверка (пачка, Haiku, 13.10.2026)

| № | Документ | Роли | Отклонение | Как закрыть | Где | Методология | Статус |
|---|---|---|---|---|---|---|---|
| Z-SBX-1 | docs/api/sandbox.md | Р | контракта sandbox и имён настроек CPU, памяти, диска по профилю нет: `resources` в interfaces.md agent-sandbox описан словами (в списке 73 параметров без формального типа) | открытый вопрос спеки → тип и поля `resources` (cpu, memory, disk) с диапазонами | interfaces.md agent-sandbox, профиль sandbox | да → yaml-check: значение параметра по типу из interfaces.md | ✅ тип resources (cpu, memory_mb, disk_gb) в interfaces.md agent-sandbox, раздел «Тип resources»; параметры resources.* |
