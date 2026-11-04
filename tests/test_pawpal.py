from datetime import date

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task("Feed Zack", 3, "08:45", "high")
    assert task.completed is False
    assert task.last_completed is None

    task.mark_complete(on=date(2026, 11, 4))

    assert task.completed is True
    assert task.last_completed == date(2026, 11, 4)


def test_add_task_increases_pet_task_count():
    zack = Pet("Zack", "dog")
    assert len(zack.tasks) == 0

    zack.add_task(Task("Take Zack for a walk", 5, "08:30", "high"))
    assert len(zack.tasks) == 1

    zack.add_task(Task("Feed Zack", 3, "08:45", "high"))
    assert len(zack.tasks) == 2
