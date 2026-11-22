---
name: "Han Bao"
---

While an agent runs a long task, the missing information is forcibly given to it at different points in time, to see how the task success rate changes.

First the agent runs the task 3 times with complete information to get the average number of steps it needs; the information is then inserted at 10%, 30%, 50%, 70% and 90% of that step count.

Missing information falls into four types: **goal** (unclear what the final deliverable is), **input** (unclear where the data is), **constraint** (a rule or threshold is missing), and **context** (domain knowledge is missing).

Conclusion: if what is missing is the *goal*, it must be clarified right at the start; if it is the *input data*, asking any time before the halfway point is still fine.

Second experiment: models decide for themselves when to ask, and their actual timing is compared with the best timing found by the forced-insertion experiment. None of the current models ask at the best time.
