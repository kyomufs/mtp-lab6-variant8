"""Tests for the in-memory tasks REST API (medium task 10)."""

import unittest

from fastapi.testclient import TestClient

from lab6.tasks_api import TASKS, app


class TasksApiTests(unittest.TestCase):
    """Checks for the tasks endpoints."""

    def setUp(self) -> None:
        """Start every test from an empty store."""
        TASKS.clear()
        self.client = TestClient(app)

    def create_task(self, title: str = "sample") -> dict[str, object]:
        """Create one task through the API and return its body."""
        response = self.client.post(
            "/tasks",
            json={"title": title, "priority": 2},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_create_returns_201_and_assigns_id(self) -> None:
        """A valid payload is stored and answered with HTTP 201."""
        body = self.create_task("read mail")
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["title"], "read mail")
        self.assertFalse(body["done"])

    def test_list_returns_created_tasks(self) -> None:
        """Created tasks are listed in identifier order."""
        self.create_task("first")
        self.create_task("second")
        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.json()]
        self.assertEqual(titles, ["first", "second"])

    def test_get_missing_task_returns_404(self) -> None:
        """Unknown identifiers are answered with HTTP 404."""
        response = self.client.get("/tasks/999")
        self.assertEqual(response.status_code, 404)

    def test_toggle_flips_done_flag(self) -> None:
        """The toggle route flips the ``done`` flag on every call."""
        task_id = self.create_task()["id"]
        first = self.client.patch(f"/tasks/{task_id}/toggle")
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.json()["done"])
        second = self.client.patch(f"/tasks/{task_id}/toggle")
        self.assertFalse(second.json()["done"])

    def test_toggle_missing_task_returns_404(self) -> None:
        """Toggling an unknown task fails with HTTP 404."""
        response = self.client.patch("/tasks/42/toggle")
        self.assertEqual(response.status_code, 404)

    def test_patch_updates_only_given_fields(self) -> None:
        """PATCH changes the provided fields and keeps the rest."""
        task_id = self.create_task("old title")["id"]
        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"priority": 5},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "old title")
        self.assertEqual(response.json()["priority"], 5)

    def test_invalid_priority_returns_422(self) -> None:
        """Pydantic rejects priorities outside 1..5 with 422."""
        response = self.client.post(
            "/tasks",
            json={"title": "bad", "priority": 0},
        )
        self.assertEqual(response.status_code, 422)

    def test_blank_title_returns_422(self) -> None:
        """A title that strips to nothing fails with HTTP 422."""
        response = self.client.post(
            "/tasks",
            json={"title": "   ", "priority": 1},
        )
        self.assertEqual(response.status_code, 422)

    def test_delete_returns_204_then_404(self) -> None:
        """Deleting removes the task; a second delete fails."""
        task_id = self.create_task()["id"]
        deleted = self.client.delete(f"/tasks/{task_id}")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get(f"/tasks/{task_id}").status_code, 404)
        again = self.client.delete(f"/tasks/{task_id}")
        self.assertEqual(again.status_code, 404)


if __name__ == "__main__":
    unittest.main()
