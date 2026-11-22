# Classification rubric (from the IIA survey outline)

Every paper gets one **primary category** (where its main contribution sits) and up to three **subtopics** (survey subsections it speaks to). The old 7-step sections are kept in `papers.yaml` as `legacy_section` but no longer shown.

## Primary categories

| key | survey chapter | put a paper here when its main contribution is ... |
|---|---|---|
| Foundations | 2 Interactive Intent Alignment | a conceptual framework, definition, history, or position on intent alignment / mixed initiative as a whole (classic HCI theory, broad position papers) |
| When | 4 When: Timing the Intervention | deciding *whether and when* the agent should intervene: detect that something is off, choose between acting / asking / confirming / abstaining / escalating / interrupting, or learn such a policy |
| What | 5 What: Locating the Gap | finding *which part* of the user's intent is missing or wrong: ambiguity in what was said, unstated preferences or needs, intent that changes over time, shared understanding / grounding between user and agent |
| How | 6 How: Resolving Misalignment | the *mechanism* used to close the gap: interacting with the user, retrieving from the environment or tools, inferring from context, memory and history, or combining several kinds of evidence |
| Evaluation | 7 Evaluation and Simulation | a benchmark, an evaluation protocol or metric, a user simulator, or a study of how valid simulators are |
| Practice | 8 Intent Alignment in Practice | a deployed or applied system, or an application study, where the setting (a general-purpose product agent, or a specific domain such as medicine, law, education, robotics, data analysis) is the point |

Tie-breakers:
- A benchmark, metric or simulator paper is **Evaluation** even if its topic is when or what to ask; record the topic in subtopics.
- A method that decides when to ask is **When**; a method about which question to ask or which unknown to resolve is **What**; a method whose novelty is the channel (asking vs retrieving vs inferring from history) is **How**.
- Domain papers go to **Practice** only when the domain application is the contribution; a general method merely tested in a domain keeps its method category.
- User studies of how people experience intervention or grounding go with the topic they study (usually When or What).

## Subtopics (survey subsections)

- 4.1 Detecting misalignment · 4.2 Choosing an intervention · 4.3 Learning intervention policies
- 5.1 Clarifying expressed intent · 5.2 Uncovering implicit intent · 5.3 Tracking evolving intent · 5.4 Building mutual understanding
- 6.1 Interacting with the user · 6.2 Retrieving from the environment · 6.3 Inferring from context and history · 6.4 Integrating evidence
- 7.1 Benchmarks · 7.2 Protocols and metrics · 7.3 User simulation · 7.4 Simulator validity
- 8.1 General-purpose agents · 8.2 Domain-specific applications
- 2.1 Historical roots and evolution · 2.2 Definition · 2.3 Boundaries with related problems

Classification is done by an LLM from each paper's title, topic and summary. It is a draft until a person checks it; papers that have been read in full get their category checked by hand.
