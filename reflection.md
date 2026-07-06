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
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
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
