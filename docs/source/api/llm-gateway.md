# Интеграции: LiteLLM gateway

← компонент · Deploy · методология

<div class="api-head">
<div><span class="about-label">Базовый адрес</span> `http://litellm:4000`</div>
<div><span class="about-label">Аутентификация</span> virtual key агента; админ — master key</div>
</div>

## Модели

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `/v1/chat/completions` | <span class="st st-ok">✅ есть</span> | вызов модели (поля — сборка запроса) | Harness · virtual key | US-HAR-01, US-LLM-01 | FR-21, FR-30, FR-134 | I8 |
| <span class="m m-post">POST</span> | `/key/generate · /key/update` | <span class="st st-ok">✅ есть</span> | virtual key агента с бюджетом и лимитами | Platform module · master key | US-PM-04 | FR-100, FR-138 | I15 |
| <span class="m m-get">GET</span> | `/model/info` | <span class="st st-ok">✅ есть</span> | алиасы `model_list` и их параметры: проверка модели при сохранении агента | Platform module · master key | US-ICP-21 | FR-58 | I15 |
| <span class="m m-get">GET</span> | `/spend/logs` | <span class="st st-ok">✅ есть</span> | затраты по `metadata.run_id` | Observability · master key | US-LLM-03, US-LLM-05 | FR-136 | I14 |

## mock-LLM

| Метод | Путь | Статус | Что делает | Кто вызывает | Истории | Требования | I |
|---|---|---|---|---|---|---|---|
| <span class="m m-post">POST</span> | `/v1/chat/completions` | <span class="st st-new">🆕 новое</span> | скриптовые ответы и вызовы тулов | LiteLLM (алиас `mock`) · — | US-LLM-02 | FR-137 | I13 |
