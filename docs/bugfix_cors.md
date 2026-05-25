# Исправление ошибки парсинга CORS_ORIGINS

## Описание ошибки
При запуске тестов или приложения происходила ошибка:
`pydantic_settings.exceptions.SettingsError: error parsing value for field "cors_origins" from source "DotEnvSettingsSource"`

Это происходило из-за того, что в файле `.env` переменная `CORS_ORIGINS` была установлена в `*`, а в `app/core/config.py` поле `cors_origins` имело тип `list[str]`. По умолчанию `pydantic-settings` пытается распарсить значения сложных типов (таких как списки) из переменных окружения как JSON. Так как `*` не является валидным JSON, происходил сбой парсинга до запуска валидаторов Pydantic.

## Что сделано
1. В [config.py](file:///C:/Antigravity/backend-template/app/core/config.py) тип поля `cors_origins` изменен на `list[str] | str`. Это позволяет `pydantic-settings` успешно считывать строковое значение из файла `.env` / переменных окружения.
2. Добавлен `@field_validator("cors_origins", mode="before")`, который преобразует строку (например, разделенную запятыми или просто `*`) в список строк `list[str]`.
3. Успешно запущены тесты `pytest` и статический анализатор `mypy` / линтер `ruff`. Все проверки проходят успешно.
