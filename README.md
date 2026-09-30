# Лабораторная работа №6

Самодуров Матвей Николаевич, группа 221341, вариант 8, лабораторная №6.

## Задания варианта

**Средняя сложность:**

- №4 — страница с таблицей данных (`lab6/table_app.py`)
- №8 — FastAPI принимает параметр и отвечает (`lab6/param_api.py`)
- №10 — простейший REST API списка задач (`lab6/tasks_api.py`)

**Повышенная сложность:**

- №8 — использование Pydantic-схем (`lab6/schemas.py`)
- №1 — Flask с базой SQLite, CRUD (`lab6/flask_sqlite.py`)

## Клонирование

```bash
git clone https://github.com/kyomufs/mtp-lab6-variant8.git
```

## Запуск

Демо без поднятия серверов (только `TestClient`, сетевые порты не
открываются):

```bash
uv run --with flask --with fastapi --with httpx python -m lab6
```

Запуск HTTP-серверов (открывает порт; `Ctrl+C` — остановить):

```bash
uv run --with fastapi --with uvicorn uvicorn lab6.tasks_api:app --reload
uv run --with fastapi --with uvicorn uvicorn lab6.param_api:app --reload
uv run --with flask flask --app lab6.table_app run --debug
```

## Проверки

```bash
uv run --with flask --with fastapi --with httpx --with flake8 \
  python -m unittest discover -s tests -v
uv run --with flask --with fastapi --with httpx --with flake8 \
  flake8 lab6 tests
```

Подробное описание выполнения и вывод команд — в `docs/report.md`.
