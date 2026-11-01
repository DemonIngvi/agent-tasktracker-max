# guardrails — схема

← spec.md

Схема C3 по FORMAT.md. Цвет: зелёный — есть, жёлтый — частично, серый — не начато; оранжевый пунктир — соседний компонент.

## Схема

```mermaid
flowchart TB
  classDef done fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
  classDef part fill:#fff8e1,stroke:#f9a825,color:#5d4037
  classDef todo fill:#f5f5f5,stroke:#9e9e9e,color:#424242
  classDef ext fill:#fff3e0,stroke:#ef6c00,color:#e65100,stroke-dasharray:4 3
  classDef user fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
  classDef store fill:#ede7f6,stroke:#5e35b1,color:#311b92
  classDef back fill:#fafafa,stroke:#bdbdbd,color:#9e9e9e,stroke-dasharray:2 2
  classDef zone fill:#fafafa,stroke:#9fa8da,color:#1a237e
  b1[("<b>Rego в git</b><br/><small>логика правил, opa test</small>")]:::store
  b2["<b>Данные правил</b><br/><small>allowlist, лимиты · Platform module</small>"]:::ext
  b3[("<b>Конфиг деплоя</b><br/><small>guardrails.gN.enabled, on_engine_error</small>")]:::store
  b4["<b>OPA</b><br/><small>движок решений G1 / G2</small>"]:::part
  b1 --> b4
  subgraph z5["Точки применения"]
    b6["<b>G1 Admission [G1]</b><br/><small>Agent Runner: допуск, бюджет</small>"]:::ext
    b7["<b>G2 Action [G2]</b><br/><small>Harness hooks: тулы, память, approve</small>"]:::ext
    b8["<b>G3 Isolation [G3]</b><br/><small>Sandbox: сеть, ФС, ресурсы</small>"]:::ext
    b9["<b>G4 LLM [G4]</b><br/><small>LiteLLM: PII, injection, модерация</small>"]:::ext
  end
  class z5 zone
  b4 -->|"решения allow / deny / confirm"| b6
  b4 ~~~ b7
  b4 ~~~ b8
  b4 ~~~ b9
  b10["<b>Аудит</b><br/><small>каждое срабатывание с run_id</small>"]:::ext
  b6 --> b10
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Rego в git | логика правил, opa test | ⬜ не начато |
| Конфиг деплоя | guardrails.gN.enabled, on_engine_error | ⬜ не начато |
| OPA | движок решений G1 / G2 | ⚠️ частично |

## Настройка

Параметры модуля — [interfaces.md](guardrails-interfaces.md) (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Безопасность настраивается и проверяется, а не размазана по коду | Rego сложнее читать — шаблоны правил и тесты на каждое. |
| Понятно, почему агенту отказали (аудит) | OPA недоступен — `on_engine_error: deny`. |
| Опасные действия ждут человека | Пересмотр: появится официальная Python-библиотека Cedar и правила станут чисто ролевыми. |

Обоснование: [R&D](..\..\..\..\research\guardrails-engine.md).
