import re
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}
TIME_PATTERN = re.compile(r"([01]\d|2[0-3]):[0-5]\d")  # zero-padded 24-hour "HH:MM"


@dataclass(eq=False)  # compare by identity so duplicate-looking tasks stay distinct
class Task:
    """A single pet care task, e.g. a walk or feeding."""
    description: str
    duration_minutes: int
    time: str = ""                # preferred start time as "HH:MM", or "" for any time
    priority: str = "medium"      # "low", "medium", or "high"
    frequency: str = "daily"      # "daily" or "weekly"
    due_date: date | None = None  # None means due now
    completed: bool = False
    last_completed: date | None = None
    pet_name: str = ""            # set by Pet.add_task()

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.time and not TIME_PATTERN.fullmatch(self.time):
            raise ValueError(f"time must be in 24-hour 'HH:MM' format, got {self.time!r}")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.frequency not in RECURRENCE_DAYS:
            raise ValueError(f"frequency must be one of {list(RECURRENCE_DAYS)}")

    def mark_complete(self, on: date | None = None) -> "Task":
        """Mark this task as done and return a new task for its next occurrence."""
        if self.completed:
            raise ValueError(f"{self.description!r} is already complete")
        on = on or date.today()
        self.completed = True
        self.last_completed = on
        return replace(
            self,
            due_date=on + timedelta(days=RECURRENCE_DAYS[self.frequency]),
            completed=False,
            last_completed=None,
        )

    def is_due_today(self, today: date | None = None) -> bool:
        """Return True if this task is not done and its due date has arrived."""
        if self.completed:
            return False
        return self.due_date is None or self.due_date <= (today or date.today())


@dataclass
class Pet:
    """A pet and the care tasks it needs."""
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task: Task, **changes) -> None:
        """Update fields on an existing task, e.g. edit_task(t, priority="high")."""
        if task not in self.tasks:
            raise ValueError(f"{task.description!r} is not one of {self.name}'s tasks")
        validated = replace(task, **changes)  # raises before anything is changed
        for name in changes:
            setattr(task, name, getattr(validated, name))

    def complete_task(self, task: Task, on: date | None = None) -> Task:
        """Mark a task done and add its next occurrence to this pet."""
        if task not in self.tasks:
            raise ValueError(f"{task.description!r} is not one of {self.name}'s tasks")
        next_task = task.mark_complete(on)
        self.add_task(next_task)
        return next_task

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """A pet owner, their pets, and their daily constraints."""
    name: str
    available_minutes: int = 60
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def filter_tasks(self, pet_name: str | None = None,
                     completed: bool | None = None) -> list[Task]:
        """Return tasks matching every filter given; None means don't filter on it."""
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks


@dataclass
class Scheduler:
    """Builds a daily care plan for an owner's pets."""
    owner: Owner
    plan: list[Task] = field(default_factory=list, init=False)
    skipped: list[Task] = field(default_factory=list, init=False)

    def generate_plan(self, today: date | None = None) -> list[Task]:
        """Pick due tasks by priority to fit the owner's time, then order them by start time."""
        due = [t for t in self.owner.get_all_tasks() if t.is_due_today(today)]
        self.plan, self.skipped = [], []
        minutes_left = self.owner.available_minutes
        for task in self.sort_by_priority(due):       # decide what fits
            if task.duration_minutes <= minutes_left:
                self.plan.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append(task)
        self.plan = self.sort_by_time(self.plan)      # decide display order
        return self.plan

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority, then start time, then shortest first."""
        return sorted(
            tasks,
            key=lambda t: (PRIORITY_RANK[t.priority], t.time or "99:99", t.duration_minutes),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks in start-time order; untimed tasks go last."""
        return sorted(tasks, key=lambda t: (t.time or "99:99", PRIORITY_RANK[t.priority]))

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return a warning for each start time shared by two or more tasks; never raises."""
        tasks = self.plan if tasks is None else tasks
        by_time: dict[str, list[Task]] = defaultdict(list)
        for task in tasks:
            if task.time:
                by_time[task.time].append(task)

        warnings = []
        for time, clashing in sorted(by_time.items()):
            if len(clashing) < 2:
                continue
            pets = {t.pet_name for t in clashing}
            who = f"for {clashing[0].pet_name}" if len(pets) == 1 else "across pets"
            names = ", ".join(f"{t.description} ({t.pet_name})" for t in clashing)
            warnings.append(f"Conflict at {time} {who}: {names}")
        return warnings

    def explain_plan(self) -> str:
        """Describe why the plan includes and orders tasks the way it does."""
        if not self.plan and not self.skipped:
            return "No tasks are due today."
        used = sum(t.duration_minutes for t in self.plan)
        lines = [
            f"Plan for {self.owner.name}: {used} of {self.owner.available_minutes} "
            "minutes used. Tasks were chosen by priority (high first) to fit your "
            "available time, then listed in start-time order."
        ]
        for task in self.plan:
            when = f" at {task.time}" if task.time else ""
            lines.append(
                f"  - {task.description} for {task.pet_name}{when} "
                f"({task.duration_minutes} min, {task.priority} priority)"
            )
        for task in self.skipped:
            lines.append(
                f"  Skipped: {task.description} for {task.pet_name} "
                f"({task.duration_minutes} min) - not enough time left"
            )
        return "\n".join(lines)
