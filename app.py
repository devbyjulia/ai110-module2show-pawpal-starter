import streamlit as st
from pawpal_system import Owner, Task, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def task_rows(tasks: list[Task], show_status: bool = False) -> list[dict]:
    """Turn tasks into readable table rows."""
    rows = []
    for t in tasks:
        row = {
            "Time": t.time or "Anytime",
            "Pet": t.pet_name,
            "Task": t.description,
            "Minutes": t.duration_minutes,
            "Priority": PRIORITY_BADGE[t.priority],
            "Repeats": t.frequency,
        }
        if show_status:
            row["Status"] = "✅ Done" if t.completed else "⏳ Pending"
        rows.append(row)
    return rows


def show_conflicts(conflicts: list[str]) -> None:
    """Show each time clash as a warning, with a tip for fixing it."""
    if not conflicts:
        return
    for message in conflicts:
        st.warning(message, icon="⚠️")
    st.caption("💡 Tip: you can only be in one place at a time. Move one of these "
               "tasks to a different start time, or leave its time blank so it "
               "can happen whenever you're free.")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ app.
PawPal+ is a Streamlit app that helps a pet owner plan care tasks for their pet.
"""


)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Add Owner and Pets")
owner_name = st.text_input("Enter your name", placeholder="Julia")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
owner = st.session_state.owner

owner.name = owner_name
owner.available_minutes = int(st.number_input(
    "Minutes available for pet care today", min_value=5, max_value=720,
    value=owner.available_minutes, step=5,
))
scheduler = Scheduler(owner)

pet_name = st.text_input("Enter pet name", placeholder="Smudge")
species = st.text_input("Enter pet species", placeholder="cat")
if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))


st.markdown("### Tasks")
st.caption("Add care tasks for each pet. These feed into the scheduler below.")

if not owner.pets:
    st.info("Add a pet above before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    chosen_pet = st.selectbox("For which pet?", pet_names)
    pet = owner.pets[pet_names.index(chosen_pet)]

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        start_time = st.text_input("Start time (HH:MM, optional)", placeholder="08:00")
    with col5:
        frequency = st.selectbox("Repeats", ["daily", "weekly"])

    if st.button("Add task"):
        try:
            pet.add_task(Task(task_title, int(duration), time=start_time.strip(),
                              priority=priority, frequency=frequency))
            st.success(f"Added '{task_title}' for {pet.name}.")
        except ValueError as e:
            st.error(str(e))

    if owner.get_all_tasks():
        st.write("Current tasks:")
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            pet_filter = st.selectbox("Show pet", ["All"] + pet_names)
        with filter_col2:
            status_filter = st.selectbox("Show status", ["All", "Pending", "Done"])

        filtered_tasks = owner.filter_tasks(
            pet_name=None if pet_filter == "All" else pet_filter,
            completed={"All": None, "Pending": False, "Done": True}[status_filter],
        )
        if filtered_tasks:
            st.table(task_rows(scheduler.sort_by_time(filtered_tasks), show_status=True))
        else:
            st.info("No tasks match these filters.")

        # Warn early, before the owner builds a schedule.
        show_conflicts(scheduler.detect_conflicts(owner.filter_tasks(completed=False)))

        st.markdown("#### Mark a task complete")
        if "flash" in st.session_state:
            st.success(st.session_state.pop("flash"))

        due_now = scheduler.sort_by_time(
            [t for t in owner.get_all_tasks() if t.is_due_today()]
        )
        if due_now:
            to_complete = st.selectbox(
                "Which task did you finish?",
                due_now,
                format_func=lambda t: f"{t.time or 'Anytime'} · {t.description} ({t.pet_name})",
            )
            if st.button("✅ Mark complete"):
                done_pet = next(p for p in owner.pets if to_complete in p.tasks)
                next_task = done_pet.complete_task(to_complete)
                st.session_state.flash = (
                    f"Nice! '{to_complete.description}' for {done_pet.name} is done. "
                    f"Next {next_task.frequency} occurrence is due "
                    f"{next_task.due_date:%a %b %d}."
                )
                st.rerun()  # refresh the tables so the task shows as Done
        else:
            st.caption("🎉 Nothing is due right now.")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("High-priority tasks are picked first to fit your available time, "
           "then the plan is shown in start-time order.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()
    if not plan and not scheduler.skipped:
        st.info("No tasks are due today. Enjoy the time off! 🐾")
    else:
        used = sum(t.duration_minutes for t in plan)
        if plan:
            st.success(f"Scheduled {len(plan)} task(s) using {used} of "
                       f"{owner.available_minutes} minutes.")
            st.table(task_rows(plan))
        else:
            st.error("None of today's tasks fit in your available time.")

        show_conflicts(scheduler.detect_conflicts())

        if scheduler.skipped:
            st.warning(f"⏭️ {len(scheduler.skipped)} task(s) didn't fit and were skipped. "
                       "Add more available minutes or shorten a task to include them.")
            st.table(task_rows(scheduler.skipped))

        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan())
