from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 11, 5)

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


def test_task_accepts_valid_or_empty_time():
    assert Task("Feed Zack", 3, "00:00").time == "00:00"
    assert Task("Feed Zack", 3, "23:59").time == "23:59"
    assert Task("Feed Zack", 3).time == ""


@pytest.mark.parametrize("bad_time", ["8:30", "24:00", "12:60", "8.30", "08:30am", "noon"])
def test_task_rejects_invalid_time(bad_time):
    with pytest.raises(ValueError):
        Task("Feed Zack", 3, bad_time)


def test_edit_task_rejects_invalid_time_without_changing_task():
    zack = Pet("Zack", "dog")
    task = Task("Feed Zack", 3, "08:45")
    zack.add_task(task)

    with pytest.raises(ValueError):
        zack.edit_task(task, time="25:00")
    assert task.time == "08:45"

def make_owner():
    owner = Owner("Julia")
    zack = Pet("Zack", "dog")
    smudge = Pet("Smudge", "cat")
    zack.add_task(Task("Take Zack for a walk", 5, "08:30", "high"))
    zack.add_task(Task("Feed Zack", 3, "08:45", "high"))
    smudge.add_task(Task("Feed Smudge", 3, "09:00", "high"))
    owner.add_pet(zack)
    owner.add_pet(smudge)
    return owner


def test_filter_tasks_with_no_filters_returns_all_tasks():
    owner = make_owner()
    assert owner.filter_tasks() == owner.get_all_tasks()


def test_filter_tasks_by_pet_name():
    owner = make_owner()
    tasks = owner.filter_tasks(pet_name="Zack")
    assert [t.description for t in tasks] == ["Take Zack for a walk", "Feed Zack"]


def test_filter_tasks_unknown_pet_returns_empty():
    assert make_owner().filter_tasks(pet_name="Rex") == []


def test_filter_tasks_by_completion_includes_next_occurrence_as_pending():
    owner = make_owner()
    zack = owner.pets[0]
    walk, feed_zack, feed_smudge = owner.get_all_tasks()
    next_walk = zack.complete_task(walk, on=TODAY)

    assert owner.filter_tasks(completed=True) == [walk]
    assert owner.filter_tasks(completed=False) == [feed_zack, next_walk, feed_smudge]


def test_filter_tasks_combines_pet_and_completion():
    owner = make_owner()
    walk, feed_zack, feed_smudge = owner.get_all_tasks()
    walk.mark_complete(on=TODAY)
    feed_smudge.mark_complete(on=TODAY)

    assert owner.filter_tasks(pet_name="Zack", completed=False) == [feed_zack]


def test_sort_by_time_orders_out_of_order_tasks_by_start_time():
    owner = Owner("Julia")
    zack = Pet("Zack", "dog")
    zack.add_task(Task("Evening walk", 20, "18:00", "medium"))
    zack.add_task(Task("Brush Zack", 10, "", "high"))           # untimed goes last
    zack.add_task(Task("Feed Zack", 3, "08:45", "high"))
    zack.add_task(Task("Morning walk", 15, "08:30", "medium"))
    zack.add_task(Task("Give meds", 2, "08:30", "high"))        # same time: high first
    zack.add_task(Task("Lunch snack", 2, "12:00", "low"))
    owner.add_pet(zack)

    ordered = Scheduler(owner).sort_by_time(zack.tasks)

    assert [t.description for t in ordered] == [
        "Give meds", "Morning walk", "Feed Zack", "Lunch snack", "Evening walk", "Brush Zack",
    ]


def make_tight_schedule():
    owner = Owner("Julia", available_minutes=30)
    zack = Pet("Zack", "dog")
    zack.add_task(Task("Play fetch", 20, "08:00", "low"))
    zack.add_task(Task("Evening meds", 15, "19:00", "high"))
    zack.add_task(Task("Lunch walk", 10, "12:00", "medium"))
    owner.add_pet(zack)
    return Scheduler(owner)


