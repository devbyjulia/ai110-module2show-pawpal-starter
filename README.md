# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks for their pet.

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

With the virtual environment activated (see [Setup](#setup)), run from the project root:

```bash
# Run the full test suite:
python -m pytest

# Show each test name as it runs:
python -m pytest -v

# Run only tests whose names match a keyword:
python -m pytest -k conflict
```

`pytest.ini` points pytest at the `tests/` folder and adds the project root to the import path, so no extra flags are needed.

Sample test output:

```
============================= test session starts =============================
collected 35 items

tests\test_pawpal.py ...................................                 [100%]

============================= 35 passed in 0.05s ==============================
```

### What the tests cover

All tests are in `tests/test_pawpal.py` and use fixed dates, so results don't depend on the day they're run.

| Area | Happy path | Edge cases |
|------|------------|------------|
| Task basics | Adding tasks to a pet; marking a task complete | Rejects invalid times such as `8:30`, `24:00` and `noon`; a failed `edit_task` leaves the task unchanged |
| Sorting | Tasks given out of order come back in start-time order | Tasks at the same time are ordered by priority; tasks with no time go last |
| Plan generation | Due tasks are picked and listed in start-time order | When time is tight, high-priority tasks are kept and lower ones skipped; completed and not-yet-due tasks are left out |
| Filtering | Filtering by pet, by completion status, or both | An unknown pet name returns an empty list; a new recurring occurrence shows up as pending |
| Recurring tasks | Daily tasks repeat in 1 day, weekly in 7 | Rolling over the end of a month; completing a task twice raises an error; a new occurrence isn't due until its date, and overdue tasks still appear |
| Conflict detection | Warnings for a clash within one pet and across pets | A three-way clash gives one warning; different times, untimed tasks and completed tasks are ignored |
| Duplicate tasks | Two identical-looking tasks are both planned and flagged as a conflict | Removing, editing or completing a task affects only that exact task, and a lookalike task that was never added is rejected |

### Confidence level
 ★ ★ ★ ★ ★

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

Start the app from the project root with:

```bash
streamlit run app.py
```

### Main UI features

The app is one page with three sections, from top to bottom.

| Section | What you can do |
|---------|-----------------|
| **Add Owner and Pets** | Enter your name and how many minutes you have for pet care today (default 60). Add pets by name and species. |
| **Tasks** | Pick a pet and add a task with a title, duration, priority, optional start time (`HH:MM`) and frequency (daily or weekly). View all tasks in a table sorted by start time and filter it by pet and status. See conflict warnings as soon as two pending tasks share a start time. Mark a task that's due today as complete. |
| **Build Schedule** | Click **Generate schedule** to see today's plan, any conflicts in it, any tasks that didn't fit, and a "Why this plan?" explanation. |

Invalid input, such as a start time of `8:30` or `noon`, shows an error message instead of crashing the app. Data is kept in Streamlit's session state, so it lasts until you close or refresh the browser tab.

### Example workflow

1. **Set up the owner.** Enter `Julia` as your name and leave available time at **60 minutes**.
2. **Add pets.** Add `Zack` (dog), then `Smudge` (cat).
3. **Add tasks.** Choose a pet in "For which pet?" and add:

   | Pet | Task | Minutes | Priority | Start time |
   |-----|------|---------|----------|------------|
   | Zack | Morning walk | 30 | high | 08:30 |
   | Zack | Give meds | 5 | high | 08:30 |
   | Zack | Brush Zack | 15 | low | 09:00 |
   | Smudge | Feed Smudge | 5 | high | 09:00 |
   | Smudge | Play with Smudge | 20 | medium | *(blank)* |

   Each task shows a green "Added …" confirmation. The task table lists them in start-time order, with "Play with Smudge" last as **Anytime**.
4. **Check early conflict warnings.** Under the table, two warnings appear before any schedule is built:
   ```
   ⚠️ Conflict at 08:30 for Zack: Morning walk (Zack), Give meds (Zack)
   ⚠️ Conflict at 09:00 across pets: Brush Zack (Zack), Feed Smudge (Smudge)
   ```
   A tip below them suggests moving one task or leaving its time blank.
5. **Try the filters.** Set "Show pet" to `Smudge` to see only Smudge's two tasks, or set "Show status" to `Done` to see completed tasks (none yet).
6. **Generate today's schedule.** Click **Generate schedule**. The five tasks need 75 minutes, but only 60 are available:
   - A success banner reads **"Scheduled 4 task(s) using 60 of 60 minutes."**
   - The plan table shows, in order: Give meds (08:30), Morning walk (08:30), Feed Smudge (09:00), Play with Smudge (Anytime).
   - A warning flags the 08:30 clash that is still in the plan.
   - A second warning says **1 task was skipped**: Brush Zack (low priority, 15 min) didn't fit after the higher-priority tasks were chosen.
   - Opening **"Why this plan?"** shows the scheduler's explanation for each chosen and skipped task.
7. **Mark a task complete.** In "Mark a task complete", choose `08:30 · Morning walk (Zack)` and click **✅ Mark complete**. A message confirms it's done and says when the next daily walk is due (tomorrow). The table now shows the walk as ✅ Done, plus a new pending walk for tomorrow.
8. **Regenerate.** Click **Generate schedule** again. The finished walk and tomorrow's walk are both left out, which frees 30 minutes, so Brush Zack now fits and all four remaining tasks are planned. A new warning appears because Feed Smudge and Brush Zack now share 09:00 in the plan.

### Key Scheduler behaviors shown

| Behavior | Where you see it | Method |
|----------|------------------|--------|
| **Priority decides what fits** | Brush Zack (low) is skipped while all high-priority tasks are kept | `Scheduler.generate_plan()`, `sort_by_priority()` |
| **Time decides the order** | The plan and task table read like a day, with untimed tasks last and ties at the same time broken by priority | `Scheduler.sort_by_time()` |
| **Conflict warnings** | Yellow ⚠️ warnings under the task table and the plan, naming the time, the pet(s) and the tasks | `Scheduler.detect_conflicts()` |
| **Time budget** | The success banner shows minutes used out of minutes available, and skipped tasks are listed with a suggestion | `Scheduler.generate_plan()`, `Scheduler.skipped` |
| **Filtering** | "Show pet" and "Show status" dropdowns | `Owner.filter_tasks()` |
| **Recurring tasks** | Completing a task adds its next occurrence, which isn't scheduled until its due date | `Pet.complete_task()`, `Task.is_due_today()` |
| **Explanation** | The "Why this plan?" expander | `Scheduler.explain_plan()` |

### Sample CLI output from running main.py
```
Today's schedule for Julia:
  08:30    Take Zack for a walk   Zack       5 min  [high]
  08:45    Feed Zack              Zack       3 min  [high]
  09:00    Feed Smudge            Smudge     3 min  [high]
  09:30    Play with Smudge       Smudge    10 min  [medium]

Tasks out of order:
  13:30    Clean Goldie's tank    Goldie    25 min  [high]
  08:30    Feed Goldie            Goldie     2 min  [high]

Sorted tasks for Gary:
  08:30    Feed Goldie            Goldie     2 min  [high]
  13:30    Clean Goldie's tank    Goldie    25 min  [high]

Conflicting task:
  13:30    Photoshoot with Goldie Goldie    25 min  [high]

Conflict warnings:  ["Conflict at 13:30 for Goldie: Clean Goldie's tank (Goldie), Photoshoot with Goldie (Goldie)"]
```
