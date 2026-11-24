---
name: "Jason"
---

Answering questions about an image, but the answer depends on one fact that cannot be seen in the image. The paper's example: in the image, a 20-year-old holds a drink, and the question is "Is it legal for him to drink this?" The answer depends on which country this is (legal at 18 or at 21), and the image does not say. A normal model just guesses an answer. What they want: the model notices that the question is missing one thing, first asks "Which country is this in?", gets the reply, and then answers. **The system has three roles, all played by the same small model (for example Qwen2.5-VL-7B).** Controller: looks at the image and the question, and says "ask" or "answer". Asker: when the controller says "ask", it writes that one clarifying question. Answerer: takes the image, the question, and the question and reply (if it asked), and gives the final answer. Only the first two are trained; the answerer is the original model and is not changed.

**They made the data themselves.** From the existing CODIS, they picked 266 questions of this "missing one fact outside the image" kind. The missing fact in each question belongs to one of five types (place and direction, time, cultural background, attribute, relationship between people). Each question comes with a reference clarifying question, written by GPT-4o and checked by people (example: "What is the legal drinking age where this photo was taken?"). Then they made control questions: write the missing fact straight into the question (for example, put "This is in Germany" into the question), and then there is no need to ask; or write in an unrelated sentence (for example, "This was taken on a Tuesday"), and then it still needs to ask. 532 questions in total, half need asking and half do not, split 70 / 15 / 15 into train, validation and test.

**How the controller is trained: it is just classification.** Input is the image + the question; output is "ask / answer"; the label is which half the question was put in when the data was made. There is no interaction at all. What it learns is "whether the question states that key piece of information".

**How the asker is trained: this is the RL part of the paper, called GRPO-CR.** Only the 186 training questions that need asking are used. For each question, the asker writes 2 candidate questions, and each candidate gets a total score from a five-item scoring table (a series of reward shaping):

1) Format: ends with a question mark and is within 50 words, +0.5; otherwise −0.5.

2) Whether it targets the missing type of information: the sentence uses a "what / which" kind of question and has keywords for this type of missing information (for culture, words like country, city), +0.3; only one of the two, +0.1; neither, −0.1.

3) Whether the reply can change the answer: a model pretends to be the user and answers this candidate question, then the model answers the original question again with this reply, and we see whether the answer changed. Changed, +0.5; not changed, −0.3.

4) Not a restatement: too much word overlap with the original question (like saying the original question in other words) loses points; low overlap gains points.

5) Like the reference: GPT-4o gives a 0 to 1 similarity score between the candidate and the human-checked reference question.

The two candidates' scores are subtracted; the words of the higher-scoring one are made stronger, and the lower one is made weaker. It is standard GRPO, group size 2, one round, practicing only one question. Note that none of the five items is "whether the final answer is right". What the asker learns: write a question with the right format, the right keywords, not a restatement, like the reference, and whose reply can change the answer.

**How testing runs.** A question comes in, and the controller looks at the image and the question. If it says "answer", the answerer answers directly. If it says "ask", the asker writes one question, and then GPT-4o plays the user and replies. Note here: GPT-4o only sees the image and does not know the real missing fact; it gives a "reasonable" reply (the paper says this is so it does not rely on the gold answer). The answerer takes the image, the original question, and this question and reply, and gives the final answer; then GPT-4o judges right or wrong using the gold answer. Multi-round mode: after one round, the controller looks again (this time with the question and reply added); if it says "ask", there is another round, until it says "answer" or the limit is reached (the paper does not say what the limit is). During training, the controller never saw an input where one round of asking had already happened.

**What the numbers say (Qwen2.5-VL-7B, their own test set, accuracy).** No asking 0.266; no controller, always ask 0.357; controller + asker 0.409; with a perfect controller 0.452; GPT-4o answering directly without asking 0.619. So: most of the gain comes from "asking" (+9 points), the controller adds 5 points over always asking, a perfect controller adds 4 more points, and more rounds add almost nothing and sometimes go down. On the outside datasets ClearVQA and VizWiz, the trend is the same.

**Seen from your angle.** when: not learned; it comes from the labels of the self-made data, and in fact it matches the very start of the query. The controller judges "whether the question looks like it is missing information", which has nothing to do with whether asking helps afterwards. what: the asker writes it itself; the score is five rules set by people plus one GPT-4o similarity score, with no right or wrong. One more point matters more than when and what: the "user" here is GPT-4o guessing from the image, and it does not have the missing fact. So "asking helps" really means "the hard step is pushed to GPT-4o to guess".

- Data: self-made (based on CODIS; image questions missing one fact outside the image); also tested on ClearVQA (image questions that are unclear in themselves) and VizWiz (questions from blind people about photos they took).
- Baselines: no methods from this field; only heuristics (never ask, always ask), 4-shot prompting, a perfect controller (upper bound), and GPT-4o answering directly.
