"""In-memory REST API for tasks built with FastAPI (task 10)."""

from fastapi import FastAPI, HTTPException, status

from lab6.schemas import Task, TaskCreate, TaskUpdate

app = FastAPI(title="Tasks API")

#: In-memory task storage keyed by task identifier.
TASKS: dict[int, Task] = {}


def _require_task(task_id: int) -> Task:
    """Return the stored task or raise a 404 HTTP error."""
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found",
        )
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    """Return every stored task ordered by identifier."""
    return [TASKS[key] for key in sorted(TASKS)]


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
)
def create_task(payload: TaskCreate) -> Task:
    """Store ``payload`` as a new task and answer with HTTP 201."""
    task_id = max(TASKS, default=0) + 1
    task = Task(id=task_id, **payload.model_dump())
    TASKS[task_id] = task
    return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    """Return the task with identifier ``task_id``."""
    return _require_task(task_id)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    """Apply a partial update to the task with identifier ``task_id``."""
    task = _require_task(task_id)
    changes = payload.model_dump(exclude_unset=True)
    updated = task.model_copy(update=changes)
    TASKS[task_id] = updated
    return updated


@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: int) -> Task:
    """Flip the ``done`` flag of the task with identifier ``task_id``."""
    task = _require_task(task_id)
    updated = task.model_copy(update={"done": not task.done})
    TASKS[task_id] = updated
    return updated


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int) -> None:
    """Remove the task with identifier ``task_id`` from the store."""
    _require_task(task_id)
    del TASKS[task_id]
