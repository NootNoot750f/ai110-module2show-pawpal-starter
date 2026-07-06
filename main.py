from datetime import date
from pawpal_system import Owner, Pet, Plan, Task

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
#Task1
taskOneForCatOne = Task(
    id="task-1",
    title="Feed Bindi",
    description="Feed Bindi her favorite cat food.",
    priority="high",
    dueDate=date(2026, 7, 5),
)
#Task2
taskTwoForCatOne = Task(
    id="task-2",
    title="Play with Bindi",
    description="Spend 15 minutes playing with Bindi using her favorite toy.",
    priority="medium",
    dueDate=date(2026, 7, 6),
)
#Task 3
taskThreeForCatOne = Task(
    id="task-3",
    title="Groom Bindi",
    description="Groom Bindi to keep her coat healthy and shiny.",
    priority="low",
    dueDate=date(2026, 7, 7),
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
    dueDate=date(2026, 7, 6),
)
taskTwoForCatTwo = Task(
    id="task-2",
    title="Play with Sushi",
    description="Spend 15 minutes playing with Sushi using her favorite toy.",
    priority="medium",
    dueDate=date(2026, 7, 7),
)
taskThreeForCatTwo = Task(
    id="task-3",
    title="Groom Sushi",
    description="Groom Sushi to keep her coat healthy and shiny.",
    priority="low",
    dueDate=date(2026, 7, 8),
)

#Cat1
planForCatOne.addTask(taskOneForCatOne)
planForCatOne.addTask(taskTwoForCatOne)
planForCatOne.addTask(taskThreeForCatOne)
catOne.addPlan(planForCatOne)
ownerOne.addPet(catOne)


planForCatTwo.addTask(taskOneForCatTwo)
planForCatTwo.addTask(taskTwoForCatTwo)
planForCatTwo.addTask(taskThreeForCatTwo)
catTwo.addPlan(planForCatTwo)
ownerOne.addPet(catTwo)



print(f"All tasks for {ownerOne.name}:")
for task in ownerOne.getAllTasks():
    status = "done" if task.completed else "pending"
    print(f"  [{task.priority}] {task.title} (due {task.dueDate}) - {status}")

for pet in ownerOne.getPets():
    sheet = pet.getTaskSheet()
    print(f"\nTask sheet for {pet.name}:")
    for task in sheet.getTaskList():
        print(f"  - {task.title}: {task.description}")