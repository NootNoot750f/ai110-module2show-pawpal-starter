"""PawPal system class skeleton.

Generated from diagrams/uml.mmd. Method bodies are left as stubs
to be implemented.
"""

from dataclasses import dataclass, field
from datetime import date
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
class TaskSheet:
    petId: str
    tasks: List[Task] = field(default_factory=list)

    def addTaskFromList(self, task: Task) -> None:
        pass

    def getTaskList(self) -> List[Task]:
        pass

    def filterByPriority(self, priority: str) -> List[Task]:
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

    def getEventList(self) -> list:
        pass


@dataclass
class Pet:
    id: str
    name: str
    type: str
    plans: List[Plan] = field(default_factory=list)
    taskSheet: "TaskSheet | None" = None

    def addPlan(self, plan: Plan) -> None:
        pass

    def getPlan(self) -> List[Plan]:
        pass

    def getTaskSheet(self) -> TaskSheet:
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
