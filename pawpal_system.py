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
from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Set


@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: str
    dueDate: date
    completed: bool = False
    # Time of day the task is meant to happen. None = unscheduled / all-day.
    # Having a real time-of-day is what makes chronological sorting and
    # conflict detection meaningful (a date alone only orders by day).
    dueTime: Optional[time] = None
    # How long the task takes; used to detect overlaps between timed tasks.
    durationMinutes: int = 30
    # Recurrence rule. None = one-shot. "daily"/"weekly" repeat every
    # `interval` days/weeks. The stored task acts as the template; concrete
    # dated occurrences are materialized on demand via expandRecurring().
    recurrence: Optional[str] = None
    interval: int = 1
    # Dates on which a recurring occurrence has been completed. Lets the owner
    # tick off a single day without duplicating the whole template.
    completedDates: Set[date] = field(default_factory=set)

    def markComplete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def markDateComplete(self, on: date) -> None:
        """Mark a single recurring occurrence (on `on`) as completed."""
        self.completedDates.add(on)

    def dueDateTime(self) -> Optional[datetime]:
        """Combine dueDate + dueTime into a datetime, or None if untimed."""
        if self.dueTime is None:
            return None
        return datetime.combine(self.dueDate, self.dueTime)

    def occurrences(self, start: date, end: date) -> List[date]:
        """Return the dates this task falls on within [start, end] inclusive.

        A one-shot task yields its single dueDate (if in range); a recurring
        task yields every repeat that lands in the window.
        """
        if self.recurrence is None:
            return [self.dueDate] if start <= self.dueDate <= end else []

        step_days = self.interval if self.recurrence == "daily" else 7 * self.interval
        step = timedelta(days=step_days)
        dates: List[date] = []
        current = self.dueDate
        while current < start:  # fast-forward into the window
            current += step
        while current <= end:
            dates.append(current)
            current += step
        return dates

    def nextOccurrence(self) -> Optional["Task"]:
        """Build the next instance of a recurring task, or None if one-shot.

        Advances from this task's OWN due date so the series keeps a fixed
        cadence no matter when you act on it (complete a Monday task late and
        the next is still Tuesday): "daily" -> dueDate + 1 day (x interval),
        "weekly" -> + 1 week (x interval). timedelta does real calendar math,
        so month/year rollover is handled for free (2026-12-31 -> 2027-01-01)
        -- no manual "if day > 31" logic. The new instance keeps the same
        recurrence, so the chain continues each time it rolls forward.
        """
        if self.recurrence not in ("daily", "weekly"):
            return None
        step = (
            timedelta(days=self.interval)
            if self.recurrence == "daily"
            else timedelta(weeks=self.interval)
        )
        newDate = self.dueDate + step
        base = self.id.split("@")[0]  # drop any prior "@date" suffix
        return replace(
            self,
            id=f"{base}@{newDate.isoformat()}",
            dueDate=newDate,
            completed=False,
            completedDates=set(),  # fresh instance starts with a clean slate
        )

    def updateTask(self, updates: dict) -> None:
        """Apply a dict of field -> value changes (id is immutable)."""
        editable = {
            "title", "description", "priority", "dueDate", "completed",
            "dueTime", "durationMinutes", "recurrence", "interval",
        }
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

    Fixed vs floating: a task WITH a dueTime is "fixed" and is placed at its
    exact date+time (a vet appointment or a feeding stays put, regardless of
    priority). A task WITHOUT a dueTime is "floating" (an anytime chore) and is
    packed, in urgency order, into the earliest free gap that does not collide
    with anything already scheduled.

    Tradeoff: floating tasks are packed onto their own due date starting from a
    fixed DAY_START hour using a greedy first-fit -- simple and predictable,
    but not guaranteed to be the tightest possible packing, and it assumes an
    open-ended day (no working-hours cap).
    """

    slotMinutes: int = 30  # default duration used only as a fallback
    DAY_START = time(8, 0)  # floating tasks start filling gaps from here

    # Lower rank = more urgent. Unknown priorities sort last.
    PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

    def prioritize(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by urgency (priority, then due date)."""
        return sorted(
            tasks,
            key=lambda t: (self.PRIORITY_RANK.get(t.priority.lower(), 99), t.dueDate),
        )

    def sortByTime(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks chronologically by their time attribute.

        Uses sorted() with a lambda `key`. Because dueTime is a datetime.time,
        it compares chronologically directly -- no need to parse "HH:MM"
        strings (and no "9:00" vs "09:00" padding bug). Untimed/all-day tasks
        (dueTime is None) sort after timed ones on the same day. Delegates to
        the module-level sortByTime() so there is one implementation.
        """
        return sortByTime(tasks)

    def buildSchedule(self, tasks: List[Task]) -> List[Event]:
        """Build a schedule that honors fixed times and packs the rest around them.

        Fixed tasks (with a dueTime) are placed at their exact date+time.
        Floating tasks (no dueTime) are ordered by urgency and greedily dropped
        into the earliest free gap on their own due date -- starting at
        DAY_START and sliding past anything already scheduled -- so they never
        overlap a fixed appointment or each other. Completed tasks are skipped.
        Returns all events sorted chronologically.
        """
        pending = [t for t in tasks if not t.completed]
        floating = self.prioritize([t for t in pending if t.dueTime is None])

        # 1. Fixed tasks (those with a dueTime) go exactly where they are due.
        #    The `if` filter narrows dueTime to non-None for datetime.combine.
        events: List[Event] = [
            Event(
                id=f"evt-{t.id}",
                task=t,
                scheduledTime=datetime.combine(t.dueDate, t.dueTime),
                durationMinutes=t.durationMinutes,
            )
            for t in pending
            if t.dueTime is not None
        ]

        # 2. Floating tasks fill the gaps. We check each candidate slot against
        #    every event placed so far (fixed + earlier floating), so nothing
        #    ever double-books.
        for t in floating:
            duration = timedelta(minutes=t.durationMinutes)
            cursor = datetime.combine(t.dueDate, self.DAY_START)
            clash = self._firstOverlap(cursor, duration, events)
            while clash is not None:
                cursor = clash.scheduledTime + timedelta(minutes=clash.durationMinutes)
                clash = self._firstOverlap(cursor, duration, events)
            events.append(
                Event(
                    id=f"evt-{t.id}",
                    task=t,
                    scheduledTime=cursor,
                    durationMinutes=t.durationMinutes,
                )
            )

        # Sort chronologically; when two events land at the exact same time
        # (a genuine clash), show the more urgent one first so high-priority
        # tasks aren't buried under lower ones. Matches sortByTime's tie-break.
        events.sort(
            key=lambda e: (
                e.scheduledTime,
                self.PRIORITY_RANK.get(e.task.priority.lower(), 99),
            )
        )
        return events

    @staticmethod
    def _firstOverlap(
        startAt: datetime, duration: timedelta, events: List[Event]
    ) -> Optional[Event]:
        """Return the first event whose window overlaps [startAt, startAt+duration).

        Uses strict inequalities so back-to-back events (one ends exactly when
        the next begins) do NOT count as overlapping. Returns None if the slot
        is free.
        """
        end = startAt + duration
        for e in events:
            eStart = e.scheduledTime
            eEnd = eStart + timedelta(minutes=e.durationMinutes)
            if startAt < eEnd and end > eStart:
                return e
        return None

    def detectConflicts(self, tasks: List[Task]) -> List[tuple]:
        """Find pairs of timed tasks whose [start, start+duration) overlap.

        Only tasks with a dueTime (and not completed) can conflict. We sort by
        start time and sweep once, comparing each task against the previous
        one -- an O(n log n) interval-overlap check instead of comparing every
        pair. Returns (earlier, later) Task tuples the owner should resolve.
        """
        # Pair each timed task with its concrete start datetime, then sort.
        timed = [
            (t, datetime.combine(t.dueDate, t.dueTime))
            for t in tasks
            if t.dueTime is not None and not t.completed
        ]
        timed.sort(key=lambda pair: pair[1])

        conflicts: List[tuple] = []
        for (prev, prev_start), (curr, curr_start) in zip(timed, timed[1:]):
            prev_end = prev_start + timedelta(minutes=prev.durationMinutes)
            if prev_end > curr_start:
                conflicts.append((prev, curr))
        return conflicts

    def conflictWarnings(self, tasks: List[Task]) -> List[str]:
        """Lightweight check for tasks booked at the exact same date + time.

        Groups timed, pending tasks into (dueDate, dueTime) slots and returns a
        readable warning string for every slot holding more than one task --
        catching clashes for the same pet or across different pets alike, since
        it works on one flat list. Returns an empty list when nothing clashes;
        it never raises, so callers can just print the warnings and keep going.

        Tradeoff: this only flags tasks that start at the *exact* same time; it
        ignores durations. Two tasks that overlap without starting together --
        an 08:00 task lasting 30 min and an 08:15 task -- are NOT reported here.
        We accept that miss in exchange for an O(n) single-pass hash-bucket
        check that needs no duration data and no sorting. Use detectConflicts()
        when you need true overlapping-window detection (at O(n log n) cost).
        """
        slots: dict = {}
        for t in tasks:
            if t.dueTime is None or t.completed:
                continue
            slots.setdefault((t.dueDate, t.dueTime), []).append(t)

        warnings: List[str] = []
        for day, tod in sorted(slots):  # sorted for deterministic output
            group = slots[(day, tod)]
            if len(group) > 1:
                titles = ", ".join(f"'{t.title}'" for t in group)
                warnings.append(
                    f"Conflict: {titles} are all scheduled at "
                    f"{day} {tod.strftime('%H:%M')}"
                )
        return warnings


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

    def completeTask(self, task: Task) -> Optional[Task]:
        """Mark a task complete (kept as history) and roll a recurring one forward.

        This is where marking-complete meets recurrence. The completed task
        stays in the plan as a done-log entry; if it recurs, Task computes the
        next instance from its due date and Plan -- the source of truth for
        tasks -- stores it. Returns the newly created next-occurrence Task, or
        None if the task was one-shot or already completed.
        """
        if task.completed:
            return None
        task.markComplete()
        nextTask = task.nextOccurrence()
        if nextTask is not None:
            self.addTask(nextTask)
        return nextTask

    def skipTask(self, task: Task) -> Optional[Task]:
        """Skip a task: drop it from the plan, but still roll the series forward.

        Unlike completeTask, the skipped occurrence leaves no done-log entry --
        it is removed. If it recurs, its next occurrence is created from the
        skipped task's due date and added, so skipping Monday still leaves you
        with Tuesday. Returns the new next-occurrence Task, or None if the task
        did not recur.
        """
        nextTask = task.nextOccurrence()
        self.tasks = [t for t in self.tasks if t is not task]  # drop by identity
        if nextTask is not None:
            self.addTask(nextTask)
        return nextTask

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

    def getTasksForPet(self, petId: str) -> List[Task]:
        """Return tasks for a single pet without scanning every other pet."""
        for pet in self.pets:
            if pet.id == petId:
                return pet.getTaskSheet().getTaskList()
        return []

    def filterTasks(
        self,
        status: Optional[str] = None,
        petName: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks across all pets by completion status and/or pet name.

        status:  "done" or "pending" (mapped to the `completed` flag).
        petName: case-insensitive pet name; only that pet's tasks are kept.
        Passing None for an argument means "don't filter on it". This lives on
        Owner because it is the only object that knows both the tasks and which
        pet each one belongs to.
        """
        matches: List[Task] = []
        for pet in self.pets:
            if petName is not None and pet.name.lower() != petName.lower():
                continue
            for task in pet.getTaskSheet().getTaskList():
                if status is not None:
                    want_done = status.lower() == "done"
                    if task.completed != want_done:
                        continue
                matches.append(task)
        return matches


# ---------------------------------------------------------------------------
# Task-list utilities
#
# Free functions that operate on any list of Tasks. Kept module-level (rather
# than as methods) so they compose: filter, then sort, then expand, in any
# order, over tasks gathered from one pet or the whole household.
# ---------------------------------------------------------------------------

def sortByTime(tasks: List[Task]) -> List[Task]:
    """Order tasks chronologically for an at-a-glance agenda.

    Sort key, in order: due date, then time of day (untimed/all-day tasks
    sort after timed ones on the same day), then priority, then title for a
    stable, deterministic result.
    """
    def key(t: Task):
        untimed = t.dueTime is None
        tod = t.dueTime if t.dueTime is not None else time.max
        rank = Scheduler.PRIORITY_RANK.get(t.priority.lower(), 99)
        return (t.dueDate, untimed, tod, rank, t.title)

    return sorted(tasks, key=key)


def filterTasks(
    tasks: List[Task],
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[Task]:
    """Return tasks matching every provided filter.

    status: "done" or "pending" (mapped to the `completed` flag).
    priority: matched case-insensitively.
    Passing None for a filter means "don't filter on it".
    """
    result = tasks
    if status is not None:
        want_done = status.lower() == "done"
        result = [t for t in result if t.completed == want_done]
    if priority is not None:
        result = [t for t in result if t.priority.lower() == priority.lower()]
    return result


def expandRecurring(tasks: List[Task], start: date, end: date) -> List[Task]:
    """Materialize concrete dated occurrences within [start, end].

    Each recurring template is expanded into one Task per occurrence in the
    window; one-shot tasks pass through if their dueDate is in range. This
    keeps storage O(1) per recurring task -- occurrences exist only when a
    window is requested. Per-occurrence completion (completedDates) is carried
    onto each generated instance.
    """
    expanded: List[Task] = []
    for task in tasks:
        for occ in task.occurrences(start, end):
            expanded.append(
                replace(
                    task,
                    id=f"{task.id}@{occ.isoformat()}",
                    dueDate=occ,
                    completed=task.completed or occ in task.completedDates,
                    recurrence=None,  # a materialized occurrence is one-shot
                )
            )
    return expanded
