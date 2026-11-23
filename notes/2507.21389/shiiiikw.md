---
name: "Kevin"
---

This paper asks whether, when the user has not fully stated the writing requirements, an assistant can proactively ask for the key information and then write the document well. The authors argue that some models do ask follow-up questions, but often only about length, format and the like. The domain knowledge and specific requirements that actually shape the content still go unasked. The paper therefore sets out to train models to ask more targeted questions.

### Hide part of the requirements and let the assistant ask

The benchmark is adapted from the expert writing tasks in DOLOMITES. Each task originally has four parts: what the task is, suggested steps for completing it, the input material available, and the requirements the final document must meet. The authors give the assistant only the task goal and the input material, and leave the steps and output requirements to a simulated user. The assistant asks, the simulated user answers, and the Q&A history is kept for later turns. Each task allows at most 5 rounds of Q&A and can end early. After the questions, the collected information goes to a fixed writing model, so the main comparison is who is better at eliciting useful information.

### Training

Each question is scored as it is asked, and these scores are used to train the question asker. With only one overall score after the whole document is written, it would be hard to tell which earlier question helped. So the authors score each question separately. First, the hidden steps and output requirements are split into individual sentences, each numbered. After the assistant asks a question, the simulated user has to say: "Which hidden sentences are needed to answer this question?" A program checks the returned numbers: if at least one hidden sentence is used, the question scores 1; if none is used, it scores 0.

With these scores, the authors train with the existing actor–critic PPO algorithm. The question asker asks the questions; a separate critic estimates, from the current conversation, how much reward is still to come. During training, the program combines the actual reward with this estimate to judge which questions did better than expected, then adjusts the question asker so such questions become more likely. The critic is also updated so its estimate gets closer to the reward actually received.

### Experiments

At test time, each policy asks questions within the 5-round limit, and the same writing model then writes the document. For scoring, the originally hidden output requirements are turned into a checklist, and a fixed LLM checks them one by one. Each satisfied item scores 1 and each unsatisfied item 0; the final score is the number satisfied divided by the total number of requirements.

There are four baselines. Direct does not ask at all and writes from the available information. Vanilla QA instructs the model in the prompt to ask proactively, has it talk with the simulated user first, and then passes the collected information to the writing model. Synthetic-dialogue SFT first shows a teacher model the full task and asks it to write demonstration dialogues: assuming the assistant initially knows only the goal and the input material, how should it ask its way to the hidden requirements step by step? The question asker is then trained on these dialogues to imitate the demonstrated questioning. QMSum indirect supervision extracts the turns where people ask questions from real meeting transcripts and trains with DPO. DPO usually pairs one good and one bad response for the same input, making the model favor the good response.
