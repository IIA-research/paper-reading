---
name: "Kevin"
---

Modeling Future Conversation Turns studies how to use the outcome of answering after a clarifying question to train a model to ask more useful clarifying questions. The authors' point is that a follow-up question does not complete the task on the spot, yet it may let the assistant tell user intents apart and then give the right answer. So the method puts each candidate question through an actual "user reply, then assistant answer" exchange, and uses the final outcome to decide whether the question is worth learning.

### Training mechanism

Training first builds clarification demonstrations from NQ-Open and AmbigQA and uses supervised training for a question asker, a direct answerer, a post-clarification answerer and a user simulator. For preference data, 6 candidate questions are generated per item: 1 greedy output and 5 random samples. Each candidate question is answered by several simulated users with different intents, who give different replies, and a fixed answerer then answers. Each item allows at most one clarification. The main method, DPO-Match, scores a question as: number of users answered correctly after clarification / total number of users simulated for that item. For example, a question that leads to the right answer for all three users with different intents scores 1; one that satisfies only one of them scores 1/3. The authors build good/bad question pairs from these scores and use DPO to update the first-turn response policy.

### Experimental setup

DPO-RM has an off-the-shelf reward model score the candidate question directly, looking only at the original question and the candidate. DPO-Likelihood also simulates the user reply, but instead of freely generating an answer, it computes the fixed answerer's conditional probability of the known target answer; the easier the target answer is to predict, the higher the question's score. DPO-Match actually generates the follow-up answer and checks whether it is correct. In the version where the model decides for itself whether to ask, a direct-answer candidate is added and scored the same way, by how many users it satisfies. If asking gives a better outcome, asking is preferred; if the direct answer is better, answering directly is preferred; on a tie, answering directly is explicitly preferred, saving a turn.

The main test set is 1,960 AmbigQA questions: 788 unambiguous and 1,172 ambiguous. Baselines include answering directly, always clarifying, letting the model choose whether to ask, and the three DPO scoring methods above. The sampled version of direct answering generates 20 answers and takes the k most common, where k is the number of gold answers, so it is not a strictly equal-budget comparison. ProCoT and PPDPP only decide whether to ask or answer and then hand off to a shared generator; for PPDPP only the supervised action classifier is reproduced, not the reinforcement learning stage.
