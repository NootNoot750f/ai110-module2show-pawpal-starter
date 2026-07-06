from datetime import date, time
from pawpal_system import (
    Owner,
    Pet,
    Plan,
    Scheduler,
    Task,
    expandRecurring,
)

#Create Owner 1
ownerOne = Owner(id="owner-1", name="Nick")

#cat 1
catOne = Pet(id="pet-1", name="Bindi", type="cat")
#Plan
planForCatOne = Plan(
    id="plan-1",
    name="Daily Care Plan",
    description="A plan for daily care tasks for Bindi",
    createdAt=date.today(),
)
#Task1 - a daily recurring feeding at 8:00am
taskOneForCatOne = Task(
    id="task-1",
    title="Feed Bindi",
    description="Feed Bindi her favorite cat food.",
    priority="high",
    dueDate=date(2026, 7, 5),
    dueTime=time(8, 0),
    durationMinutes=20,
    recurrence="daily",
)
#Task2 - overlaps the 8:00 feeding on purpose (8:10-8:40) to show conflict detection
taskTwoForCatOne = Task(
    id="task-2",
    title="Play with Bindi",
    description="Spend 15 minutes playing with Bindi using her favorite toy.",
    priority="medium",
    dueDate=date(2026, 7, 5),
    dueTime=time(8, 10),
    durationMinutes=30,
)
#Task 3
taskThreeForCatOne = Task(
    id="task-3",
    title="Groom Bindi",
    description="Groom Bindi to keep her coat healthy and shiny.",
    priority="low",
    dueDate=date(2026, 7, 7),
    dueTime=time(18, 0),
)
#Task 4 - SAME-pet clash: booked at the same time as Feed Bindi (07-05 08:00).
taskFourForCatOne = Task(
    id="task-4",
    title="Medicine for Bindi",
    description="Give Bindi her morning medicine.",
    priority="high",
    dueDate=date(2026, 7, 5),
    dueTime=time(8, 0),
    durationMinutes=10,
)
#Task 5 - CROSS-pet clash: same time as 'Play with Sushi' (07-07 17:00).
taskFiveForCatOne = Task(
    id="task-5",
    title="Evening walk for Bindi",
    description="Take Bindi out for an evening stroll.",
    priority="medium",
    dueDate=date(2026, 7, 7),
    dueTime=time(17, 0),
)
#Task 6 - FLOATING: no dueTime, so the scheduler packs it into a free gap.
taskSixForCatOne = Task(
    id="task-6",
    title="Clean litter box",
    description="Scoop and refresh Bindi's litter box.",
    priority="medium",
    dueDate=date(2026, 7, 5),
    dueTime=None,
    durationMinutes=15,
)



catTwo = Pet(id="pet-2", name="Sushi", type="cat")

planForCatTwo = Plan(
    id="plan-2",
    name="Daily Care Plan",
    description="A plan for daily care tasks for Sushi",
    createdAt=date.today(),
)

taskOneForCatTwo = Task(
    id="task-1",
    title="Feed Sushi",
    description="Feed Sushi her favorite cat food.",
    priority="high",
    dueDate=date(2026, 7, 5),
    dueTime=time(9, 0),
    durationMinutes=20,
    recurrence="daily",
)
taskTwoForCatTwo = Task(
    id="task-2",
    title="Play with Sushi",
    description="Spend 15 minutes playing with Sushi using her favorite toy.",
    priority="medium",
    dueDate=date(2026, 7, 7),
    dueTime=time(17, 0),
)
taskThreeForCatTwo = Task(
    id="task-3",
    title="Groom Sushi",
    description="Groom Sushi to keep her coat healthy and shiny.",
    priority="low",
    dueDate=date(2026, 7, 12),
    dueTime=time(11, 0),
    recurrence="weekly",
)

# Cat1 -- tasks added intentionally OUT OF chronological order so the
# sorting method has real work to do (07-07 18:00, then 07-05 08:00, 08:10).
planForCatOne.addTask(taskThreeForCatOne)
planForCatOne.addTask(taskOneForCatOne)
planForCatOne.addTask(taskTwoForCatOne)
planForCatOne.addTask(taskFourForCatOne)
planForCatOne.addTask(taskFiveForCatOne)
planForCatOne.addTask(taskSixForCatOne)
catOne.addPlan(planForCatOne)
ownerOne.addPet(catOne)


# Cat2 -- also out of order (07-12, then 07-05, then 07-07).
planForCatTwo.addTask(taskThreeForCatTwo)
planForCatTwo.addTask(taskOneForCatTwo)
planForCatTwo.addTask(taskTwoForCatTwo)
catTwo.addPlan(planForCatTwo)
ownerOne.addPet(catTwo)



