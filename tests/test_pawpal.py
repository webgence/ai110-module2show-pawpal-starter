import sys
import os
from pathlib import Path

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import date, time, timedelta

from pawpal_system import (
    Owner, Pet, CareTask, Priority, TaskCategory, TaskStatus, DailyPlan, Scheduler
)



class TestTaskCompletion:
    """Test that task completion status changes correctly."""

    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() sets completed to True."""
        # Create a task
        task = CareTask(
            title="Morning Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_id="dog_001",
            completed=False
        )
        
        # Task should start as incomplete
        assert task.completed is False
        
        # Mark task as complete
        task.mark_complete()
        
        # Task should now be complete
        assert task.completed is True


class TestTaskAddition:
    """Test that adding tasks to a plan works correctly."""

    def test_add_task_to_daily_plan(self):
        """Verify that adding a task to DailyPlan increases task count."""
        # Create owner and pets
        owner = Owner(name="Jordan", email="jordan@example.com")
        dog = Pet(
            pet_id="dog_001",
            name="Biscuit",
            species="Golden Retriever",
            age=3,
            size="large",
            energy_level="high"
        )
        
        # Create a daily plan
        plan = DailyPlan(
            date=date.today(),
            owner=owner,
            pets={"dog_001": dog}
        )
        
        # Plan should start with no unscheduled tasks
        assert len(plan.unscheduled_tasks) == 0
        
        # Create a task
        task = CareTask(
            title="Morning Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_id="dog_001"
        )
        
        # Add task to plan
        plan.add_task(task)
        
        # Verify task count increased
        assert len(plan.unscheduled_tasks) == 1
        assert plan.unscheduled_tasks[0] == task
        
        # Add another task
        task2 = CareTask(
            title="Feeding",
            category=TaskCategory.FEEDING,
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_id="dog_001"
        )
        plan.add_task(task2)
        
        # Verify count increased to 2
        assert len(plan.unscheduled_tasks) == 2


class TestTaskRemoval:
    """Test that removing tasks from a plan works correctly."""

    def test_remove_task_from_daily_plan(self):
        """Verify that removing a task decreases task count."""
        owner = Owner(name="Jordan", email="jordan@example.com")
        dog = Pet(
            pet_id="dog_001",
            name="Biscuit",
            species="Golden Retriever",
            age=3,
            size="large",
            energy_level="high"
        )
        
        plan = DailyPlan(date=date.today(), owner=owner, pets={"dog_001": dog})
        
        task = CareTask(
            title="Morning Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_id="dog_001"
        )
        
        plan.add_task(task)
        assert len(plan.unscheduled_tasks) == 1
        
        # Remove the task
        plan.remove_task(task)
        
        # Verify task was removed
        assert len(plan.unscheduled_tasks) == 0


class TestSchedulerBehavior:
    """Test the scheduler sorting, filtering, and conflict detection behavior."""

    def test_sort_tasks_by_preferred_time_and_priority(self):
        owner = Owner(name="Jordan", email="jordan@example.com")
        scheduler = Scheduler(owner)

        task_a = CareTask(
            title="Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.MEDIUM,
            pet_id="dog_001",
            preferred_start_time=time(hour=10, minute=0)
        )
        task_b = CareTask(
            title="Feed",
            category=TaskCategory.FEEDING,
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_id="dog_001",
            preferred_start_time=time(hour=9, minute=0)
        )
        task_c = CareTask(
            title="Groom",
            category=TaskCategory.GROOMING,
            duration_minutes=20,
            priority=Priority.HIGH,
            pet_id="dog_001",
            recurring=True,
            preferred_start_time=time(hour=9, minute=0)
        )

        sorted_tasks = scheduler._sort_tasks([task_a, task_b, task_c])

        assert sorted_tasks[0] is task_c
        assert sorted_tasks[1] is task_b
        assert sorted_tasks[2] is task_a

    def test_generate_plan_schedules_tasks_in_chronological_order(self):
        owner = Owner(name="Jordan", email="jordan@example.com")
        pet = Pet(
            pet_id="dog_001",
            name="Biscuit",
            species="Golden Retriever",
            age=3,
            size="large",
            energy_level="high"
        )
        plan = DailyPlan(date=date.today(), owner=owner, pets={"dog_001": pet})
        scheduler = Scheduler(owner)

        task_morning = CareTask(
            title="Morning Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_id="dog_001",
            preferred_start_time=time(hour=8, minute=30)
        )
        task_afternoon = CareTask(
            title="Afternoon Play",
            category=TaskCategory.ENRICHMENT,
            duration_minutes=45,
            priority=Priority.MEDIUM,
            pet_id="dog_001",
            preferred_start_time=time(hour=14, minute=0)
        )

        plan.add_task(task_afternoon)
        plan.add_task(task_morning)

        scheduled, warnings = scheduler.generate_plan(plan, plan.unscheduled_tasks)

        assert len(scheduled) == 2
        assert scheduled[0].start_time < scheduled[1].start_time
        assert [task.task.title for task in scheduled] == ["Morning Walk", "Afternoon Play"]
        assert warnings == []

    def test_filter_tasks_by_status_and_pet_name(self):
        owner = Owner(name="Jordan", email="jordan@example.com")
        dog = Pet(
            pet_id="dog_001",
            name="Biscuit",
            species="Golden Retriever",
            age=3,
            size="large",
            energy_level="high"
        )
        plan = DailyPlan(date=date.today(), owner=owner, pets={"dog_001": dog})

        task_pending = CareTask(
            title="Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_id="dog_001"
        )
        task_complete = CareTask(
            title="Feed",
            category=TaskCategory.FEEDING,
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_id="dog_001"
        )

        plan.add_task(task_pending)
        plan.add_task(task_complete)
        task_complete.mark_complete()

        completed_tasks = plan.filter_tasks(status=TaskStatus.COMPLETED)
        assert len(completed_tasks) == 1
        assert completed_tasks[0].title == "Feed"

        biscuits_tasks = plan.filter_tasks(pet_name="Biscuit")
        assert len(biscuits_tasks) == 2

    def test_conflict_detection_returns_warning(self):
        owner = Owner(name="Jordan", email="jordan@example.com")
        pet = Pet(
            pet_id="dog_001",
            name="Biscuit",
            species="Golden Retriever",
            age=3,
            size="large",
            energy_level="high"
        )
        plan = DailyPlan(date=date.today(), owner=owner, pets={"dog_001": pet})
        scheduler = Scheduler(owner)

        task1 = CareTask(
            title="Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_id="dog_001",
            preferred_start_time=time(hour=8, minute=0)
        )
        task2 = CareTask(
            title="Feed",
            category=TaskCategory.FEEDING,
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_id="dog_001",
            preferred_start_time=time(hour=8, minute=0)
        )

        plan.add_task(task1)
        plan.add_task(task2)

        scheduled, warnings = scheduler.generate_plan(plan, plan.unscheduled_tasks)

        assert len(scheduled) == 2
        assert any("conflicts with" in warning for warning in warnings)

    def test_scheduler_flags_duplicate_times(self):
        owner = Owner(name="Jordan", email="jordan@example.com")
        pet = Pet(
            pet_id="dog_001",
            name="Biscuit",
            species="Golden Retriever",
            age=3,
            size="large",
            energy_level="high"
        )
        plan = DailyPlan(date=date.today(), owner=owner, pets={"dog_001": pet})
        scheduler = Scheduler(owner)

        task1 = CareTask(
            title="Walk",
            category=TaskCategory.WALK,
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_id="dog_001",
            preferred_start_time=time(hour=8, minute=0)
        )
        task2 = CareTask(
            title="Feed",
            category=TaskCategory.FEEDING,
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_id="dog_001",
            preferred_start_time=time(hour=8, minute=0)
        )

        plan.add_task(task1)
        plan.add_task(task2)

        scheduled, warnings = scheduler.generate_plan(plan, plan.unscheduled_tasks)

        assert len(scheduled) == 2
        assert len(warnings) >= 1
        assert any("conflicts with" in warning and "8:00" in warning for warning in warnings)


class TestRecurringTasks:
    """Test recurring task rollover behavior."""

    def test_mark_complete_creates_next_occurrence(self):
        task = CareTask(
            title="Feed Biscuit",
            category=TaskCategory.FEEDING,
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_id="dog_001",
            recurring=True,
            recurrence="daily",
            due_date=date.today()
        )

        next_task = task.mark_complete()

        assert task.completed is True
        assert next_task is not None
        assert next_task.completed is False
        assert next_task.recurrence == "daily"
        assert next_task.due_date == date.today() + timedelta(days=1)
        assert next_task.title == "Feed Biscuit"
