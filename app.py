import streamlit as st
from datetime import date, time
from pawpal_system import Pet, Owner, CareTask, Priority, TaskCategory, DailyPlan, Scheduler


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+** — your pet care planning assistant!

This app helps you plan care tasks for your pet(s) based on time constraints and priorities.
"""
)

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="", daily_available_minutes=480)
    st.session_state.pets = {}
    st.session_state.daily_plan = None
    st.session_state.scheduler = None

if st.session_state.scheduler is None:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

st.divider()

# Sidebar for Owner Setup
with st.sidebar:
    st.subheader("👤 Owner Setup")
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name or "Jordan")
    owner_email = st.text_input("Owner email", value=st.session_state.owner.email or "jordan@example.com")
    available_minutes = st.number_input(
        "Available time (minutes/day)", 
        min_value=60, 
        max_value=1440, 
        value=st.session_state.owner.daily_available_minutes
    )
    
    if st.button("Save Owner Info"):
        st.session_state.owner = Owner(
            name=owner_name,
            email=owner_email,
            daily_available_minutes=available_minutes
        )
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.success("Owner info saved! 📝")

st.divider()

# Main Content Columns
col_left, col_right = st.columns([1, 1])

# Left Column: Add/Manage Pets
with col_left:
    st.subheader("🐕 Pets")
    
    with st.expander("Add a New Pet", expanded=False):
        pet_name = st.text_input("Pet name", key="pet_name_input")
        pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"], key="pet_species_input")
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, key="pet_age_input")
        pet_size = st.selectbox("Size", ["small", "medium", "large"], key="pet_size_input")
        pet_energy = st.selectbox("Energy level", ["low", "medium", "high"], key="pet_energy_input")
        
        if st.button("Add Pet"):
            if pet_name and st.session_state.owner.name:
                pet_id = f"{pet_species}_{len(st.session_state.pets)}"
                new_pet = Pet(
                    pet_id=pet_id,
                    name=pet_name,
                    species=pet_species,
                    age=pet_age,
                    size=pet_size,
                    energy_level=pet_energy
                )
                st.session_state.pets[pet_id] = new_pet
                st.success(f"Added {pet_name}! 🎉")
                st.rerun()
            else:
                st.error("Please enter owner name and pet name.")
    
    # Display current pets
    if st.session_state.pets:
        st.write("**Current Pets:**")
        for pet_id, pet in st.session_state.pets.items():
            st.write(f"- {pet.name} ({pet.species}, {pet.energy_level} energy)")
    else:
        st.info("No pets yet. Add one above!")

# Right Column: Add/Manage Tasks
with col_right:
    st.subheader("📋 Tasks")
    
    if st.session_state.pets:
        with st.expander("Add a New Task", expanded=False):
            task_title = st.text_input("Task title", key="task_title_input", value="Morning walk")
            selected_pet = st.selectbox(
                "Pet",
                options=list(st.session_state.pets.keys()),
                format_func=lambda x: st.session_state.pets[x].name,
                key="task_pet_select"
            )
            task_category = st.selectbox(
                "Category",
                [cat.value for cat in TaskCategory],
                key="task_category_select"
            )
            task_duration = st.number_input(
                "Duration (minutes)", 
                min_value=1, 
                max_value=240, 
                value=30,
                key="task_duration_input"
            )
            task_priority = st.selectbox(
                "Priority",
                ["HIGH", "MEDIUM", "LOW"],
                key="task_priority_select"
            )
            task_recurring = st.checkbox("Recurring?", key="task_recurring_checkbox")
            task_notes = st.text_area("Notes", key="task_notes_input")
            
            if st.button("Add Task"):
                if task_title and selected_pet:
                    new_task = CareTask(
                        title=task_title,
                        category=TaskCategory(task_category),
                        duration_minutes=task_duration,
                        priority=Priority[task_priority],
                        pet_id=selected_pet,
                        recurring=task_recurring,
                        notes=task_notes
                    )
                    # Initialize daily plan if needed
                    if st.session_state.daily_plan is None:
                        st.session_state.daily_plan = DailyPlan(
                            date=date.today(),
                            owner=st.session_state.owner,
                            pets=st.session_state.pets
                        )
                    st.session_state.daily_plan.add_task(new_task)
                    st.success(f"Added task: {task_title}! ✅")
                    st.rerun()
                else:
                    st.error("Please enter task title and select a pet.")
        
        # Display current tasks
        if st.session_state.daily_plan and st.session_state.daily_plan.unscheduled_tasks:
            sorted_tasks = st.session_state.scheduler._sort_tasks(
                st.session_state.daily_plan.unscheduled_tasks.copy()
            )
            task_rows = [
                {
                    "Task": task.title,
                    "Pet": st.session_state.pets[task.pet_id].name if task.pet_id in st.session_state.pets else "Unknown",
                    "Preferred Start": task.preferred_start_time.strftime("%H:%M") if task.preferred_start_time else "Any",
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority.name,
                    "Recurring": "Yes" if task.recurring else "No",
                }
                for task in sorted_tasks
            ]
            st.subheader("Unscheduled Tasks")
            st.table(task_rows)
        else:
            st.info("No tasks yet. Add one above!")
    else:
        st.info("Add a pet first to create tasks.")

st.divider()

# Schedule Generation
st.subheader("📅 Generate Schedule")

if st.session_state.owner.name and st.session_state.pets and st.session_state.daily_plan:
    if st.button("Generate Today's Schedule", key="generate_schedule_btn"):
        with st.spinner("Creating your schedule..."):
            scheduled_tasks, warnings = st.session_state.scheduler.generate_plan(
                st.session_state.daily_plan,
                st.session_state.daily_plan.unscheduled_tasks.copy()
            )
            for scheduled_task in scheduled_tasks:
                st.session_state.daily_plan.add_scheduled_task(scheduled_task)

        if warnings:
            st.warning("⚠️ Scheduling note: some tasks were adjusted due to timing conflicts.")
            for warning in warnings:
                st.warning(warning)
        else:
            st.success("Schedule generated with no conflicts! ✅")

        if st.session_state.daily_plan.scheduled_tasks:
            st.subheader("📆 Today's Schedule")
            schedule_rows = [
                {
                    "Start": task.start_time.strftime("%H:%M"),
                    "End": task.end_time.strftime("%H:%M"),
                    "Task": task.task.title,
                    "Pet": st.session_state.pets[task.task.pet_id].name if task.task.pet_id in st.session_state.pets else "Unknown",
                    "Duration": task.task.duration_minutes,
                    "Priority": task.task.priority.name,
                }
                for task in sorted(st.session_state.daily_plan.scheduled_tasks, key=lambda x: x.start_time)
            ]
            st.table(schedule_rows)

        if st.session_state.daily_plan.unscheduled_tasks:
            st.warning("⚠️ Could not schedule the following tasks due to time limits:")
            unscheduled_rows = [
                {
                    "Task": task.title,
                    "Pet": st.session_state.pets[task.pet_id].name if task.pet_id in st.session_state.pets else "Unknown",
                    "Duration": task.duration_minutes,
                    "Priority": task.priority.name,
                }
                for task in st.session_state.daily_plan.unscheduled_tasks
            ]
            st.table(unscheduled_rows)
        else:
            st.success("All tasks fit into today's schedule.")
else:
    st.info("ℹ️ Complete the Owner setup and add at least one pet and task to generate a schedule.")

