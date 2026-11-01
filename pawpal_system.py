from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care task, e.g. a walk or feeding."""
    title: str
    duration_minutes: int
    priority: str = "medium"      # "low", "medium", or "high"
    frequency: str = "daily"      # "daily" or "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def is_due_today(self) -> bool:
        """Return True if this task should be scheduled today."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def edit_task(self, task: Task, **changes) -> None:
        """Update fields on an existing task."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        pass


@dataclass
class Owner:
    """A pet owner, their pets, and their daily constraints."""
    name: str
    available_minutes: int = 60
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        pass


@dataclass
class Scheduler:
    """Builds a daily care plan for an owner's pets."""
    owner: Owner

    def generate_plan(self) -> list[Task]:
        """Choose and order today's tasks to fit the owner's available time."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority."""
        pass

    def explain_plan(self) -> str:
        """Describe why the plan includes and orders tasks the way it does."""
        pass
