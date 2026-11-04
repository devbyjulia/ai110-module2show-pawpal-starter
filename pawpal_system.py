from dataclasses import dataclass, field, replace
from datetime import date

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = ("daily", "weekly")


@dataclass
class Task:
    """A single pet care task, e.g. a walk or feeding."""
    description: str
    duration_minutes: int
    time: str = ""                # preferred start time as "HH:MM", or "" for any time
    priority: str = "medium"      # "low", "medium", or "high"
    frequency: str = "daily"      # "daily" or "weekly"
    completed: bool = False
    last_completed: date | None = None
    pet_name: str = ""            # set by Pet.add_task()

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}")

    def mark_complete(self, on: date | None = None) -> None:
        """Mark this task as done, recording the completion date."""
        self.completed = True
        self.last_completed = on or date.today()

    def is_due_today(self, today: date | None = None) -> bool:
        """Return True if this task should be scheduled today."""
        today = today or date.today()
        if self.last_completed is None:
            return True
        if self.frequency == "daily":
            return self.last_completed < today
        return (today - self.last_completed).days >= 7


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


@dataclass
class Scheduler:
    """Builds a daily care plan for an owner's pets."""
    owner: Owner
    plan: list[Task] = field(default_factory=list, init=False)
    skipped: list[Task] = field(default_factory=list, init=False)

    def generate_plan(self, today: date | None = None) -> list[Task]:
        """Choose and order today's tasks to fit the owner's available time."""
        due = [t for t in self.owner.get_all_tasks() if t.is_due_today(today)]
        self.plan, self.skipped = [], []
        minutes_left = self.owner.available_minutes
        for task in self.sort_by_priority(due):
            if task.duration_minutes <= minutes_left:
                self.plan.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append(task)
        return self.plan

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority, then start time, then shortest first."""
        return sorted(
            tasks,
            key=lambda t: (PRIORITY_RANK[t.priority], t.time or "99:99", t.duration_minutes),
        )

    def explain_plan(self) -> str:
        """Describe why the plan includes and orders tasks the way it does."""
        if not self.plan and not self.skipped:
            return "No tasks are due today."
        used = sum(t.duration_minutes for t in self.plan)
        lines = [
            f"Plan for {self.owner.name}: {used} of {self.owner.available_minutes} "
            "minutes used. Tasks are ordered by priority (high first), then by "
            "start time, then shortest first."
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
