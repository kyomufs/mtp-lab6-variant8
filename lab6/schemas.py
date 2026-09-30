"""Pydantic v2 schemas shared by the tasks REST API (advanced task 8)."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


def _clean_title(value: str) -> str:
    """Strip surrounding spaces and reject titles left empty."""
    stripped = value.strip()
    if not stripped:
        raise ValueError("title must not be blank")
    return stripped


class TaskCreate(BaseModel):
    """Payload accepted when a new task is created."""

    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(ge=1, le=5)
    due_date: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        """Reject titles that become empty after stripping spaces."""
        return _clean_title(value)


class Task(TaskCreate):
    """A stored task: the creation payload plus server-side fields."""

    id: int
    done: bool = False


class TaskUpdate(BaseModel):
    """Partial update payload for an existing task.

    Every field is optional, but the payload itself must not be
    empty: an update that changes nothing is rejected.
    """

    title: str | None = Field(default=None, max_length=100)
    priority: int | None = Field(default=None, ge=1, le=5)
    due_date: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str | None) -> str | None:
        """Reject titles that become empty after stripping spaces."""
        if value is None:
            return None
        return _clean_title(value)

    @model_validator(mode="after")
    def must_change_something(self) -> "TaskUpdate":
        """Reject payloads that do not mention any field."""
        if not self.model_fields_set:
            raise ValueError("update must contain at least one field")
        return self
