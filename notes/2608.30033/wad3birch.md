---
name: "Han Bao"
---

"Act Like a 5th Grader" means having the model role-play a primary-school student. The paper's claim is that prompting a model to play a role is not enough on its own: you have to limit the information the model can see.

The experiment works like this. The real data come from 2,359 Norwegian students in grades 4–6, who answered 750 objective questions on 156 reading-comprehension texts, giving about 72,000 answers. Their mean accuracy is 0.687, and their scores are widely spread.

On the simulation side, an LLM plays a 5th-grade student. Even when the prompt says "the student may not always answer correctly", the LLM's accuracy is still 0.96–0.985.

To make the LLM behave more like a primary-school student, the authors propose CBUS, which has two steps:

1. While the LLM reads the text, it may write down at most C key points. There are two ways of reading:
   - SPR (single-pass reading): read the text once without seeing the questions, and keep the four most important points.
   - TS (targeted scanning): read with the question in mind, and pick out two relevant points.
2. When answering, the original text is removed, and the model answers using only these key points.
