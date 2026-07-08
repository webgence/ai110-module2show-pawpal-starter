from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta
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


class TaskStatus(Enum):
    """Status categories for a care task."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    SKIPPED = "skipped"


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
    recurrence: Optional[str] = None
    due_date: Optional[date] = None
    preferred_start_time: Optional[time] = None
    notes: str = ""
    completed: bool = False
    scheduled: bool = False
    skipped: bool = False

    def estimate_effort(self) -> int:
        """Return estimated effort in minutes (duration of task)."""
        return self.duration_minutes

    def mark_complete(self) -> Optional["CareTask"]:
        """Mark this task complete and return next occurrence if recurring."""
        self.completed = True
        if self.recurrence not in {"daily", "weekly"}:
            return None

        interval = timedelta(days=1 if self.recurrence == "daily" else 7)
        next_due = (self.due_date or date.today()) + interval

        return CareTask(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            pet_id=self.pet_id,
            recurring=self.recurring,
            recurrence=self.recurrence,
            due_date=next_due,
            preferred_start_time=self.preferred_start_time,
            notes=self.notes,
        )

    @property
    def status(self) -> TaskStatus:
        """Return the current status of the task."""
        if self.completed:
            return TaskStatus.COMPLETED
        if self.skipped:
            return TaskStatus.SKIPPED
        if self.scheduled:
            return TaskStatus.SCHEDULED
        return TaskStatus.PENDING

    def should_schedule(self) -> bool:
        """Return true when the task is eligible for scheduling."""
        return not self.completed and not self.skipped


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
        """Add an unscheduled task to the plan if it is eligible."""
        if task.should_schedule():
            self.unscheduled_tasks.append(task)

    def remove_task(self, task: CareTask) -> None:
        """Remove a task from unscheduled tasks."""
        if task in self.unscheduled_tasks:
            self.unscheduled_tasks.remove(task)

    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task with time slot to the plan."""
        scheduled_task.task.scheduled = True
        self.scheduled_tasks.append(scheduled_task)
        if scheduled_task.task in self.unscheduled_tasks:
            self.unscheduled_tasks.remove(scheduled_task.task)

    def get_all_tasks(self) -> List[CareTask]:
        """Return all tasks currently in the plan."""
        return [sched.task for sched in self.scheduled_tasks] + list(self.unscheduled_tasks)

    def get_tasks_by_pet(self, pet_id: str) -> List[CareTask]:
        """Return all tasks for a given pet."""
        return [task for task in self.get_all_tasks() if task.pet_id == pet_id]

    def get_tasks_by_pet_name(self, pet_name: str) -> List[CareTask]:
        """Return all tasks for a pet identified by name."""
        pet_ids = [pet.pet_id for pet in self.pets.values() if pet.name.lower() == pet_name.lower()]
        return [task for task in self.get_all_tasks() if task.pet_id in pet_ids]

    def get_tasks_by_status(self, status: TaskStatus) -> List[CareTask]:
        """Return all tasks matching a given status."""
        return [task for task in self.get_all_tasks() if task.status == status]

    def filter_tasks(
        self,
        status: Optional[TaskStatus] = None,
        pet_name: Optional[str] = None,
    ) -> List[CareTask]:
        """Filter tasks by completion status and/or pet name."""
        pet_ids = None
        if pet_name is not None:
            pet_ids = {
                pet.pet_id
                for pet in self.pets.values()
                if pet.name.lower() == pet_name.lower()
            }
            if not pet_ids:
                return []

        return [
            task
            for task in self.get_all_tasks()
            if (status is None or task.status == status)
            and (pet_ids is None or task.pet_id in pet_ids)
        ]

    def explain_plan(self, scheduled_tasks: List[ScheduledTask]) -> str:
        """Generate a human-readable explanation of the schedule."""
        if not scheduled_tasks:
            return f"No tasks scheduled for {self.date}."

        explanation = f"Daily plan for {self.date}:\n"
        for sched_task in sorted(scheduled_tasks, key=lambda x: x.start_time):
            task = sched_task.task
            pet_name = next(
                (p.name for p in self.pets.values() if p.pet_id == task.pet_id),
                "Unknown"
            )
            explanation += (
                f"  {sched_task.start_time.strftime('%H:%M')} - {sched_task.end_time.strftime('%H:%M')}: "
                f"{task.title} ({task.duration_minutes} min, {task.priority.name}) "
                f"for {pet_name}\n"
            )
        return explanation


