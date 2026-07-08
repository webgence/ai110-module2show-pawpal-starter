# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

Use the following command to run the PawPal+ unit tests:

```bash
pytest tests/test_pawpal.py -v
```

These tests cover the core scheduling engine and task management behaviors, including:

- task sorting and chronological plan generation
- preferred-time conflict detection and warning behavior
- task filtering by pet and status
- recurring task rollover for daily tasks

Successful test output:

```bash
9 passed in 0.04s
```

**Confidence Level:** ⭐⭐⭐

## Features

- **Sorting by time & priority:** `Scheduler._sort_tasks()` orders tasks by preferred start time (earliest first), then by priority (HIGH → LOW), recurring-first, then by duration.
- **Preferred-time conflict detection:** `Scheduler._find_conflict_at()` checks if a task’s requested `preferred_start_time` overlaps an existing `ScheduledTask` and returns the conflicting slot.
- **Automatic slot-finding (scheduling):** `Scheduler._find_next_available_start()` searches forward from a candidate time to find the next open slot within the working window (`08:00–20:00`).
- **Conflict warnings & adjustments:** `Scheduler.generate_plan()` emits human-readable warnings when a task’s preferred time conflicts or must be moved; it still attempts to place the task in the next available slot.
- **Overlap validation:** `ScheduledTask.conflicts_with()` and `Scheduler.validate_schedule()` verify overlapping time windows and help ensure the final schedule has no conflicts.
- **Daily/weekly recurrence rollover:** `CareTask.mark_complete()` marks a task completed and, for `recurrence` == "daily" or "weekly", returns a new `CareTask` with `due_date` advanced (next occurrence).
- **Task lifecycle flags & status:** tasks carry `completed`, `scheduled`, and `skipped` flags; the read-only `CareTask.status` maps these to `TaskStatus` (`PENDING`, `SCHEDULED`, `COMPLETED`, `SKIPPED`).
- **Filtering & queries:** `DailyPlan.filter_tasks()`, `DailyPlan.get_tasks_by_pet_name()`, and `Scheduler.filter_tasks_by_*()` support filtering by pet name and status for UI and testing.
- **Human-readable plan explanation:** `DailyPlan.explain_plan()` produces a chronological textual summary of scheduled tasks for display or logging.
- **Time arithmetic helper:** `Scheduler._add_minutes_to_time()` handles minute-based addition to `time` objects safely for slot calculations.
- **UI integration hooks:** `app.py` uses the scheduler methods to render sorted unscheduled tasks, scheduled tables, and present warnings with `st.warning` / `st.success` for clear owner-facing messaging.

## 📐 Smarter Scheduling

This app implements a lightweight scheduling engine with task sorting, filtering, conflict detection, and recurring task handling.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting behavior | `Scheduler._sort_tasks()` | Orders tasks by preferred start time, priority, recurrence, and duration |
| Filtering behavior | `DailyPlan.filter_tasks()`, `DailyPlan.get_tasks_by_pet_name()`, `Scheduler.filter_tasks_by_pet()`, `Scheduler.filter_tasks_by_status()` | Allows filtering by pet name and completion status |
| Conflict detection | `ScheduledTask.conflicts_with()`, `Scheduler._find_conflict_at()`, `Scheduler._find_next_available_start()` | Detects overlapping slots and returns warnings rather than crashing |
| Recurring task logic | `CareTask.mark_complete()` | Automatically creates the next daily/weekly task instance when a recurring task is completed |

## Demo Walkthrough

Main UI features and user actions

- Owner setup: enter owner name, email, and available minutes per day (sidebar). Save owner info to initialize the scheduler.
- Pet management: add, list, and view pets (left column). Each pet has `pet_id`, `name`, `species`, `age`, `size`, and `energy_level`.
- Task management: create care tasks with title, category, duration, priority, optional preferred start time and recurrence. Tasks appear under "Unscheduled Tasks" and are shown sorted by scheduler logic.
- Schedule generation: press "Generate Today's Schedule" to run the scheduling engine. The app shows a table of scheduled tasks, any unscheduled tasks, and warnings about conflicts.

Example workflow

1. Add owner info in the sidebar and click **Save Owner Info**.
2. In **Pets**, click *Add a New Pet* — enter pet name, species, age, size, and energy level, then add.
3. In **Tasks**, click *Add a New Task* — pick the pet, set title, category, duration, priority and an optional preferred start time (e.g., 08:00). Save the task.
4. Repeat to add more tasks for the same or other pets.
5. Click **Generate Today's Schedule**. The app will use the `Scheduler` to sort tasks, allocate times, and display conflict warnings if tasks shared preferred times.
6. Review the scheduled table and any warnings. If tasks were adjusted, you can edit or re-run with different preferences.

Key Scheduler behaviors demonstrated

- Sorting: tasks are ordered by preferred start time (earliest first), then by priority, recurring tasks prioritized, then by duration.
- Preferred-time conflict detection: if two tasks request the same start time, the scheduler emits a clear warning and moves the later task to the next open slot.
- Automatic slot-finding: the scheduler finds the next available slot within working hours (08:00–20:00) when a preferred slot is unavailable.
- Recurring rollover: completing a daily/weekly recurring task creates the next occurrence automatically.
- Warnings and fallbacks: tasks that cannot fit are marked `skipped` and listed under unscheduled tasks with a warning.

Sample CLI output from running `main.py`

```
Generating schedule for 2026-07-08...
Scheduled 3 tasks.
Warning: Task 'Feed' for Biscuit conflicts with 'Morning Walk' at 08:00. It will be moved to the next open slot.

Daily plan for 2026-07-08:
  08:00 - 08:30: Morning Walk (30 min, HIGH) for Biscuit
  08:30 - 08:40: Feed (10 min, HIGH) for Biscuit
  14:00 - 14:45: Afternoon Play (45 min, MEDIUM) for Biscuit

Unscheduled tasks:
  - Groom (30 min) — Whiskers

All done.
```

You can follow the example workflow interactively in `app.py` or use `main.py` as a quick CLI runner for debugging.