---
name: "Kevin"
---

Clarify When Necessary asks which requests an LLM should clarify when it has a limited question budget. The cases of interest are those the model would answer incorrectly on its own but correctly after clarification. The training-free Intent-Sim method generates a clarifying question and simulates ten possible user replies. Another model groups replies with the same meaning. Intent-Sim computes entropy from the groups' relative frequencies and prioritizes requests with several plausible interpretations.

The benchmark covers AmbigQA question answering, AmbiEnt natural language inference, and English-to-French translation on DiscourseMT. Existing annotations specify the user's intent. For translation, removing the preceding context creates ambiguity. For the evaluation itself, GPT-3.5 generates clarification questions and replies in advance using the annotated intent. The model receives the corresponding reply before completing a request it has chosen to clarify.

The authors evaluate GPT-3 and Llama-2-Chat 7B/13B. Under the same question budget, they compare random selection, answer likelihood, Self-Ask (asking the model whether clarification is needed), and Sample Entropy (grouping multiple direct answers and computing their entropy). They also test clarifying no requests, clarifying all requests, and supplying disambiguated inputs directly. In most settings, Intent-Sim is better at picking requests whose answers improve after clarification.
