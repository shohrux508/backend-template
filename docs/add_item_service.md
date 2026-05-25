# Добавление CRUD-сервиса Item (Товары)

В проект добавлен первый сервис бизнес-логики для работы с сущностью `Item`.

## Что сделано:
1. **Слой данных (Database):**
   - Добавлена ORM-модель `Item` в [models.py](file:///C:/Antigravity/backend-template/app/database/models.py) со свойствами `id`, `title`, `description`, `created_at` и `updated_at`.
   - Модель экспортирована в [__init__.py](file:///C:/Antigravity/backend-template/app/database/__init__.py).

2. **Бизнес-логика (Services):**
   - Создан класс `ItemService` и Pydantic-схемы (`ItemCreate`, `ItemUpdate`, `ItemResponse`) в [item.py](file:///C:/Antigravity/backend-template/app/services/item.py).
   - Сервис экспортирован в [__init__.py](file:///C:/Antigravity/backend-template/app/services/__init__.py).

3. **Слой API (Endpoints):**
   - Создан API роутер с CRUD-эндпоинтами (`GET`, `POST`, `PUT`, `DELETE`) в [items.py](file:///C:/Antigravity/backend-template/app/api/v1/items.py).
   - Роутер зарегистрирован в [container.py](file:///C:/Antigravity/backend-template/app/core/container.py).

4. **Миграция БД:**
   - Сгенерирована и успешно применена асинхронная миграция Alembic: `791a0d6a865b_add_item_model.py`.

5. **Тестирование и проверка качества:**
   - Написаны интеграционные тесты в [test_items.py](file:///C:/Antigravity/backend-template/tests/test_items.py) с использованием `pytest`.
   - Пройден конвейер проверок качества `scripts/run_checks.py` (тесты, типы mypy, форматирование и линтинг ruff).
