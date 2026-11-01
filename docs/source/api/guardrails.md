# Интеграции: Guardrails (OPA)

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> `http://opa:8181`</div>
<div><span class="about-label">Аутентификация</span> внутренняя сеть (mTLS — этап 4)</div>
</div>

## Решения

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `/v1/data/agent/g1` | <span class="st st-ok">✅ есть</span> | допуск запуска (`PolicyInput` → `PolicyDecision`) | Agent Runner · сеть | US-GRD-03 | FR-111 | I5 |
| <span class="m m-post">POST</span> | `/v1/data/agent/g2` | <span class="st st-ok">✅ есть</span> | проверка действия агента | Harness · сеть | US-GRD-06, US-HAR-02 | FR-112 | I10 |
| <span class="m m-get">GET</span> | `/health?bundles` | <span class="st st-ok">✅ есть</span> | готовность и версия бандла | Kubernetes · — | US-GRD-01 | FR-116 | I16 |
