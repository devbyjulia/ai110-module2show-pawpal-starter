# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
Three core actions for PawPal+ are entering a pet, adding or editing care tasks with a duration and priority, and generating a daily plan.
- What classes did you include, and what responsibilities did you assign to each?
The classes included are Owner, Pet, Task and Scheduler. Owner retrieves all pet tasks and assigns the owner name, available time, and pets.
Pet assigns pet name, species, and tasks. Task contains a description, duration, priority, frequency, and completion status.
Scheduler generates a plan for the owner's pets, sorts tasks by priority, and explains the rationale for the plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, my design changed. I added an extra attribute to the Task class called ```pet_name```.
This is a string that indicates what pet the task refers to.
Without it, the user may not know which task applies to which pet when all the tasks are collected into a single list.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler considers four things: the owner's available minutes for the day, each task's priority,
each task's preferred start time, and whether the task is due (not completed and its due date has arrived).
The `Owner` class has a `preferences` field, but the scheduler doesn't use it yet.
- How did you decide which constraints mattered most?
Available time is the hard limit, since the plan can't use more minutes than the owner has.
Priority comes next and decides which tasks fit, because skipping meds or a feeding matters more than skipping playtime.
Start time only decides the order of the chosen tasks, so a high-priority task later in the day isn't pushed out by less important tasks earlier in the morning.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
My conflict detection (`Scheduler.detect_conflicts`) only flags tasks that start at exactly the same time.
It does not check whether task durations overlap. For example, a 30-minute walk at 08:30 and a feeding at 08:45 overlap in real life, but the scheduler will not warn about them because their start times are different.
The check groups tasks by start time in a dictionary, so it only needs one pass over the plan, and it returns warning messages instead of raising errors, so a conflict never crashes the app.
- Why is that tradeoff reasonable for this scenario?
Most pet care tasks are short (feeding, meds, brushing) and owners usually think in terms of "what happens at 8:30", so two tasks booked for the same start time is the most common and most obvious mistake to catch.
Keeping the check simple made it easy to understand, test, and explain. The cost is that it can miss real conflicts between longer tasks. If I needed to catch those, the plan can sort by start time, keep track of when the latest task ends, and warn if the next task starts before that.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI tools to help me brainstorm ideas, explain design proposals and functionality, summarize changes and updates, debug, test, and explain the reasoning behind generated code.
- What kinds of prompts or questions were most helpful?
Prompts that asked for reasoning, clarification, and a summary of options or potential implementations were most helpful. These prompts helped me to brainstorm, decide on a course of action, and determine if a fix/change was reasonable or needed adjustments.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I asked Claude for a test plan covering edge cases in my scheduler. It suggested about 30 tests in five priority groups: empty inputs, time-budget limits, same-time ties, recurrence dates and input validation. I didn't add them all. I chose the duplicate-task tests, because Claude had flagged them as a likely real bug: two tasks with identical details might be treated as the same task. A bug in the code mattered more to me than extra coverage of behavior that already worked, so I left the rest of the plan for later.
- How did you evaluate or verify what the AI suggested?
I had Claude write the tests before changing any code, so I could see whether the bug was real. Two of the five new tests failed. remove_task(second) removed the first task instead of the one I passed in. And complete_task accepted a lookalike task that had never been added to the pet. Because Task is a dataclass, == compared tasks by their values. Once the failing tests confirmed this, I approved the fix: @dataclass(eq=False), which makes tasks compare by object identity. Running the full suite after the fix also caught a side effect: three of the new tests broke because their setup used == to check that the tasks were duplicates. After that was updated to compare the tasks' fields, all 35 tests passed. Writing the tests first meant I accepted the fix because of evidence, not just because the AI said it would work.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I added 35 tests in `tests/test_pawpal.py` covering task validation (rejecting times like `8:30` or `noon`), sorting by time and priority, plan generation when time is tight, filtering by pet and status, recurring tasks (daily/weekly due dates, month rollover, completing twice), conflict detection, and duplicate-looking tasks being treated as separate tasks.
- Why were these tests important?
The scheduler's choices are easy to get subtly wrong, like dropping a high-priority task or planning a task that isn't due yet. The tests use fixed dates so the recurring-task results don't change depending on the day they run.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I'm very confident in the core logic, since every main feature has both happy-path and edge-case tests and all of them pass.
- What edge cases would you test next if you had more time?
  - A task that exactly uses up the remaining minutes, and an owner with 0 minutes available.
  - A long high-priority task being skipped while a shorter, lower-priority task still fits in the leftover time.
  - Overlapping durations (e.g. a 30-min walk at 08:30 and a feeding at 08:45), once conflict detection supports them.
  - Renaming a pet, since each task stores the pet's name as a copy and would keep the old name.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm most satisfied with the implementation of the dataclasses and the UI. I was able to confirm the functionality with pytest and manual app testing. The UI is clean, delivers pertinent warnings/notifications, and displays schedules in a nice tabular form. Adding owners, pets, and tasks work as expected, scheduling returns the correct result, and some edge cases were considered in the final design.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - **Overlap-based conflict detection:** warn when task durations overlap, not just when start times match.
  - **Use owner preferences:** `Owner.preferences` exists but the scheduler ignores it, e.g. "walks in the morning".
  - **Edit and remove tasks in the UI:** `Pet.edit_task()` and `Pet.remove_task()` work but have no buttons in the app.
  - **Save data:** tasks only last for the browser session; saving to a file would keep them between visits.
  - **Link tasks to pets directly:** each task stores a copy of the pet's name, so renaming a pet would leave old names behind.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Even if I don't understand code produced by AI, I can exercise my own judgement and reject, modify, or iterate upon the output to produce something within the scope of the project and my own abilities.
