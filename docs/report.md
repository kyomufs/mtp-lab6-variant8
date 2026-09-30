# Отчёт по лабораторной работе №6

Самодуров Матвей Николаевич, группа 221341, вариант 8.

## Средняя сложность

- **№4 Страница с таблицей данных** — `lab6/table_app.py`: фабрика
  `create_app(rows)` создаёт Flask-приложение с маршрутом `GET /`,
  который рендерит Jinja2-шаблон `lab6/templates/table.html`.
  Заголовки таблицы берутся из ключей первого словаря списка, каждая
  строка данных становится строкой `<tr>`; пустой (или не переданный)
  список даёт пустую таблицу с надписью «No rows to display».
  Тесты ходят в страницу через `app.test_client()`.
- **№8 FastAPI принимает параметр и отвечает** — `lab6/param_api.py`:
  приложение `FastAPI` с маршрутом `GET /greet?name=...`; параметр
  объявлен как `Query(min_length=1)`, поэтому до обработчика доходят
  только непустые имена. Ответ — JSON
  `{"greeting": "Hello, <name>!"}`, отсутствующее или пустое имя
  отклоняется валидатором FastAPI со статусом 422.
- **№10 Простейший REST API списка задач** — `lab6/tasks_api.py`:
  приложение `FastAPI` и словарь `TASKS: dict[int, Task]` как
  in-memory хранилище. Маршруты: `GET /tasks` (список по возрастанию
  id), `POST /tasks` (201, идентификатор считается как `max(id) + 1`),
  `GET /tasks/{task_id}` и `PATCH /tasks/{task_id}` (404, если задачи
  нет), `PATCH /tasks/{task_id}/toggle` (флаг `done`),
  `DELETE /tasks/{task_id}` (204/404). Тела запросов и ответов
  описываются моделями Pydantic из `lab6/schemas.py`.

## Повышенная сложность

- **№8 Использование Pydantic-схем** — `lab6/schemas.py`: модели
  Pydantic v2 `TaskCreate` (`title` длиной 1–100, `priority` 1–5,
  `due_date: datetime | None`), `Task` (наследует `TaskCreate`,
  добавляет `id` и `done`) и `TaskUpdate` (все поля необязательны).
  `field_validator` приводит заголовок через `strip()` и отклоняет
  строку, пустую после strip; `model_validator(mode="after")`
  запрещает обновление, в котором не указано ни одного поля.
  `tasks_api.py` использует именно эти схемы (422 при нарушении).
- **№1 Flask с базой SQLite (CRUD)** — `lab6/flask_sqlite.py`:
  фабрика `create_app(db_path)` (по умолчанию `":memory:"`) открывает
  одно соединение `sqlite3` на всё время жизни приложения — иначе
  in-memory база исчезала бы между запросами. Таблица `items`
  создаётся при первом обращении: `CREATE TABLE IF NOT EXISTS`
  выполняется в контекстном менеджере соединения, который фиксирует
  транзакцию. Маршруты: `GET /items` (JSON-список), `POST /items`
  (201), `PUT /items/<int:item_id>` (200/404),
  `DELETE /items/<int:item_id>` (204/404); ошибки тела запроса
  обработчиком `ValueError` превращаются в 400. Соединение закрывается
  через `contextlib.closing` в `close_db(app)` — отдельный тест
  проверяет, что после закрытия запросы к базе падают с
  `sqlite3.ProgrammingError`.

## Проверки

Команды выполнялись из каталога репозитория; `python3` в PATH нет,
поэтому всё запускается через `uv`.

### Тесты

```bash
uv run --with flask --with fastapi --with httpx --with flake8 \
  python -m unittest discover -s tests -v
```

Вывод команды (реальный stdout/stderr):

