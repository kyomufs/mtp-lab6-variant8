"""Tests for the data table Flask page (medium task 4)."""

import unittest

from lab6.table_app import create_app

ROWS = [
    {"name": "alpha", "value": "1"},
    {"name": "beta", "value": "2"},
]


class TableAppTests(unittest.TestCase):
    """Checks for :func:`lab6.table_app.create_app`."""

    def test_index_returns_200(self) -> None:
        """The index page answers with HTTP 200."""
        client = create_app(ROWS).test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_headers_come_from_first_row_keys(self) -> None:
        """Table headers are the keys of the first dictionary."""
        client = create_app(ROWS).test_client()
        html = client.get("/").get_data(as_text=True)
        self.assertIn("<th>name</th>", html)
        self.assertIn("<th>value</th>", html)

    def test_cell_values_are_rendered(self) -> None:
        """Every row value appears in its own table cell."""
        client = create_app(ROWS).test_client()
        html = client.get("/").get_data(as_text=True)
        self.assertIn("<td>alpha</td>", html)
        self.assertIn("<td>beta</td>", html)
        self.assertIn("<td>2</td>", html)

    def test_empty_list_shows_note(self) -> None:
        """An empty row list renders an empty table with a note."""
        client = create_app([]).test_client()
        html = client.get("/").get_data(as_text=True)
        self.assertIn("<table>", html)
        self.assertIn("No rows to display", html)

    def test_missing_rows_default_to_empty_table(self) -> None:
        """Calling the factory without rows still serves a page."""
        client = create_app().test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "No rows to display",
            response.get_data(as_text=True),
        )


if __name__ == "__main__":
    unittest.main()
