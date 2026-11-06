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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
My conflict detection (`Scheduler.detect_conflicts`) only flags tasks that start at exactly the same time.
It does not check whether task durations overlap. For example, a 30-minute walk at 08:30 and a feeding at 08:45
overlap in real life, but the scheduler will not warn about them because their start times are different.
The check groups tasks by start time in a dictionary, so it only needs one pass over the plan, and it returns
warning messages instead of raising errors, so a conflict never crashes the app.
- Why is that tradeoff reasonable for this scenario?
Most pet care tasks are short (feeding, meds, brushing) and owners usually think in terms of "what happens at 8:30",
so two tasks booked for the same start time is the most common and most obvious mistake to catch.
Keeping the check simple made it easy to understand, test, and explain. The cost is that it can miss real
conflicts between longer tasks. If I needed to catch those, the upgrade is small: sort the plan by start time,
keep track of when the latest task ends, and warn if the next task starts before that.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