class Scheduler:
    """Handles scheduling logic for daily plans across multiple pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.warnings: List[str] = []

    def generate_plan(
        self, plan: DailyPlan, available_tasks: List[CareTask]
    ) -> tuple[List[ScheduledTask], List[str]]:
        """
        Schedule tasks into the daily plan, respecting constraints and priorities.
        Returns list of successfully scheduled tasks and warning messages.
        """
        self.warnings = []
        tasks = [task for task in available_tasks if task.should_schedule()]
        tasks = self._sort_tasks(tasks)

        schedule_start = time(hour=8, minute=0)
        schedule_end = time(hour=20, minute=0)
        scheduled: List[ScheduledTask] = []
        current_time = schedule_start

        for task in tasks:
            task_start = task.preferred_start_time or current_time
            if task_start < current_time:
                task_start = current_time

            existing_conflict = self._find_conflict_at(scheduled, task, task_start, task.duration_minutes)
            if existing_conflict is not None:
                pet_name = plan.pets.get(task.pet_id).name if task.pet_id in plan.pets else task.pet_id
                conflict_name = existing_conflict.task.title
                self.warnings.append(
                    f"Task '{task.title}' for {pet_name} conflicts with '{conflict_name}' at {task_start.strftime('%H:%M')}. "
                    "It will be moved to the next open slot."
                )

            scheduled_start = self._find_next_available_start(
                scheduled,
                task,
                task_start,
                task.duration_minutes,
                schedule_end,
            )

            if scheduled_start is None:
                task.skipped = True
                self.warnings.append(
                    f"Task '{task.title}' for {plan.pets.get(task.pet_id).name if task.pet_id in plan.pets else task.pet_id} "
                    "could not fit into today's schedule and was skipped."
                )
                continue

            task_end = self._add_minutes_to_time(scheduled_start, task.duration_minutes)
            scheduled_task = ScheduledTask(task=task, start_time=scheduled_start, end_time=task_end)
            scheduled.append(scheduled_task)
            current_time = task_end

        return scheduled, self.warnings

    def validate_schedule(self, scheduled_tasks: List[ScheduledTask]) -> bool:
        """Check for conflicts and time availability."""
        for i, task1 in enumerate(scheduled_tasks):
            for task2 in scheduled_tasks[i + 1 :]:
                if task1.conflicts_with(task2):
                    return False
        return True

    def _sort_tasks(self, tasks: List[CareTask]) -> List[CareTask]:
        """Sort tasks by preferred time, priority, and recurrence."""
        return sorted(
            tasks,
            key=lambda t: (
                t.preferred_start_time or time(hour=23, minute=59),
                -t.priority.value,
                not t.recurring,
                t.duration_minutes,
            ),
        )

    def _add_minutes_to_time(self, start_time: time, minutes: int) -> time:
        """Add minutes to a time object."""
        from datetime import timedelta, datetime
        dt = datetime.combine(date.today(), start_time)
        new_dt = dt + timedelta(minutes=minutes)
        return new_dt.time()

    def _find_next_available_start(
        self,
        scheduled_tasks: List[ScheduledTask],
        task: CareTask,
        candidate_start: time,
        duration_minutes: int,
        schedule_end: time,
    ) -> Optional[time]:
        """Find the next available time slot for a task."""
        candidate = candidate_start
        while True:
            candidate_end = self._add_minutes_to_time(candidate, duration_minutes)
            if candidate_end > schedule_end:
                return None

            proposed = ScheduledTask(task=task, start_time=candidate, end_time=candidate_end)
            conflict = next(
                (existing for existing in scheduled_tasks if proposed.conflicts_with(existing)),
                None,
            )
            if conflict is None:
                return candidate

            candidate = conflict.end_time
            if candidate >= schedule_end:
                return None

    def _find_conflict_at(
        self,
        scheduled_tasks: List[ScheduledTask],
        task: CareTask,
        start_time: time,
        duration_minutes: int,
    ) -> Optional[ScheduledTask]:
        """Find a scheduled task conflict for a proposed time slot."""
        proposed = ScheduledTask(
            task=task,
            start_time=start_time,
            end_time=self._add_minutes_to_time(start_time, duration_minutes),
        )
        return next(
            (existing for existing in scheduled_tasks if proposed.conflicts_with(existing)),
            None,
        )

    def filter_tasks_by_pet(self, tasks: List[CareTask], pet_id: str) -> List[CareTask]:
        """Filter tasks for a specific pet."""
        return [task for task in tasks if task.pet_id == pet_id]

    def filter_tasks_by_status(self, tasks: List[CareTask], status: TaskStatus) -> List[CareTask]:
        """Filter tasks by task status."""
        return [task for task in tasks if task.status == status]
