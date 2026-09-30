"""Flask CRUD application backed by SQLite (advanced task 1)."""

import sqlite3
from contextlib import closing

from flask import Flask, Response, jsonify, request

#: Schema of the single table used by the application.
CREATE_ITEMS_TABLE = (
    "CREATE TABLE IF NOT EXISTS items ("
    " id INTEGER PRIMARY KEY AUTOINCREMENT,"
    " name TEXT NOT NULL,"
    " quantity INTEGER NOT NULL DEFAULT 0"
    ")"
)

#: Flask extension key holding the application-wide connection.
CONNECTION_KEY = "items_connection"


def parse_item_payload(payload: object) -> dict[str, object]:
    """Validate a decoded JSON body and return normalized fields.

    Args:
        payload: Object decoded from the request body.

    Returns:
        A mapping with the ``name`` and ``quantity`` fields.

    Raises:
        ValueError: If the body is not a JSON object or contains an
            invalid ``name`` or ``quantity`` value.
    """
    if not isinstance(payload, dict):
        raise ValueError("JSON object body is required")
    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("'name' must be a non-empty string")
    quantity = payload.get("quantity", 0)
    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise ValueError("'quantity' must be an integer")
    return {"name": name.strip(), "quantity": quantity}


def fetch_item(
    connection: sqlite3.Connection,
    item_id: int,
) -> dict[str, object] | None:
    """Return the item row as a dict or ``None`` when it is missing."""
    row = connection.execute(
        "SELECT id, name, quantity FROM items WHERE id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def close_db(app: Flask) -> None:
    """Close the database connection of ``app``.

    The connection is released through :func:`contextlib.closing`,
    so ``close()`` runs even if the surrounding block fails. Calling
    the function twice is safe.
    """
    connection = app.extensions.get(CONNECTION_KEY)
    if connection is not None:
        with closing(connection):
            pass


def create_app(db_path: str | None = None) -> Flask:
    """Create a Flask app with CRUD routes over an SQLite database.

    The ``items`` table is created on the first database access.
    One connection serves the whole application lifetime: the default
    ``":memory:"`` database exists only while that connection is
    open, so data must survive between requests. Release the
    connection with :func:`close_db` when the app is no longer used.

    Args:
        db_path: SQLite file path, ``":memory:"`` by default.

    Returns:
        A Flask application exposing the ``/items`` CRUD routes.
    """
    target = ":memory:" if db_path is None else db_path
    app = Flask(__name__)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    app.extensions[CONNECTION_KEY] = connection
    table_ready = False

    def get_db() -> sqlite3.Connection:
        """Return the app connection, creating the table once."""
        nonlocal table_ready
        if not table_ready:
            with connection:
                connection.execute(CREATE_ITEMS_TABLE)
            table_ready = True
        return connection

    @app.errorhandler(ValueError)
    def handle_bad_payload(error: ValueError) -> tuple[Response, int]:
        """Turn payload validation failures into HTTP 400."""
        return jsonify({"error": str(error)}), 400

    @app.get("/items")
    def list_items() -> Response:
        """Return all stored items as a JSON list ordered by id."""
        db = get_db()
        rows = db.execute(
            "SELECT id, name, quantity FROM items ORDER BY id"
        ).fetchall()
        return jsonify([dict(row) for row in rows])

    @app.post("/items")
    def create_item() -> tuple[Response, int]:
        """Store a new item and answer with HTTP 201."""
        fields = parse_item_payload(request.get_json(silent=True))
        db = get_db()
        with db:
            cursor = db.execute(
                "INSERT INTO items (name, quantity) VALUES (?, ?)",
                (fields["name"], fields["quantity"]),
            )
        item_id = int(cursor.lastrowid)
        return jsonify(fetch_item(db, item_id)), 201

    @app.put("/items/<int:item_id>")
    def update_item(item_id: int) -> tuple[Response, int]:
        """Replace the item ``item_id``; 404 when it does not exist."""
        fields = parse_item_payload(request.get_json(silent=True))
        db = get_db()
        with db:
            cursor = db.execute(
                "UPDATE items SET name = ?, quantity = ? WHERE id = ?",
                (fields["name"], fields["quantity"], item_id),
            )
        if cursor.rowcount == 0:
            return jsonify({"error": "item not found"}), 404
        return jsonify(fetch_item(db, item_id)), 200

    @app.delete("/items/<int:item_id>")
    def delete_item(item_id: int) -> tuple[Response, int]:
        """Delete the item ``item_id``; 404 when it does not exist."""
        db = get_db()
        with db:
            cursor = db.execute(
                "DELETE FROM items WHERE id = ?",
                (item_id,),
            )
        if cursor.rowcount == 0:
            return jsonify({"error": "item not found"}), 404
        return Response(status=204), 204

    return app
