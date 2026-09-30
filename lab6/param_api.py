"""FastAPI endpoint greeting a validated query parameter (task 8)."""

from fastapi import FastAPI, Query

app = FastAPI(title="Greeting API")


@app.get("/greet")
def greet(name: str = Query(min_length=1)) -> dict[str, str]:
    """Return a greeting that embeds the ``name`` query parameter.

    FastAPI validates the parameter first: a missing or empty
    ``name`` is rejected with HTTP 422 before this function runs.

    Args:
        name: Non-empty name to greet.

    Returns:
        A JSON object with the ``greeting`` key.
    """
    return {"greeting": f"Hello, {name}!"}
