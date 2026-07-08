from pawpal_system import Owner, Pet, CareTask, Priority, TaskCategory, DailyPlan, Scheduler
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
        notes="Before breakfast, around neighborhood"
    )
    
    task2 = CareTask(
        title="Feed Biscuit",
        category=TaskCategory.FEEDING,
        duration_minutes=10,
        priority=Priority.HIGH,
        pet_id="dog_001",
        recurring=True,
        notes="Use special food for sensitive stomach"
    )
    
    task3 = CareTask(
        title="Playtime & Enrichment",
        category=TaskCategory.ENRICHMENT,
        duration_minutes=20,
        priority=Priority.MEDIUM,
        pet_id="dog_001",
        recurring=True,
        notes="Fetch or tug toy"
    )
    
    task4 = CareTask(
        title="Feed Whiskers",
        category=TaskCategory.FEEDING,
        duration_minutes=5,
        priority=Priority.HIGH,
        pet_id="cat_001",
        recurring=True,
        notes="Wet food preferred"
    )
    
    task5 = CareTask(
        title="Litter Box Cleaning",
        category=TaskCategory.ENRICHMENT,
        duration_minutes=5,
        priority=Priority.MEDIUM,
        pet_id="cat_001",
        recurring=True,
        notes="Clean and refresh litter"
    )
    
    # Create a Daily Plan
    today = date.today()
    plan = DailyPlan(
        date=today,
        owner=owner,
        pets={"dog_001": dog, "cat_001": cat}
    )
    
    # Add tasks to the plan
    plan.add_task(task1)
    plan.add_task(task2)
    plan.add_task(task3)
    plan.add_task(task4)
    plan.add_task(task5)
    
    # Create a Scheduler and generate the plan
    scheduler = Scheduler(owner)
    scheduled_tasks = scheduler.generate_plan(plan, plan.unscheduled_tasks)
    
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
    
    # Print unscheduled tasks if any
    if plan.unscheduled_tasks:
        print("\n⚠️  COULD NOT SCHEDULE (ran out of time):")
        for task in plan.unscheduled_tasks:
            print(f"  - {task.title} ({task.duration_minutes} min, {task.priority.name} priority)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()




