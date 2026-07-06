# PawPal+ Project Reflection

## 1. System Design

3 Actions the user should be able to do:

1. Be able to add their pet
2. Have a catered plan about their pet
3. See what tasks need to be done for the pet

**a. Initial design**

- Briefly describe your initial UML design.
  My UML design Has 5 classes, User, which has pet, Pet which has Plan and Contains TaskSheet, Plan which contains Task, and TaskSheet which manages Task

- What classes did you include, and what responsibilities did you assign to each?
  User has an id, name and pet list, has the ability to addPet to themself, as well as list the pets that they have. Pet has an id string, name string, a type string, plan list, and taskSheet. They're able to get a plan and get a taskSheet. The plan also has a n id, string, but also a description, the date it was created and a task list. A taskSheet has the petid as a string, and a task list, and you can add a task from the taskList, return the taskList, and filter by priority. And finally task has an id, title, description, priority, due date, and a completed boolean. You can mark a task complete or update the task info.

**b. Design changes**

- Did your design change during implementation?
  Yes
- If yes, describe at least one change and why you made it.
  One change that happened is that getEventList() was removed. It returned List[Event], but there was no Event class. It also generated a schedule of events, which was supposed to have logic, so that portion was moved to a helper Scheduler class that would handle the logic of that, so now Plan is simply a container of tasks, turining those taks into timed events is the Schedulers job now.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  It consideres things like priority first, lower rank means more urgent. Then the due date is the tie breaker after priority. time of day comes after where its used to order same day tasks and it's the basis for conflict checks. Completion status is next where buildSchedule only schedules pending tasks.
- How did you decide which constraints mattered most?
  It was based on what was most urgent. If something was not done yet and it was urgent, then it needs to be prioritized. After that was due date, because if something was due yesterday and it was urgent, and something is due today and it's not urgent, then the urgent thing will get first in line, even though the non urgent item is due today and the urgent item has passed.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  buildSchedule can overlap tasks if they are set for the same time, regardless of the priotity, which means the user would need to decide which task they would want to complete at that time.
- Why is that tradeoff reasonable for this scenario?
  This is reasonable because then the schedule is set by the user when they make a task to be completed, and it allows for specific management of due dates, especially if 2 tasks need to be done at the same time, then the user can make that happen.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  I used it for brainstorming and refactoring.

- What kinds of prompts or questions were most helpful?
  Something that was very helpful was to ask it what it thought my work needed, why it thinks that, what it would do differently, and if it implemented a feature, I would ask the reasoning behind it, because I found some issues with where it's logic was.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  When it wanted to make the scheduling system as one where tasks would not have any blank gaps between them and would make them more back to back, which the AI said would remove overlapping of tasks, and help the user to get the done faster since this app is not a calendar, but an app to help get things done. I did not accept this because say you have a vet visit, need to give your pet medication at a certain time, or something important like that, and the app rearanged your timing, then it could throw you off and be dangerous.
- How did you evaluate or verify what the AI suggested?
  I verified this by going through the code that it made, and through test runs and read the printed schedule, and noticed that indeed it would squish things together, so that had to go.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  Sorting Correctness:
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
