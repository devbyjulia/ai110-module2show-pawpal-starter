import streamlit as st
from pawpal_system import Owner, Task, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
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

    if st.button("Add task"):
        try:
            pet.add_task(Task(task_title, int(duration), priority=priority))
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
            st.table([
                {
                    "Pet": t.pet_name,
                    "Task": t.description,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                    "Status": "Done" if t.completed else "Pending",
                }
                for t in filtered_tasks
            ])
        else:
            st.info("No tasks match these filters.")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