def test_generate_plan_keeps_high_priority_tasks_when_time_is_tight():
    scheduler = make_tight_schedule()
    scheduler.generate_plan(today=TODAY)

    assert {t.description for t in scheduler.plan} == {"Evening meds", "Lunch walk"}
    assert [t.description for t in scheduler.skipped] == ["Play fetch"]


def test_generate_plan_returns_tasks_in_start_time_order():
    plan = make_tight_schedule().generate_plan(today=TODAY)

    assert [t.description for t in plan] == ["Lunch walk", "Evening meds"]


@pytest.mark.parametrize("frequency, days", [("daily", 1), ("weekly", 7)])
def test_mark_complete_returns_next_occurrence(frequency, days):
    task = Task("Feed Zack", 3, "08:45", "high", frequency=frequency)

    next_task = task.mark_complete(on=TODAY)

    assert next_task is not task
    assert next_task.due_date == TODAY + timedelta(days=days)
    assert next_task.completed is False
    assert next_task.last_completed is None
    assert (next_task.description, next_task.time, next_task.priority) == ("Feed Zack", "08:45", "high")


def test_daily_next_occurrence_crosses_month_end():
    next_task = Task("Feed Zack", 3).mark_complete(on=date(2026, 11, 30))
    assert next_task.due_date == date(2026, 12, 1)


def test_mark_complete_twice_raises():
    task = Task("Feed Zack", 3)
    task.mark_complete(on=TODAY)
    with pytest.raises(ValueError):
        task.mark_complete(on=TODAY)


def test_complete_task_adds_next_occurrence_to_pet():
    zack = Pet("Zack", "dog")
    walk = Task("Walk", 20, "08:30", frequency="weekly")
    zack.add_task(walk)

    next_walk = zack.complete_task(walk, on=TODAY)

    assert zack.tasks == [walk, next_walk]
    assert next_walk.pet_name == "Zack"


def test_next_occurrence_is_only_due_from_its_due_date():
    walk = Task("Walk", 20, frequency="weekly")
    next_walk = walk.mark_complete(on=TODAY)

    assert walk.is_due_today(TODAY) is False
    assert next_walk.is_due_today(TODAY + timedelta(days=6)) is False
    assert next_walk.is_due_today(TODAY + timedelta(days=7)) is True
    assert next_walk.is_due_today(TODAY + timedelta(days=9)) is True  # overdue still shows


def test_generate_plan_skips_completed_and_not_yet_due_tasks():
    owner = Owner("Julia")
    zack = Pet("Zack", "dog")
    feed = Task("Feed Zack", 3, "08:45", frequency="daily")
    bath = Task("Bath", 30, "10:00", frequency="weekly")
    zack.add_task(feed)
    zack.add_task(bath)
    owner.add_pet(zack)
    next_feed = zack.complete_task(feed, on=TODAY)
    zack.complete_task(bath, on=TODAY)

    scheduler = Scheduler(owner)
    assert scheduler.generate_plan(today=TODAY) == []
    assert scheduler.generate_plan(today=TODAY + timedelta(days=1)) == [next_feed]


def make_conflict_scheduler(*tasks_by_pet):
    owner = Owner("Julia")
    for pet_name, tasks in tasks_by_pet:
        pet = Pet(pet_name, "dog")
        for task in tasks:
            pet.add_task(task)
        owner.add_pet(pet)
    return Scheduler(owner)


def test_detect_conflicts_same_pet_same_time():
    scheduler = make_conflict_scheduler(
        ("Zack", [Task("Give meds", 2, "08:30"), Task("Morning walk", 15, "08:30")]),
    )
    scheduler.generate_plan(today=TODAY)

    assert scheduler.detect_conflicts() == [
        "Conflict at 08:30 for Zack: Give meds (Zack), Morning walk (Zack)"
    ]


