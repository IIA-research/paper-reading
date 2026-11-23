---
name: "Han Bao"
---

### Background: SDPO

- **The problem with RLVR**: reasoning models have mainly been trained with RLVR, e.g. GRPO. But these methods carry too little information: the reward is binary, so the model does not know exactly where it went wrong or right, and when every attempt is wrong it cannot learn at all.
- **Text feedback**: many environments give text feedback, such as code error messages or a reviewer model's comments, and this feedback says what went wrong. SDPO calls this RLRF (Reinforcement Learning with Rich Feedback).
- **Method**: the same model, with the feedback added to its context, acts as a teacher that scores the student token by token. The principle is to put the same answer in two contexts, compute the probability of each token in each, and pull the student's response toward the teacher's.

### This paper

It does not create a new method. Instead it proposes a new idea: use the user's next message as the feedback in SDPO.

Both experiments use the same data format, with three parts:

- x: the user request
- y: the response
- o: the user's reply

### Experiment 1 (offline)

Train on WildChat to see whether the model gets better without hurting its other abilities.

- Alignment and instruction following: both improve
- Knowledge questions: about the same

### Experiment 2 (online): personalization

x is a prompt taken from TL;DR or HelpSteer2. The question is whether the model, only by chatting with this user, can gradually learn their preferences from their replies. There are three setups:

1. **Learning one preference**: after 50 interactions the win rate exceeds 85%; after 200 it exceeds 95%.
2. **Preference reversed midway**: for the first 250 interactions the user likes "short and casual", then suddenly likes "detailed and formal". The model quickly reverses the learned behavior and shifts to the new preference.
3. **Stacking three preferences one after another**: 1,500 interactions in total, with a new preference added every 500; the three preferences do not conflict. When learning a new preference, the old ones are kept, with no catastrophic forgetting, and learning is fairly fast, but each preference levels off lower than the one before.
