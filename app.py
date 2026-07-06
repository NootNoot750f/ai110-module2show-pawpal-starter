from datetime import date, time

import streamlit as st
from pawpal_system import (
    Owner,
    Pet,
    Plan,
    Scheduler,
    Task,
    filterTasks,
    sortByTime,
)

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

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# The Owner lives in the session "vault" so it survives Streamlit's reruns.
# Create it once; on every later rerun we reuse the same persistent instance.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(id="owner-1", name=owner_name)
owner = st.session_state.owner
owner.name = owner_name  # keep the model in sync with the input box

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and new_pet_name.strip():
        pet_id = f"pet-{len(owner.getPets()) + 1}"
        pet = Pet(id=pet_id, name=new_pet_name.strip(), type=species)
        # Give every pet a default plan so added tasks have a home
        # (Plan is the source of truth for tasks).
        pet.addPlan(
            Plan(
                id=f"plan-{pet_id}",
                name="Daily Care Plan",
                description=f"Daily care tasks for {pet.name}",
                createdAt=date.today(),
            )
        )
        owner.addPet(pet)  # <-- the class method that handles the form data
        st.success(f"Added {pet.name} 🐾")

st.divider()

st.subheader("Add a Task")
pets = owner.getPets()
if not pets:
    st.info("Add a pet first — tasks belong to a pet's plan.")
else:
    pet_names = [p.name for p in pets]
    with st.form("add_task_form", clear_on_submit=True):
        target_name = st.selectbox("For which pet?", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        task_desc = st.text_input("Description", value="")
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            due = st.date_input("Due date", value=date.today())
            repeat = st.selectbox("Repeats", ["none", "daily", "weekly"])
        with col2:
            due_time = st.time_input("Time of day", value=time(8, 0))
            duration = st.number_input(
                "Duration (min)", min_value=5, max_value=240, value=30, step=5
            )
        if st.form_submit_button("Add task") and task_title.strip():
            pet = pets[pet_names.index(target_name)]
            plan = pet.getPlans()[0]
            task_id = f"{pet.id}-task-{len(plan.getTasks()) + 1}"
            plan.addTask(  # <-- the class method that handles the form data
                Task(
                    id=task_id,
                    title=task_title.strip(),
                    description=task_desc,
                    priority=priority,
                    dueDate=due,
                    dueTime=due_time,
                    durationMinutes=int(duration),
                    recurrence=None if repeat == "none" else repeat,
                )
            )
            st.success(f"Added '{task_title}' for {pet.name}")

st.divider()

st.subheader("Complete or Skip a Task")
st.caption(
    "A daily/weekly task rolls forward off its own due date. Completing keeps "
    "it as a done-log entry; skipping drops it. Both create the next occurrence."
)
complete_pets = owner.getPets()
if not complete_pets:
    st.info("Add a pet and a task first.")
else:
    cp_names = [p.name for p in complete_pets]
    cp_name = st.selectbox("Pet", cp_names, key="complete_pet")
    cp = complete_pets[cp_names.index(cp_name)]
    cp_plan = cp.getPlans()[0]
    cp_pending = [t for t in cp_plan.getTasks() if not t.completed]
    if not cp_pending:
        st.caption("No pending tasks for this pet.")
    else:
        cp_labels = [f"{t.title} (due {t.dueDate})" for t in cp_pending]
        cp_pick = st.selectbox("Task", cp_labels, key="complete_task")
        picked = cp_pending[cp_labels.index(cp_pick)]
        done_col, skip_col = st.columns(2)
        with done_col:
            if st.button("Mark complete"):
                spawned = cp_plan.completeTask(picked)  # kept as history
                msg = f"Completed '{picked.title}'."
                if spawned is not None:
                    msg += f" Next occurrence created for {spawned.dueDate}."
                st.success(msg)
        with skip_col:
            if st.button("Skip"):
                spawned = cp_plan.skipTask(picked)  # dropped, no log entry
                msg = f"Skipped '{picked.title}'."
                if spawned is not None:
                    msg += f" Next occurrence created for {spawned.dueDate}."
                st.info(msg)

st.divider()

st.subheader("Current Pets & Tasks")

# Filter controls: narrow the list by status and/or priority before display.
fcol1, fcol2 = st.columns(2)
with fcol1:
    status_filter = st.selectbox("Filter status", ["all", "pending", "done"])
with fcol2:
    priority_filter = st.selectbox("Filter priority", ["all", "low", "medium", "high"])

if not owner.getPets():
    st.info("No pets yet. Add one above.")
for pet in owner.getPets():
    st.markdown(f"**{pet.name}** ({pet.type})")
    tasks = filterTasks(
        pet.getTaskSheet().getTaskList(),
        status=None if status_filter == "all" else status_filter,
        priority=None if priority_filter == "all" else priority_filter,
    )
    tasks = sortByTime(tasks)  # chronological agenda order
    if tasks:
        st.table(
            [
                {
                    "time": t.dueTime.strftime("%H:%M") if t.dueTime else "all day",
                    "title": t.title,
                    "priority": t.priority,
                    "due": str(t.dueDate),
                    "repeats": t.recurrence or "once",
                    "status": "done" if t.completed else "pending",
                }
                for t in tasks
            ]
        )
    else:
        st.caption("No matching tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption(
    "Places timed tasks at their exact time and packs untimed tasks into the "
    "gaps around them, in priority order."
)

if st.button("Generate schedule"):
    all_tasks = owner.getAllTasks()
    if not all_tasks:
        st.warning("No tasks to schedule yet. Add some above.")
    else:
        scheduler = Scheduler()

        # Warn about tasks whose intended times collide before ordering them.
        conflicts = scheduler.detectConflicts(all_tasks)
        for earlier, later in conflicts:
            st.warning(
                f"⚠ '{earlier.title}' ({earlier.dueTime.strftime('%H:%M')}) "
                f"overlaps '{later.title}' ({later.dueTime.strftime('%H:%M')})"
            )

        events = scheduler.buildSchedule(all_tasks)
        st.write(f"Proposed schedule ({len(events)} events):")
        st.table(
            [
                {
                    "date": e.scheduledTime.strftime("%Y-%m-%d"),
                    "time": e.scheduledTime.strftime("%H:%M"),
                    "task": e.task.title,
                    "kind": "fixed" if e.task.dueTime is not None else "floating",
                    "priority": e.task.priority,
                    "minutes": e.durationMinutes,
                }
                for e in events
            ]
        )
