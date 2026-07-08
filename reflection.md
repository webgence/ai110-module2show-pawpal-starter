# PawPal+ Project Reflection

## 1. System Design

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Owner, Pet, Task, Scheduler

There should be a class for the owner where there is attributes on the number of pets, time, priorities, and owner preferences.

There should be a method in the owner class for addPets() where this function add pet to owner.

There should be a method in the owner class for new_time() where this fucntion will calcuate the new time the new pet will cost the owner.

There should be a method in the owner class for time_for_pets() where this function will calcuate the time needed for each pet.

There should be a method in the owner class for time_for preference where this function will calcuate the time needed for the owner.

There should be a method in the owner class for ranking_prioities() where the function will rank the responsiblities of the owner.




There should be a class for the pet where there is attributes on walks, feeding, meds, enrichments, grooming.

There should be a method in the pet class for rank_activity() where this fucntion will rank the given activities by pet preference.

There should be a method in the pet class for cost_of_time() where this function will calcuate the time it will take to perform a specfic activity.




There should be a class for task where the attribute is cost of task, number of tasks.

There should be a method in the task class for new_task where this function will add a new task.

There should be a emthod in the task class for edit_task where this function edits the task time.


There should be a class for Scheduler where the attributes is contraints(what stuff should owner still need to do) and priories(what stuff the owner get done for pet), 


There should be a method for priories_over_contraints where this method returns a new order list of items of priories and items of contraints in order of importance that needs to get done.

There should be a method for sheduler where it returns a schdule of when to perform priories and when to perform owner tasks.





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
