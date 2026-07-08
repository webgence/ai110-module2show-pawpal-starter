from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import Dict, List, Optional


# Enums for type safety
class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def __lt__(self, other: Priority) -> bool:
        """Compare priority levels (less than)."""
        return self.value < other.value

    def __le__(self, other: Priority) -> bool:
        """Compare priority levels (less than or equal)."""
        return self.value <= other.value


class TaskCategory(Enum):
    """Types of pet care tasks."""
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"


@dataclass
class Owner:
    name: str
    email: str
    preferences: List[str] = field(default_factory=list)
    daily_available_minutes: int = 0

    def add_preference(self, preference: str) -> None:
        """Add a preference if not already present."""
        if preference not in self.preferences:
            self.preferences.append(preference)

    def remove_preference(self, preference: str) -> None:
        """Remove a preference."""
        if preference in self.preferences:
            self.preferences.remove(preference)

    def get_availability(self) -> int:
        """Return available minutes per day."""
        return self.daily_available_minutes


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    size: str
    energy_level: str
    care_notes: List[str] = field(default_factory=list)

    def update_health_notes(self, note: str) -> None:
        """Add a health or care note to the pet's record."""
        self.care_notes.append(note)

    def needs_today(self) -> List[str]:
        """Return list of care notes/needs for this pet."""
        return self.care_notes.copy()


@dataclass
class CareTask:
    title: str
    category: TaskCategory
    duration_minutes: int
    priority: Priority
    pet_id: str
    recurring: bool = False
    notes: str = ""
    completed: bool = False

    def estimate_effort(self) -> int:
        """Return estimated effort in minutes (duration of task)."""
        return self.duration_minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class ScheduledTask:
    """A CareTask with assigned start and end times."""
    task: CareTask
    start_time: time
    end_time: time

    def conflicts_with(self, other: ScheduledTask) -> bool:
        """Check if this task overlaps with another."""
        # Tasks conflict if one starts before the other ends
        return self.start_time < other.end_time and self.end_time > other.start_time


@dataclass
class DailyPlan:
    date: date
    owner: Owner
    pets: Dict[str, Pet] = field(default_factory=dict)
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    unscheduled_tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add an unscheduled task to the plan."""
        self.unscheduled_tasks.append(task)

    def remove_task(self, task: CareTask) -> None:
        """Remove a task from unscheduled tasks."""
        if task in self.unscheduled_tasks:
            self.unscheduled_tasks.remove(task)

    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task with time slot to the plan."""
        self.scheduled_tasks.append(scheduled_task)
        # Remove from unscheduled if present
        if scheduled_task.task in self.unscheduled_tasks:
            self.unscheduled_tasks.remove(scheduled_task.task)

    def explain_plan(self, scheduled_tasks: List[ScheduledTask]) -> str:
        """Generate a human-readable explanation of the schedule."""
        if not scheduled_tasks:
            return f"No tasks scheduled for {self.date}."
        
        explanation = f"Daily plan for {self.date}:\n"
        for sched_task in sorted(scheduled_tasks, key=lambda x: x.start_time):
            task = sched_task.task
            explanation += (
                f"  {sched_task.start_time.strftime('%H:%M')} - {sched_task.end_time.strftime('%H:%M')}: "
                f"{task.title} ({task.duration_minutes} min, {task.priority.name}) "
                f"for {[p.name for p in self.pets.values() if p.pet_id == task.pet_id]}\n"
            )
        return explanation


class Scheduler:
    """Handles scheduling logic for daily plans across multiple pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(
        self, plan: DailyPlan, available_tasks: List[CareTask]
    ) -> List[ScheduledTask]:
        """
        Schedule tasks into the daily plan, respecting constraints and priorities.
        Returns list of successfully scheduled tasks.
        """
        # Prioritize tasks first
        prioritized = self.prioritize_tasks(available_tasks)
        
        scheduled = []
        current_time = time(hour=8, minute=0)  # Start at 8 AM
        
        for task in prioritized:
            # Check if task fits in available time
            task_end = self._add_minutes_to_time(current_time, task.duration_minutes)
            
            # Simple validation: tasks shouldn't go past 8 PM
            if task_end.hour >= 20:
                plan.unscheduled_tasks.append(task)
                continue
            
            # Check for conflicts with existing scheduled tasks
            proposed_scheduled_task = ScheduledTask(
                task=task,
                start_time=current_time,
                end_time=task_end
            )
            
            if not self._has_conflict(proposed_scheduled_task, scheduled):
                scheduled.append(proposed_scheduled_task)
                current_time = task_end
            else:
                plan.unscheduled_tasks.append(task)
        
        return scheduled

    def validate_schedule(self, scheduled_tasks: List[ScheduledTask]) -> bool:
        """Check for conflicts and time availability."""
        for i, task1 in enumerate(scheduled_tasks):
            for task2 in scheduled_tasks[i + 1 :]:
                if task1.conflicts_with(task2):
                    return False
        return True

    def prioritize_tasks(self, tasks: List[CareTask]) -> List[CareTask]:
        """Sort tasks by priority (high to low) and recurrence."""
        # Sort by priority descending, then recurring tasks first
        return sorted(
            tasks,
            key=lambda t: (-t.priority.value, not t.recurring)
        )

    def _add_minutes_to_time(self, start_time: time, minutes: int) -> time:
        """Add minutes to a time object."""
        from datetime import timedelta, datetime
        dt = datetime.combine(date.today(), start_time)
        new_dt = dt + timedelta(minutes=minutes)
        return new_dt.time()

    def _has_conflict(
        self, proposed_task: ScheduledTask, scheduled_tasks: List[ScheduledTask]
    ) -> bool:
        """Check if proposed task conflicts with any scheduled tasks."""
        for scheduled in scheduled_tasks:
            if proposed_task.conflicts_with(scheduled):
                return True
        return False
