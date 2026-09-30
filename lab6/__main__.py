"""Demo entry point: run ``python -m lab6``.

No network port is opened: FastAPI applications are called through
``fastapi.testclient.TestClient`` and Flask applications through
their own ``test_client()``.
"""

from fastapi.testclient import TestClient
from pydantic import ValidationError

from lab6.flask_sqlite import close_db, create_app as create_sqlite_app
from lab6.param_api import app as param_api
from lab6.schemas import TaskCreate
from lab6.table_app import create_app as create_table_app
from lab6.tasks_api import TASKS, app as tasks_api

TABLE_ROWS = [
    {"name": "alpha", "value": "1"},
    {"name": "beta", "value": "2"},
]


def show_medium_tasks() -> None:
    """Demonstrate the three medium-level tasks in-process."""
    print("Medium tasks")

    table_app = create_table_app(TABLE_ROWS)
    table_response = table_app.test_client().get("/")
    print("table_app GET / ->", table_response.status_code)
    print("  contains cell 'alpha':", b"alpha" in table_response.data)

    greet_client = TestClient(param_api)
    greet_response = greet_client.get("/greet", params={"name": "Ada"})
    print("param_api GET /greet?name=Ada ->", greet_response.json())

    TASKS.clear()
    tasks_client = TestClient(tasks_api)
    created = tasks_client.post(
        "/tasks",
        json={"title": "write report", "priority": 3},
    )
    print("tasks_api POST /tasks ->", created.status_code)
    print("tasks_api GET /tasks ->", tasks_client.get("/tasks").json())


def show_advanced_tasks() -> None:
    """Demonstrate the two advanced-level tasks in-process."""
    print("Advanced tasks")

    try:
        TaskCreate(title="   ", priority=3)
    except ValidationError as error:
        print("schemas: blank title rejected ->", error.errors()[0]["msg"])

    sqlite_app = create_sqlite_app()
    client = sqlite_app.test_client()
    created = client.post(
        "/items",
        json={"name": "notebook", "quantity": 2},
    )
    print("flask_sqlite POST /items ->", created.status_code)
    print("flask_sqlite GET /items ->", client.get("/items").get_json())
    close_db(sqlite_app)


def print_server_commands() -> None:
    """Print commands that start real HTTP servers (not run here)."""
    print("Start the real servers with (ports are NOT opened here):")
    print("  uv run --with fastapi --with uvicorn \\")
    print("    uvicorn lab6.param_api:app --reload")
    print("  uv run --with fastapi --with uvicorn \\")
    print("    uvicorn lab6.tasks_api:app --reload")
    print("  uv run --with flask flask --app lab6.table_app run")


def main() -> None:
    """Print a short tour over every task of the variant."""
    show_medium_tasks()
    show_advanced_tasks()
    print_server_commands()


if __name__ == "__main__":
    main()
