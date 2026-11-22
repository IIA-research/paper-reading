---
name: "Han Bao"
---

The paper asks whether a signal meaning "this question doesn't have enough information to be answered yet" can be read from an LLM's internal states, and used to decide when to stop and ask the user. The authors find that such a signal does exist and transfers well between similar problems, e.g. from one set of math problems with missing numbers to another; but whether questions that *nobody* can answer correspond to a separate signal cannot be determined once wording and similar factors are controlled for.

Probes trained on single-turn data fail completely when moved to multi-turn dialogue; probes trained specifically on multi-turn data can detect it, but are no better than a simple classifier that only looks at which words the user said.

Finally, when the probe is actually used as a gate, its accuracy at deciding when to ask is far above chance and close to deciding with the ground truth, but the final task success rate still can't beat a simple prompting method: restate the conditions the user has given before answering. The authors conclude that the bottleneck is mainly not detecting missing information, but how the model uses the information once it gets the clarification. The paper is mostly negative results, but its experimental controls and pre-registered analysis plan are very rigorous.
