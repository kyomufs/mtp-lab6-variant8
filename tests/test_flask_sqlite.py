"""Tests for the Flask SQLite CRUD app (advanced task 1)."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from lab6.flask_sqlite import CONNECTION_KEY, close_db, create_app


class FlaskSqliteTests(unittest.TestCase):
    """Checks for the ``/items`` CRUD routes."""

    def setUp(self) -> None:
        """Build an in-memory app together with its test client."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.addCleanup(close_db, self.app)

    @staticmethod
    def table_names(connection: sqlite3.Connection) -> list[str]:
        """Return user table names visible to ``connection``."""
        rows = connection.execute(
            "SELECT name FROM sqlite_master"
            " WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        return [row["name"] for row in rows]

    def test_empty_database_returns_empty_list(self) -> None:
        """A fresh database answers with HTTP 200 and ``[]``."""
        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_create_returns_201_and_item_appears_in_list(self) -> None:
        """A valid body creates an item visible to later GETs."""
        response = self.client.post(
            "/items",
            json={"name": "apple", "quantity": 3},
        )
        self.assertEqual(response.status_code, 201)
        created = response.get_json()
        self.assertEqual(created["name"], "apple")
        self.assertEqual(created["quantity"], 3)
        listed = self.client.get("/items").get_json()
        self.assertEqual(listed, [created])

    def test_create_without_name_returns_400(self) -> None:
        """A missing or blank ``name`` is answered with HTTP 400."""
        missing = self.client.post("/items", json={"quantity": 1})
        self.assertEqual(missing.status_code, 400)
        blank = self.client.post("/items", json={"name": "   "})
        self.assertEqual(blank.status_code, 400)

    def test_create_without_json_body_returns_400(self) -> None:
        """A non-object body is answered with HTTP 400."""
        response = self.client.post(
            "/items",
            data="not a json object",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_replaces_item_fields(self) -> None:
        """PUT answers with 200 and stores the new values."""
        created = self.client.post(
            "/items",
            json={"name": "pen", "quantity": 1},
        ).get_json()
        response = self.client.put(
            f"/items/{created['id']}",
            json={"name": "pencil", "quantity": 10},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "pencil")
        self.assertEqual(response.get_json()["quantity"], 10)

    def test_update_missing_item_returns_404(self) -> None:
        """Updating an unknown identifier fails with HTTP 404."""
        response = self.client.put(
            "/items/77",
            json={"name": "ghost"},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_returns_204_then_404(self) -> None:
        """Deleting removes the row; a second delete fails."""
        created = self.client.post(
            "/items",
            json={"name": "box"},
        ).get_json()
        deleted = self.client.delete(f"/items/{created['id']}")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get("/items").get_json(), [])
        again = self.client.delete(f"/items/{created['id']}")
        self.assertEqual(again.status_code, 404)

    def test_table_is_created_on_first_access(self) -> None:
        """The items table appears only after the first request."""
        app = create_app()
        self.addCleanup(close_db, app)
        connection = app.extensions[CONNECTION_KEY]
        self.assertEqual(self.table_names(connection), [])
        app.test_client().get("/items")
        self.assertEqual(self.table_names(connection), ["items"])

    def test_connection_closes_with_context_manager(self) -> None:
        """``contextlib.closing`` releases the SQLite connection."""
        app = create_app()
        connection = app.extensions[CONNECTION_KEY]
        with closing(connection):
            pass
        self.addCleanup(close_db, app)
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")

    def test_file_database_keeps_data_between_apps(self) -> None:
        """A file path stores rows outside the process memory."""
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "items.sqlite3")
            first_app = create_app(path)
            created = first_app.test_client().post(
                "/items",
                json={"name": "disk"},
            )
            self.assertEqual(created.status_code, 201)
            close_db(first_app)

            second_app = create_app(path)
            stored = second_app.test_client().get("/items").get_json()
            self.assertEqual([row["name"] for row in stored], ["disk"])
            close_db(second_app)


if __name__ == "__main__":
    unittest.main()