```text
/home/kyomufs/.cache/uv/archive-v0/SVjYXrb9zkOjZcm2/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa
test_connection_closes_with_context_manager (test_flask_sqlite.FlaskSqliteTests.test_connection_closes_with_context_manager)
``contextlib.closing`` releases the SQLite connection. ... ok
test_create_returns_201_and_item_appears_in_list (test_flask_sqlite.FlaskSqliteTests.test_create_returns_201_and_item_appears_in_list)
A valid body creates an item visible to later GETs. ... ok
test_create_without_json_body_returns_400 (test_flask_sqlite.FlaskSqliteTests.test_create_without_json_body_returns_400)
A non-object body is answered with HTTP 400. ... ok
test_create_without_name_returns_400 (test_flask_sqlite.FlaskSqliteTests.test_create_without_name_returns_400)
A missing or blank ``name`` is answered with HTTP 400. ... ok
test_delete_returns_204_then_404 (test_flask_sqlite.FlaskSqliteTests.test_delete_returns_204_then_404)
Deleting removes the row; a second delete fails. ... ok
test_empty_database_returns_empty_list (test_flask_sqlite.FlaskSqliteTests.test_empty_database_returns_empty_list)
A fresh database answers with HTTP 200 and ``[]``. ... ok
test_file_database_keeps_data_between_apps (test_flask_sqlite.FlaskSqliteTests.test_file_database_keeps_data_between_apps)
A file path stores rows outside the process memory. ... ok
test_table_is_created_on_first_access (test_flask_sqlite.FlaskSqliteTests.test_table_is_created_on_first_access)
The items table appears only after the first request. ... ok
test_update_missing_item_returns_404 (test_flask_sqlite.FlaskSqliteTests.test_update_missing_item_returns_404)
Updating an unknown identifier fails with HTTP 404. ... ok
test_update_replaces_item_fields (test_flask_sqlite.FlaskSqliteTests.test_update_replaces_item_fields)
PUT answers with 200 and stores the new values. ... ok
test_empty_name_returns_422 (test_param_api.ParamApiTests.test_empty_name_returns_422)
An empty ``name`` violates ``min_length=1``: 422. ... ok
test_greet_returns_greeting (test_param_api.ParamApiTests.test_greet_returns_greeting)
A valid name is embedded into the greeting. ... ok
test_missing_name_returns_422 (test_param_api.ParamApiTests.test_missing_name_returns_422)
A request without ``name`` fails validation with 422. ... ok
test_non_ascii_name_is_supported (test_param_api.ParamApiTests.test_non_ascii_name_is_supported)
Non-ASCII names are passed through unchanged. ... ok
test_blank_title_is_rejected (test_schemas.TaskCreateTests.test_blank_title_is_rejected)
A title that strips to nothing raises a validation error. ... ok
test_due_date_accepts_a_future_datetime (test_schemas.TaskCreateTests.test_due_date_accepts_a_future_datetime)
An explicit deadline is stored as a datetime value. ... ok
test_priority_out_of_range_is_rejected (test_schemas.TaskCreateTests.test_priority_out_of_range_is_rejected)
Priorities outside the 1..5 range are rejected. ... ok
test_valid_payload_is_accepted (test_schemas.TaskCreateTests.test_valid_payload_is_accepted)
A well-formed payload keeps its normalized values. ... ok
test_task_adds_id_and_done_flag (test_schemas.TaskTests.test_task_adds_id_and_done_flag)
Stored tasks carry the server id and the status flag. ... ok
test_task_inherits_creation_constraints (test_schemas.TaskTests.test_task_inherits_creation_constraints)
The stored model keeps the validation of its payload. ... ok
test_blank_title_is_rejected (test_schemas.TaskUpdateTests.test_blank_title_is_rejected)
Updates validate the title exactly like creation does. ... ok
test_empty_update_is_rejected (test_schemas.TaskUpdateTests.test_empty_update_is_rejected)
A payload that changes nothing raises a validation error. ... ok
test_explicit_null_due_date_is_allowed (test_schemas.TaskUpdateTests.test_explicit_null_due_date_is_allowed)
Clearing the deadline counts as a meaningful update. ... ok
test_partial_payload_is_accepted (test_schemas.TaskUpdateTests.test_partial_payload_is_accepted)
Only the provided fields are marked as set. ... ok
test_cell_values_are_rendered (test_table_app.TableAppTests.test_cell_values_are_rendered)
Every row value appears in its own table cell. ... ok
test_empty_list_shows_note (test_table_app.TableAppTests.test_empty_list_shows_note)
An empty row list renders an empty table with a note. ... ok
test_headers_come_from_first_row_keys (test_table_app.TableAppTests.test_headers_come_from_first_row_keys)
Table headers are the keys of the first dictionary. ... ok
test_index_returns_200 (test_table_app.TableAppTests.test_index_returns_200)
The index page answers with HTTP 200. ... ok
test_missing_rows_default_to_empty_table (test_table_app.TableAppTests.test_missing_rows_default_to_empty_table)
Calling the factory without rows still serves a page. ... ok
test_blank_title_returns_422 (test_tasks_api.TasksApiTests.test_blank_title_returns_422)
A title that strips to nothing fails with HTTP 422. ... ok
test_create_returns_201_and_assigns_id (test_tasks_api.TasksApiTests.test_create_returns_201_and_assigns_id)
A valid payload is stored and answered with HTTP 201. ... ok
test_delete_returns_204_then_404 (test_tasks_api.TasksApiTests.test_delete_returns_204_then_404)
Deleting removes the task; a second delete fails. ... ok
test_get_missing_task_returns_404 (test_tasks_api.TasksApiTests.test_get_missing_task_returns_404)
Unknown identifiers are answered with HTTP 404. ... ok
test_invalid_priority_returns_422 (test_tasks_api.TasksApiTests.test_invalid_priority_returns_422)
Pydantic rejects priorities outside 1..5 with 422. ... ok
test_list_returns_created_tasks (test_tasks_api.TasksApiTests.test_list_returns_created_tasks)
Created tasks are listed in identifier order. ... ok
test_patch_updates_only_given_fields (test_tasks_api.TasksApiTests.test_patch_updates_only_given_fields)
PATCH changes the provided fields and keeps the rest. ... ok
test_toggle_flips_done_flag (test_tasks_api.TasksApiTests.test_toggle_flips_done_flag)
The toggle route flips the ``done`` flag on every call. ... ok
test_toggle_missing_task_returns_404 (test_tasks_api.TasksApiTests.test_toggle_missing_task_returns_404)
Toggling an unknown task fails with HTTP 404. ... ok

----------------------------------------------------------------------
Ran 38 tests in 0.112s

OK
```

