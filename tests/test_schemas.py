"""Tests for the Pydantic schemas (advanced task 8)."""

import unittest
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from lab6.schemas import Task, TaskCreate, TaskUpdate


class TaskCreateTests(unittest.TestCase):
    """Checks for :class:`lab6.schemas.TaskCreate`."""

    def test_valid_payload_is_accepted(self) -> None:
        """A well-formed payload keeps its normalized values."""
        task = TaskCreate(title="  buy milk  ", priority=2)
        self.assertEqual(task.title, "buy milk")
        self.assertEqual(task.priority, 2)
        self.assertIsNone(task.due_date)

    def test_blank_title_is_rejected(self) -> None:
        """A title that strips to nothing raises a validation error."""
        with self.assertRaises(ValidationError):
            TaskCreate(title="   \t", priority=1)

    def test_priority_out_of_range_is_rejected(self) -> None:
        """Priorities outside the 1..5 range are rejected."""
        with self.assertRaises(ValidationError):
            TaskCreate(title="ok", priority=0)
        with self.assertRaises(ValidationError):
            TaskCreate(title="ok", priority=6)

    def test_due_date_accepts_a_future_datetime(self) -> None:
        """An explicit deadline is stored as a datetime value."""
        moment = datetime.now(timezone.utc) + timedelta(days=1)
        task = TaskCreate(title="deadline", priority=3, due_date=moment)
        self.assertEqual(task.due_date, moment)


class TaskTests(unittest.TestCase):
    """Checks for :class:`lab6.schemas.Task`."""

    def test_task_adds_id_and_done_flag(self) -> None:
        """Stored tasks carry the server id and the status flag."""
        task = Task(id=7, title="ship", priority=5)
        self.assertEqual(task.id, 7)
        self.assertFalse(task.done)

    def test_task_inherits_creation_constraints(self) -> None:
        """The stored model keeps the validation of its payload."""
        with self.assertRaises(ValidationError):
            Task(id=1, title="", priority=3)


class TaskUpdateTests(unittest.TestCase):
    """Checks for :class:`lab6.schemas.TaskUpdate`."""

    def test_partial_payload_is_accepted(self) -> None:
        """Only the provided fields are marked as set."""
        update = TaskUpdate(priority=2)
        self.assertEqual(update.model_fields_set, {"priority"})

    def test_empty_update_is_rejected(self) -> None:
        """A payload that changes nothing raises a validation error."""
        with self.assertRaises(ValidationError):
            TaskUpdate()

    def test_blank_title_is_rejected(self) -> None:
        """Updates validate the title exactly like creation does."""
        with self.assertRaises(ValidationError):
            TaskUpdate(title=" ")

    def test_explicit_null_due_date_is_allowed(self) -> None:
        """Clearing the deadline counts as a meaningful update."""
        update = TaskUpdate(due_date=None)
        self.assertIn("due_date", update.model_fields_set)


if __name__ == "__main__":
    unittest.main()