def test_detect_conflicts_across_pets():
    scheduler = make_conflict_scheduler(
        ("Zack", [Task("Brush Zack", 5, "09:00")]),
        ("Smudge", [Task("Feed Smudge", 3, "09:00")]),
    )
    scheduler.generate_plan(today=TODAY)

    assert scheduler.detect_conflicts() == [
        "Conflict at 09:00 across pets: Feed Smudge (Smudge), Brush Zack (Zack)"
    ]


def test_detect_conflicts_reports_three_way_clash_once():
    scheduler = make_conflict_scheduler(
        ("Zack", [Task("Walk", 10, "08:00"), Task("Feed Zack", 3, "08:00")]),
        ("Smudge", [Task("Feed Smudge", 3, "08:00")]),
    )
    scheduler.generate_plan(today=TODAY)

    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Walk (Zack)" in warnings[0] and "Feed Smudge (Smudge)" in warnings[0]


def test_detect_conflicts_ignores_different_and_untimed_tasks():
    scheduler = make_conflict_scheduler(
        ("Zack", [Task("Walk", 10, "08:00"), Task("Feed Zack", 3, "08:15"),
                  Task("Brush", 5), Task("Play", 5)]),
    )
    scheduler.generate_plan(today=TODAY)

    assert scheduler.detect_conflicts() == []
    assert scheduler.detect_conflicts([]) == []


def make_pet_with_duplicate_tasks():
    """A pet with two separate but identical tasks (equal by value, different objects)."""
    zack = Pet("Zack", "dog")
    first = Task("Feed Zack", 3, "08:45")
    second = Task("Feed Zack", 3, "08:45")
    zack.add_task(first)
    zack.add_task(second)
    assert vars(first) == vars(second) and first is not second  # same fields, different objects
    return zack, first, second


def test_remove_task_removes_the_exact_duplicate_given():
    zack, first, second = make_pet_with_duplicate_tasks()

    zack.remove_task(second)

    assert len(zack.tasks) == 1
    assert zack.tasks[0] is first


def test_complete_task_completes_only_the_exact_duplicate_given():
    zack, first, second = make_pet_with_duplicate_tasks()

    next_feed = zack.complete_task(second, on=TODAY)

    assert second.completed is True
    assert first.completed is False
    assert len(zack.tasks) == 3 and zack.tasks[2] is next_feed


def test_edit_task_changes_only_the_exact_duplicate_given():
    zack, first, second = make_pet_with_duplicate_tasks()

    zack.edit_task(second, priority="high")

    assert second.priority == "high"
    assert first.priority == "medium"


def test_complete_task_rejects_equal_task_not_owned_by_pet():
    zack, first, second = make_pet_with_duplicate_tasks()
    lookalike = Task("Feed Zack", 3, "08:45", pet_name="Zack")  # equal by value, never added

    with pytest.raises(ValueError):
        zack.complete_task(lookalike, on=TODAY)
    assert not first.completed and not second.completed


def test_duplicate_tasks_both_planned_and_flagged_as_conflict():
    zack, first, second = make_pet_with_duplicate_tasks()
    owner = Owner("Julia")
    owner.add_pet(zack)
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan(today=TODAY)

    assert len(plan) == 2
    assert plan[0] is first and plan[1] is second
    assert scheduler.detect_conflicts() == [
        "Conflict at 08:45 for Zack: Feed Zack (Zack), Feed Zack (Zack)"
    ]


def test_detect_conflicts_skips_completed_tasks_in_plan():
    scheduler = make_conflict_scheduler(
        ("Zack", [Task("Walk", 10, "08:00"), Task("Feed Zack", 3, "08:00")]),
    )
    zack = scheduler.owner.pets[0]
    zack.complete_task(zack.tasks[0], on=TODAY)  # next walk is due tomorrow
    scheduler.generate_plan(today=TODAY)

    assert scheduler.detect_conflicts() == []
