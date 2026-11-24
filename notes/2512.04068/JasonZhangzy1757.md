---
name: "Jason"
---

This is not an agentic task (AmbigQA). Goal: when a QA question is itself ambiguous, which way pays off (answer directly, give several answers, ask first then answer, ask first then give several answers) depends on two prices: how many points one question costs, and how many points each extra answer costs. These two numbers differ by situation. The authors write the two numbers straight into the prompt, so one model makes different choices according to the numbers, and chooses more accurately than a model that relies on prompting alone.

Over the whole process, the only chance to ask is once, at the start of the conversation (when). So the key of this paper is how to simulate a reward for useful asking to train with.

The environment holds, for each question, a list of interpretations and the gold answer for each interpretation. At the start of each conversation, it draws one interpretation as "what the user really means", and draws a pair of prices α, β (random, to simulate user preferences). The simulated user (an untrained Gemma 2 9B) holds the question and the drawn interpretation. The agent (another Gemma 2 9B, with SFT) gets a prompt with the task description, the reward formula, this conversation's α and β, and a few examples. A question comes in, and the assistant picks one of three: write a clarifying question (CLARIFY), give a short answer (ANSWER), or give one answer for each of several interpretations (MULTI_ANS). If it asks, the simulated user answers according to the secret interpretation, but is told not to repeat the original text.

The reward is the word-level F1 between the final answer and the gold answer (0 to 100) − α × the number of questions asked (0 or 1) − β × the number of words in the assistant's final answer. Asking pays off only if one question raises accuracy by more than α; several answers pay off only if the extra words times β are less than the accuracy gain they bring.

At its core this paper is doing reward shaping, finding a way to simulate the loss that asking brings. The authors report that after this training, the success rate of the task itself can also go up. This is actually very doubtful. Because of reward hacking, the paper does not learn what to ask; most of the time, what SFT can learn is probably which strategy to pick under these a and b. Not to mention that a and b on the test set are also chosen at random; if a and b are large, the model is basically a plain model.

- Data: AmbigQA (open-domain questions that are ambiguous), PACIFIC (multi-turn QA over financial documents and tables; the assistant can see the documents, the user cannot).
- Baselines: no methods from this field; they compare the same model with prompting only, with a limited set of actions, fine-tuned only to answer directly, and the best choice in hindsight (upper bound).
