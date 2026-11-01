# agent-sandbox — схема

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
  b1["<b>Agent Runner</b><br/><small>claim / destroy</small>"]:::ext
  b2["<b>Тёплый пул</b><br/><small>N готовых контейнеров на профиль</small>"]:::todo
  b3["<b>SandboxProvider</b><br/><small>Docker сейчас · K8s позже</small>"]:::todo
  b1 --> b2
  b1 ~~~ b3
  subgraph z4["Контейнер запуска [G3]"]
    b5["<b>Harness</b><br/><small>агентский цикл</small>"]:::ext
    b6[("<b>/workspace</b><br/><small>эфемерный, клон репозиториев</small>")]:::store
    b7["<b>Профиль</b><br/><small>CPU, RAM, диск, без privileged</small>"]:::todo
    b8["<b>Credential helper</b><br/><small>токены git без env</small>"]:::todo
    b5 --> b7
    b5 ~~~ b8
  end
  class z4 zone
  b2 -->|"один контейнер = один запуск"| b5
  b2 ~~~ b6
  b9["<b>Egress-прокси [G3]</b><br/><small>Squid: allowlist по подсети — среда агента и шаг подготовки</small>"]:::todo
  b7 -->|"весь исходящий трафик"| b9
  b10["<b>LiteLLM gateway</b>"]:::ext
  b11["<b>Memory</b>"]:::ext
  b12["<b>Реестры пакетов</b><br/><small>только шаг подготовки</small>"]:::ext
  b9 -->|"MCP — только через Agent Runner (AD-19)"| b10
  b9 ~~~ b11
  b9 ~~~ b12
```

## Блоки

| Блок | Задача | Статус |
|---|---|---|
| Тёплый пул | N готовых контейнеров на профиль | ⬜ не начато |
| SandboxProvider | Docker сейчас · K8s позже | ⬜ не начато |
| /workspace | эфемерный, клон репозиториев | ⬜ не начато |
| Профиль | CPU, RAM, диск, без privileged | ⬜ не начато |
| Credential helper | токены git без env | ⬜ не начато |
| Egress-прокси | Squid: allowlist по подсети — среда агента и шаг подготовки | ⬜ не начато |

## Настройка

Параметры модуля — [interfaces.md](agent-sandbox-interfaces.md) (раздел «Параметры модуля»); на сайте — вкладка «Deploy» компонента, раздел «Конфигурация».

## Плюсы / минусы

| ➕ | ➖ |
|---|---|
| Сбой или атака в одном запуске не задевает другие и хост | Побег из контейнера через ядро — gVisor (проверка в 2.2), rootless, без привилегий. |
| Старт за доли секунды | Пересмотр: агенты запускают код из внешних источников → microVM (Kata, Firecracker), если KVM есть. |
| Секреты не попадают к агенту |  |

Обоснование: [R&D](..\..\..\..\research\sandbox-isolation.md).