def fmt(task):
    """One-line label: time (or 'all day'), priority, title, status."""
    when = task.dueTime.strftime("%H:%M") if task.dueTime else "all day"
    status = "done" if task.completed else "pending"
    return f"{task.dueDate} {when:>6}  [{task.priority:^6}] {task.title} - {status}"


# Mark one task done so the status filter has something to exclude.
taskThreeForCatOne.markComplete()  # "Groom Bindi" -> done

scheduler = Scheduler()
allTasks = ownerOne.getAllTasks()

# Show the raw insertion order first so the sort's effect is obvious.
print(f"Tasks for {ownerOne.name} in the order they were ADDED (not sorted):")
for task in allTasks:
    print(f"  {fmt(task)}")

# --- Feature 1: sort by time (Scheduler.sortByTime) --------------------------
print("\nSame tasks sorted by time via Scheduler.sortByTime():")
for task in scheduler.sortByTime(allTasks):
    print(f"  {fmt(task)}")

# --- Feature 2: filter by completion status or pet name (Owner.filterTasks) --
print("\nPending tasks only  ->  ownerOne.filterTasks(status='pending'):")
for task in scheduler.sortByTime(ownerOne.filterTasks(status="pending")):
    print(f"  {fmt(task)}")

print(f"\nTasks for {catTwo.name} only  ->  ownerOne.filterTasks(petName='{catTwo.name}'):")
for task in scheduler.sortByTime(ownerOne.filterTasks(petName=catTwo.name)):
    print(f"  {fmt(task)}")

# --- Feature 3: recurring tasks ----------------------------------------------
weekStart, weekEnd = date(2026, 7, 5), date(2026, 7, 11)
print(f"\nMaterialized occurrences for the week of {weekStart}:")
for task in scheduler.sortByTime(expandRecurring(allTasks, weekStart, weekEnd)):
    print(f"  {fmt(task)}")

# --- Feature 4: conflict detection -------------------------------------------
# Lightweight, message-based check for tasks booked at the exact same time.
# Returns warning strings (never raises), so we just print them and move on.
print("\nSame-time conflict warnings:")
warnings = scheduler.conflictWarnings(allTasks)
if not warnings:
    print("  none")
for message in warnings:
    print(f"  [!] {message}")

# Richer overlap check (tasks whose time windows overlap, not just exact ties).
print("\nOverlapping-window conflicts:")
conflicts = scheduler.detectConflicts(allTasks)
if not conflicts:
    print("  none")
for earlier, later in conflicts:
    print(f"  [!] '{earlier.title}' ({earlier.dueTime.strftime('%H:%M')}) "
          f"overlaps '{later.title}' ({later.dueTime.strftime('%H:%M')})")

# --- Feature 5: build a schedule that honors fixed times --------------------
# Fixed tasks (with a dueTime) land at their exact time; the floating
# 'Clean litter box' (no dueTime) is packed into the first free gap on 07-05.
print("\nGenerated schedule (fixed times honored, floating task packed in):")
for event in scheduler.buildSchedule(allTasks):
    when = event.scheduledTime.strftime("%Y-%m-%d %H:%M")
    kind = "fixed " if event.task.dueTime is not None else "float "
    print(f"  {when}  ({kind}{event.durationMinutes:>2}m)  {event.task.title}")

# --- Feature 6: recurring tasks roll forward on complete OR skip ------------
# 'Feed Bindi' is daily, due 2026-07-05. The cadence is fixed off each due
# date: completing keeps the day as a done-log entry and spawns the next day;
# skipping the next day drops it (no log) but still rolls the series forward.
print("\nRolling the daily 'Feed Bindi' forward (cadence fixed off each due date):")
day2 = planForCatOne.completeTask(taskOneForCatOne)  # 07-05 done -> spawns 07-06
assert day2 is not None  # daily task always spawns a next occurrence
print(f"  completed 07-05: {fmt(taskOneForCatOne)}")
print(f"  -> spawned:      {fmt(day2)}")
day3 = planForCatOne.skipTask(day2)                  # skip 07-06   -> spawns 07-07
print("  skipped   07-06: (removed, no log entry)")
print(f"  -> spawned:      {fmt(day3)}")

for pet in ownerOne.getPets():
    sheet = pet.getTaskSheet()
    print(f"\nTask sheet for {pet.name}:")
    for task in sheet.getTaskList():
        print(f"  - {task.title}: {task.description}")