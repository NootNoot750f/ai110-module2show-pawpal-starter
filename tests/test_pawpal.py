import os
import sys
from datetime import date, time

# Allow importing pawpal_system.py from the project root when running from tests/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, Plan, Scheduler, Task, sortByTime


def make_task(task_id="task-1"):
    return Task(
        id=task_id,
        title="Feed Bindi",
        description="Feed Bindi her favorite cat food.",
        priority="high",
        dueDate=date(2026, 7, 5),
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False

    task.markComplete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(id="pet-1", name="Bindi", type="cat")
    plan = Plan(
        id="plan-1",
        name="Daily Care Plan",
        description="A plan for daily care tasks for Bindi",
        createdAt=date.today(),
    )
    pet.addPlan(plan)

    before = len(pet.getTaskSheet().getTaskList())
    plan.addTask(make_task())
    after = len(pet.getTaskSheet().getTaskList())

    assert after == before + 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sortByTime should return timed tasks in clock order regardless of
    the order they were added in."""
    noon = Task(
        id="noon", title="Noon walk", description="", priority="low",
        dueDate=date(2026, 7, 5), dueTime=time(12, 0),
    )
    morning = Task(
        id="morning", title="Morning feed", description="", priority="low",
        dueDate=date(2026, 7, 5), dueTime=time(8, 0),
    )
    evening = Task(
        id="evening", title="Evening meds", description="", priority="low",
        dueDate=date(2026, 7, 5), dueTime=time(18, 0),
    )

    # Deliberately out of order on input.
    ordered = sortByTime([evening, noon, morning])

    assert [t.id for t in ordered] == ["morning", "noon", "evening"]


def test_sort_by_time_untimed_task_sorts_after_timed_same_day():
    """A task with no dueTime is treated as all-day and should sort AFTER
    timed tasks that fall on the same date."""
    timed = Task(
        id="timed", title="Vet visit", description="", priority="low",
        dueDate=date(2026, 7, 5), dueTime=time(9, 0),
    )
    untimed = Task(
        id="untimed", title="Buy food", description="", priority="low",
        dueDate=date(2026, 7, 5), dueTime=None,
    )

    ordered = sortByTime([untimed, timed])

    assert [t.id for t in ordered] == ["timed", "untimed"]


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_completing_daily_task_creates_next_day_task():
    """Marking a daily recurring task complete should append a fresh task
    for the following day and leave the original as a completed done-log."""
    plan = Plan(
        id="plan-1", name="Daily Care", description="",
        createdAt=date.today(),
    )
    daily = Task(
        id="feed", title="Feed Bindi", description="", priority="high",
        dueDate=date(2026, 7, 5), recurrence="daily", interval=1,
    )
    plan.addTask(daily)

    next_task = plan.completeTask(daily)

    # Original stays as history, marked done.
    assert daily.completed is True
    # A new occurrence was produced for the following day...
    assert next_task is not None
    assert next_task.dueDate == date(2026, 7, 6)
    assert next_task.completed is False
    # ...and it lives in the plan (source of truth) alongside the original.
    assert next_task in plan.getTasks()
    assert len(plan.getTasks()) == 2


def test_completing_one_shot_task_creates_no_recurrence():
    """A non-recurring task should not spawn a follow-up when completed."""
    plan = Plan(
        id="plan-1", name="Daily Care", description="",
        createdAt=date.today(),
    )
    one_shot = make_task()  # recurrence defaults to None
    plan.addTask(one_shot)

    next_task = plan.completeTask(one_shot)

    assert next_task is None
    assert len(plan.getTasks()) == 1


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflict_warnings_flags_duplicate_times():
    """conflictWarnings should flag two pending tasks booked at the exact
    same date and time."""
    scheduler = Scheduler()
    first = Task(
        id="a", title="Feed cat", description="", priority="high",
        dueDate=date(2026, 7, 5), dueTime=time(8, 0),
    )
    second = Task(
        id="b", title="Give meds", description="", priority="high",
        dueDate=date(2026, 7, 5), dueTime=time(8, 0),
    )

    warnings = scheduler.conflictWarnings([first, second])

    assert len(warnings) == 1
    assert "Feed cat" in warnings[0]
    assert "Give meds" in warnings[0]


def test_detect_conflicts_flags_overlapping_windows():
    """detectConflicts should catch tasks whose time windows overlap even
    when they do not start at the same moment (8:00 for 30 min vs 8:15)."""
    scheduler = Scheduler()
    first = Task(
        id="a", title="Feed cat", description="", priority="high",
        dueDate=date(2026, 7, 5), dueTime=time(8, 0), durationMinutes=30,
    )
    second = Task(
        id="b", title="Give meds", description="", priority="high",
        dueDate=date(2026, 7, 5), dueTime=time(8, 15), durationMinutes=30,
    )

    conflicts = scheduler.detectConflicts([first, second])

    assert len(conflicts) == 1
    earlier, later = conflicts[0]
    assert earlier.id == "a"
    assert later.id == "b"


def test_no_conflict_for_back_to_back_tasks():
    """Tasks that touch but do not overlap (8:00-8:30 then 8:30-9:00)
    should NOT be reported as conflicting."""
    scheduler = Scheduler()
    first = Task(
        id="a", title="Feed cat", description="", priority="high",
        dueDate=date(2026, 7, 5), dueTime=time(8, 0), durationMinutes=30,
    )
    second = Task(
        id="b", title="Walk dog", description="", priority="high",
        dueDate=date(2026, 7, 5), dueTime=time(8, 30), durationMinutes=30,
    )

    assert scheduler.detectConflicts([first, second]) == []


# ---------------------------------------------------------------------------
# Edge case: a pet with no tasks
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_returns_empty_sheet():
    """A pet with no plans/tasks should yield an empty task list without
    raising."""
    pet = Pet(id="pet-1", name="Bindi", type="cat")

    assert pet.getTaskSheet().getTaskList() == []
