import os
import sys
from datetime import date

# Allow importing pawpal_system.py from the project root when running from tests/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, Plan, Task


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
