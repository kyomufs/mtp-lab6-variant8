"""Tests for the greeting FastAPI endpoint (medium task 8)."""

import unittest

from fastapi.testclient import TestClient

from lab6.param_api import app


class ParamApiTests(unittest.TestCase):
    """Checks for the ``/greet`` endpoint."""

    def setUp(self) -> None:
        """Create a transport-free client for the API."""
        self.client = TestClient(app)

    def test_greet_returns_greeting(self) -> None:
        """A valid name is embedded into the greeting."""
        response = self.client.get("/greet", params={"name": "Ada"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"greeting": "Hello, Ada!"})

    def test_missing_name_returns_422(self) -> None:
        """A request without ``name`` fails validation with 422."""
        response = self.client.get("/greet")
        self.assertEqual(response.status_code, 422)

    def test_empty_name_returns_422(self) -> None:
        """An empty ``name`` violates ``min_length=1``: 422."""
        response = self.client.get("/greet", params={"name": ""})
        self.assertEqual(response.status_code, 422)

    def test_non_ascii_name_is_supported(self) -> None:
        """Non-ASCII names are passed through unchanged."""
        response = self.client.get("/greet", params={"name": "Матвей"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"greeting": "Hello, Матвей!"},
        )


if __name__ == "__main__":
    unittest.main()
