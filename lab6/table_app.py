"""Flask page rendering rows of dictionaries as an HTML table (task 4)."""

from flask import Flask, render_template


def create_app(rows: list[dict[str, str]] | None = None) -> Flask:
    """Create a Flask app that renders ``rows`` as an HTML table.

    The table headers are taken from the keys of the first row.
    An empty or missing ``rows`` list produces an empty table
    together with an explanatory note.

    Args:
        rows: Table rows; every row maps a header to its cell text.

    Returns:
        A configured Flask application with a ``GET /`` route.
    """
    app = Flask(__name__)
    data: list[dict[str, str]] = list(rows) if rows else []

    @app.get("/")
    def index() -> str:
        """Render the table page for the rows captured by the factory."""
        headers: list[str] = list(data[0]) if data else []
        return render_template("table.html", headers=headers, rows=data)

    return app