Первая строка — предупреждение сторонней библиотеки (Starlette
переиспользует `fastapi.testclient`), на результат проверок оно не
влияет.

### Стиль кода

```bash
uv run --with flask --with fastapi --with httpx --with flake8 \
  flake8 lab6 tests && echo "flake8: clean, exit code 0"
```

Вывод команды (реальный):

```text
flake8: clean, exit code 0
```

### Демонстрация

```bash
uv run --with flask --with fastapi --with httpx python -m lab6
```

Вывод команды (реальный; сетевые порты не открываются):

```text
Medium tasks
table_app GET / -> 200
  contains cell 'alpha': True
param_api GET /greet?name=Ada -> {'greeting': 'Hello, Ada!'}
tasks_api POST /tasks -> 201
tasks_api GET /tasks -> [{'title': 'write report', 'priority': 3, 'due_date': None, 'id': 1, 'done': False}]
Advanced tasks
schemas: blank title rejected -> Value error, title must not be blank
flask_sqlite POST /items -> 201
flask_sqlite GET /items -> [{'id': 1, 'name': 'notebook', 'quantity': 2}]
Start the real servers with (ports are NOT opened here):
  uv run --with fastapi --with uvicorn \
    uvicorn lab6.param_api:app --reload
  uv run --with fastapi --with uvicorn \
    uvicorn lab6.tasks_api:app --reload
  uv run --with flask flask --app lab6.table_app run
```

### CI

- GitHub Actions workflow `.github/workflows/python-checks.yml`:
  матрица версий Python `["3.12", "3.13"]`, шаги — установка
  зависимостей из `requirements-dev.txt`, `flake8 lab6 tests`,
  `python -m compileall -q lab6 tests`,
  `python -m unittest discover -s tests -v`.
