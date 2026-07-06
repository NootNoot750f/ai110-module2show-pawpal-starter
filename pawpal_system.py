"""PawPal system class skeleton.

Generated from diagrams/uml.mmd. Method bodies are left as stubs
to be implemented.

Design notes:
- Plan is the single source of truth for Tasks. A TaskSheet is a *derived
  view*: Pet.getTaskSheet() rebuilds one from the pet's plans on demand, so
  there is never a second stored copy of a task to fall out of sync.
- Scheduler reads a list of Tasks and produces an ordered list of Events
  (a Task placed at a specific time).
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: str
    dueDate: date
    completed: bool = False

    def markComplete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def updateTask(self, updates: dict) -> None:
        """Apply a dict of field -> value changes (id is immutable)."""
        editable = {"title", "description", "priority", "dueDate", "completed"}
        for key, value in updates.items():
            if key in editable:
                setattr(self, key, value)


@dataclass
class Event:
    """A Task placed at a specific time on the schedule."""

    id: str
    task: Task
    scheduledTime: datetime
    durationMinutes: int = 0


@dataclass
class TaskSheet:
    """A read-only, aggregated view of a pet's tasks.

    Built by Pet.getTaskSheet() from the pet's plans. Do not add tasks
    here directly -- add them to a Plan (the source of truth) instead.
    """

    petId: str
    tasks: List[Task] = field(default_factory=list)

    def getTaskList(self) -> List[Task]:
        """Return all tasks in this sheet."""
        return self.tasks

    def filterByPriority(self, priority: str) -> List[Task]:
        """Return tasks matching the given priority (case-insensitive)."""
        return [t for t in self.tasks if t.priority.lower() == priority.lower()]


@dataclass
class Scheduler:
    """Turns a flat list of tasks into an ordered schedule of events.

    Tradeoff: tasks are laid into consecutive fixed-length slots by urgency
    (priority, then due date) rather than being placed at each task's exact
    due time. This keeps the schedule simple and gap-free at the cost of not
    honoring precise due times.
    """

    slotMinutes: int = 30

    # Lower rank = more urgent. Unknown priorities sort last.
    PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def prioritize(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by urgency (priority, then due date)."""
        return sorted(
            tasks,
            key=lambda t: (self.PRIORITY_RANK.get(t.priority.lower(), 99), t.dueDate),
        )

    def buildSchedule(self, tasks: List[Task], start: Optional[datetime] = None) -> List[Event]:
        """Place pending tasks into consecutive time slots as ordered events."""
        if start is None:
            start = datetime.now()

        pending = [task for task in tasks if not task.completed]
        ordered = self.prioritize(pending)

        events: List[Event] = []
        slot = start
        for task in ordered:
            events.append(
                Event(
                    id=f"evt-{task.id}",
                    task=task,
                    scheduledTime=slot,
                    durationMinutes=self.slotMinutes,
                )
            )
            slot = slot + timedelta(minutes=self.slotMinutes)
        return events


@dataclass
class Plan:
    id: str
    name: str
    description: str
    createdAt: date
    tasks: List[Task] = field(default_factory=list)

    def addTask(self, task: Task) -> None:
        """Add a task to this plan."""
        self.tasks.append(task)

    def getTasks(self) -> List[Task]:
        """Return all tasks in this plan."""
        return self.tasks


@dataclass
class Pet:
    id: str
    name: str
    type: str
    plans: List[Plan] = field(default_factory=list)

    def addPlan(self, plan: Plan) -> None:
        """Add a plan to this pet."""
        self.plans.append(plan)

    def getPlans(self) -> List[Plan]:
        """Return all plans for this pet."""
        return self.plans

    def getTaskSheet(self) -> TaskSheet:
        """Build a fresh TaskSheet by aggregating tasks across all plans."""
        tasks = [task for plan in self.plans for task in plan.getTasks()]
        return TaskSheet(petId=self.id, tasks=tasks)


@dataclass
class Owner:
    id: str
    name: str
    pets: List[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def getPets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def getAllTasks(self) -> List[Task]:
        """Gather every task across all of the user's pets.

        Delegates to each pet's derived TaskSheet so all task reads flow
        through the same path (Plan is the source of truth).
        """
        return [
            task
            for pet in self.pets
            for task in pet.getTaskSheet().getTaskList()
        ]
