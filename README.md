# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's schedule for Julia:
  08:30    Take Zack for a walk   Zack       5 min  [high]
  08:45    Feed Zack              Zack       3 min  [high]
  09:00    Feed Smudge            Smudge     3 min  [high]
  09:30    Play with Smudge       Smudge    10 min  [medium]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ goes beyond a plain task list with four scheduling features. All of them live in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()`, `Scheduler.generate_plan()` | Priority decides what fits; start time decides display order |
| Filtering | `Owner.filter_tasks()` | By pet name, completion status, or both |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns about tasks with the same start time; never crashes |
| Recurring tasks | `Task.mark_complete()`, `Pet.complete_task()`, `Task.is_due_today()` | Daily tasks repeat after 1 day, weekly after 7 |

### Sorting

- **`Scheduler.sort_by_time(tasks)`** returns tasks in start-time order. Ties go to the higher priority, and tasks with no time ("anytime") go last.
- **`Scheduler.sort_by_priority(tasks)`** orders tasks by priority (high first), then start time, then shortest duration.
- **`Scheduler.generate_plan(today)`** uses both sorts in two steps:
  1. It goes through due tasks in priority order and keeps each one that still fits in the owner's `available_minutes`. Tasks that don't fit go to `Scheduler.skipped`.
  2. It reorders the chosen tasks by start time, so the plan reads like a normal day.

  This way, an important task late in the day isn't pushed out by less important tasks earlier in the morning.
- Task times must be in zero-padded 24-hour `"HH:MM"` format, which is checked when a `Task` is created. This guarantees that sorting the time strings gives the correct order.

### Filtering

- **`Owner.filter_tasks(pet_name=None, completed=None)`** returns tasks that match every filter given. A filter left as `None` is skipped, so the filters can be combined:
  - `filter_tasks(pet_name="Zack")` returns only Zack's tasks.
  - `filter_tasks(completed=False)` returns tasks that are still pending.
  - `filter_tasks(pet_name="Zack", completed=False)` returns Zack's pending tasks.
- An unknown pet name returns an empty list instead of an error.
- In the Streamlit app, the "Show pet" and "Show status" dropdowns above the task table use this method.

### Conflict detection

- **`Scheduler.detect_conflicts(tasks=None)`** checks the current plan (or a list of tasks you pass in) for two or more tasks with the same start time.
- It groups tasks by start time in a dictionary, so it only needs one pass. Tasks with no time are ignored.
- It returns a list of warning messages instead of raising an error, and an empty list means no conflicts. Each warning says whether the clash is for one pet or across pets:
  ```
  Conflict at 08:30 for Zack: Give meds (Zack), Morning walk (Zack)
  Conflict at 09:00 across pets: Feed Smudge (Smudge), Brush Zack (Zack)
  ```
- **Tradeoff:** only exact start-time matches are caught. Overlapping durations are not, such as a 30-minute walk at 08:30 and a feeding at 08:45. See `reflection.md` section 2b.

### Recurring tasks

- Each `Task` is one occurrence of a care activity, with a `frequency` of `"daily"` or `"weekly"` and an optional `due_date`.
- **`Task.mark_complete(on)`** marks the task done and returns a new `Task` for the next occurrence. Its `due_date` is the completion date plus `timedelta(days=1)` for daily tasks or `timedelta(days=7)` for weekly ones. Completing the same task twice raises an error, so duplicate occurrences can't be created by accident.
- **`Pet.complete_task(task, on)`** marks a task complete and adds its next occurrence to the pet. This is the method to call when a task is finished.
- **`Task.is_due_today(today)`** returns `True` only for tasks that aren't completed and whose `due_date` has arrived (or that have no due date). Overdue tasks still show up. `generate_plan()` uses this to skip finished tasks and future occurrences.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
