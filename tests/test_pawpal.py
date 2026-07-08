import sys
import os
from pathlib import Path

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import date

from pawpal_system import (
    Owner, Pet, CareTask, Priority, TaskCategory, DailyPlan, Scheduler
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
