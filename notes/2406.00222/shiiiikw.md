---
name: "Kevin"
---

Learning to Clarify studies how to teach a model to ask or answer using a small number of task conversations. It proposes ACT, which starts from existing correct conversations, keeps adding good and bad responses produced by the current model itself, and then does preference training. The authors first split the original conversations into samples at each assistant turn, with the original correct response as the good response. Another fixed model takes the opposite action to produce the bad response: for example, where the assistant should have confirmed the year, it guesses the year and answers; where it could already answer, it produces an unnecessary follow-up question. The training data therefore explicitly contains both errors: "should have asked but didn't" and "shouldn't have asked but did".

### Training method

Training here means repeatedly updating the good and bad responses. During training, the model generates one extra response for each input, and a classifier first checks whether it is asking or answering. If the action is wrong, this extra response replaces the old bad response and forms a new pair with the original good response. If the action is right, the model keeps talking with a simulated user until it gives an answer. A successful trajectory replaces the good response and is paired with the existing bad response; a failed trajectory replaces the bad response and is paired with the existing good response. ACT thus always keeps part of the existing supervision while continually training the model to correct the mistakes it currently makes.

These results are used to build preference pairs, and the whole response model is then updated with existing DPO.

### Experimental setup

The benchmarks are PACIFIC (financial QA), Abg-CoQA (reading comprehension) and AmbigSQL, adapted from Spider. For Abg-CoQA the existing clarification turns are removed so the model has to ask on its own, and it is run separately for each true intent. AmbigSQL removes the queried object, needed information or sorting condition; half of the requests are clear and half ambiguous, and scoring uses the SQL execution result.

Baselines include SFT, plain few-shot prompting, CoT prompting that first judges ambiguity, MIPrompt that explicitly prompts for proactive interaction, offline preference training DPO-Dist, and iterative preference training IRPO. DPO-Dist simply takes a stronger model's response as the winner and does not verify the final task result; IRPO builds preference pairs by answer correctness but needs extra test-time compute. ACT improves clarification behavior and some task results overall, but gains in action choice do not always turn into proportional gains in final accuracy.
