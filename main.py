from pawpal_system import Owner, Pet, CareTask, Priority, TaskCategory, TaskStatus, DailyPlan, Scheduler
from datetime import date, time


def main():
    # Create an Owner
    owner = Owner(
        name="Jordan",
        email="jordan@example.com",
        preferences=["morning walks", "prefer grooming on weekends"],
        daily_available_minutes=480  # 8 hours
    )
    
    # Create two Pets
    dog = Pet(
        pet_id="dog_001",
        name="Biscuit",
        species="Golden Retriever",
        age=3,
        size="large",
        energy_level="high",
        care_notes=["needs 2 walks daily", "sensitive stomach - special food only"]
    )
    
    cat = Pet(
        pet_id="cat_001",
        name="Whiskers",
        species="Tabby Cat",
        age=5,
        size="small",
        energy_level="medium",
        care_notes=["indoor only", "arthritis - monitor activity"]
    )
    
    # Create at least three Tasks with different priorities and pets
    task1 = CareTask(
        title="Morning Walk",
        category=TaskCategory.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
        pet_id="dog_001",
        recurring=True,
        recurrence="daily",
        due_date=date.today(),
        preferred_start_time=time(hour=8, minute=0),
        notes="Before breakfast, around neighborhood"
    )
    
    task2 = CareTask(
        title="Feed Biscuit",
        category=TaskCategory.FEEDING,
        duration_minutes=10,
        priority=Priority.HIGH,
        pet_id="dog_001",
        recurring=True,
        recurrence="daily",
        due_date=date.today(),
        notes="Use special food for sensitive stomach"
    )

    task3 = CareTask(
        title="Playtime & Enrichment",
        category=TaskCategory.ENRICHMENT,
        duration_minutes=20,
        priority=Priority.MEDIUM,
        pet_id="dog_001",
        recurring=True,
        recurrence="weekly",
        due_date=date.today(),
        notes="Fetch or tug toy"
    )

    task4 = CareTask(
        title="Feed Whiskers",
        category=TaskCategory.FEEDING,
        duration_minutes=5,
        priority=Priority.HIGH,
        pet_id="cat_001",
        recurring=True,
        recurrence="daily",
        due_date=date.today(),
        preferred_start_time=time(hour=8, minute=0),
        notes="Wet food preferred"
    )

    task5 = CareTask(
        title="Litter Box Cleaning",
        category=TaskCategory.ENRICHMENT,
        duration_minutes=5,
        priority=Priority.MEDIUM,
        pet_id="cat_001",
        recurring=True,
        recurrence="weekly",
        due_date=date.today(),
        notes="Clean and refresh litter"
    )

    # Mark one task complete to test status filtering and auto-create next occurrence
    next_task = task2.mark_complete()
    
    # Create a Daily Plan
    today = date.today()
    plan = DailyPlan(
        date=today,
        owner=owner,
        pets={"dog_001": dog, "cat_001": cat}
    )
    
    # Add tasks to the plan out of logical order
    plan.add_task(task3)
    plan.add_task(task5)
    plan.add_task(task1)
    plan.add_task(task4)
    plan.add_task(task2)
    if next_task is not None:
        plan.add_task(next_task)
    
    # Create a Scheduler and generate the plan
    scheduler = Scheduler(owner)
    scheduled_tasks, warnings = scheduler.generate_plan(plan, plan.unscheduled_tasks)
    
    # Add scheduled tasks to the plan
    for scheduled_task in scheduled_tasks:
        plan.add_scheduled_task(scheduled_task)
    
    # Print Today's Schedule
    print("=" * 60)
    print("🐾 PawPal+ DAILY SCHEDULE 🐾")
    print("=" * 60)
    print(f"Owner: {owner.name} ({owner.email})")
    print(f"Date: {today}")
    print(f"Available Time: {owner.get_availability()} minutes\n")
    
    # Print pets
    print("Pets in care:")
    for pet in plan.pets.values():
        print(f"  - {pet.name} ({pet.species}): {pet.energy_level} energy, {pet.size} size")
        if pet.care_notes:
            for note in pet.care_notes:
                print(f"    📝 {note}")
    
    print("\n" + "-" * 60)
    print("TODAY'S SCHEDULE:")
    print("-" * 60)
    
    # Print the schedule explanation
    explanation = plan.explain_plan(plan.scheduled_tasks)
    print(explanation)

    # Print any scheduler warnings
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    # Print filtered results to verify sorting and filtering
    print("\nFiltered task views:")
    completed_tasks = plan.filter_tasks(status=TaskStatus.COMPLETED)
    print(f"- Completed tasks ({len(completed_tasks)}):")
    for task in completed_tasks:
        print(f"    • {task.title} ({task.pet_id})")

    whiskers_tasks = plan.filter_tasks(pet_name="Whiskers")
    print(f"- Tasks for Whiskers ({len(whiskers_tasks)}):")
    for task in whiskers_tasks:
        print(f"    • {task.title} [{task.status.value}] ")

    # Print unscheduled tasks if any
    if plan.unscheduled_tasks:
        print("\n⚠️  COULD NOT SCHEDULE (ran out of time):")
        for task in plan.unscheduled_tasks:
            print(f"  - {task.title} ({task.duration_minutes} min, {task.priority.name} priority)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()




