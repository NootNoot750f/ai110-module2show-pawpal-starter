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
from datetime import date, datetime
from typing import List


@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: str
    dueDate: date
    completed: bool = False

    def markComplete(self) -> None:
        pass

    def updateTask(self, updates) -> None:
        pass


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
        pass

    def filterByPriority(self, priority: str) -> List[Task]:
        pass


@dataclass
class Scheduler:
    """Turns a flat list of tasks into an ordered schedule of events."""

    def buildSchedule(self, tasks: List[Task]) -> List[Event]:
        pass

    def prioritize(self, tasks: List[Task]) -> List[Task]:
        pass


@dataclass
class Plan:
    id: str
    name: str
    description: str
    createdAt: date
    tasks: List[Task] = field(default_factory=list)

    def addTask(self, task: Task) -> None:
        pass

    def getTasks(self) -> List[Task]:
        pass


@dataclass
class Pet:
    id: str
    name: str
    type: str
    plans: List[Plan] = field(default_factory=list)

    def addPlan(self, plan: Plan) -> None:
        pass

    def getPlans(self) -> List[Plan]:
        pass

    def getTaskSheet(self) -> TaskSheet:
        """Build a fresh TaskSheet by aggregating tasks across all plans."""
        pass


@dataclass
class User:
    id: str
    name: str
    pets: List[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        pass

    def getPets(self) -> List[Pet]:
        pass
