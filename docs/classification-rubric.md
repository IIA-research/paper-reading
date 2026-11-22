# Classification rubric: When / What / How

Papers are tagged with the three core questions of the IIA survey (chapters 4–6). The field is `dims` in `papers.yaml`.

- A paper can have **one or two** tags when each is a main part of its contribution. Tag what the paper is *about*, not every topic it mentions.
- A paper can have **no tag** (`dims: []`) when none of the three is central: general user simulators, agent benchmarks that are not about intent gaps, broad theory or position papers, domain systems where intent is not the point.
- Benchmarks, analyses and user studies are tagged by what they study. Whether a paper is a benchmark is shown separately by the Benchmark tag.

## The three tags

| tag | survey chapter | the paper is mainly about ... |
|---|---|---|
| **When** | 4 When: Timing the Intervention | *whether and when* the agent should step in: detecting that something is off (ambiguity, underspecification, infeasibility, uncertainty), choosing between acting, asking, confirming, abstaining, stopping or escalating, the timing of questions or proactive help, or learning such a policy (e.g. a reward for asking at the right time) |
| **What** | 5 What: Locating the Gap | *which part* of the user's intent is missing or wrong: which question to ask or which unknown matters most, ambiguity in what the user said, unstated preferences or needs, intent that changes over a conversation or across sessions, and shared understanding / grounding / repair between user and agent |
| **How** | 6 How: Resolving Misalignment | the *mechanism or channel* used to close the gap: how to interact with the user (question formats, options, interfaces), retrieving from the environment, documents or tools instead of asking, inferring intent from context, memory, history or feedback, or combining several kinds of evidence |

## Telling them apart

- Deciding *to* ask (or not) is **When**. Deciding *what* to ask about is **What**. Choosing *where the answer comes from* (ask vs look it up vs infer from history) is **How**.
- Learning a user's preferences from past feedback is usually **What + How**: the gap is an implicit preference (What) and the mechanism is inference from history (How).
- A benchmark of whether agents ask at the right moment is **When**; one that scores which questions they ask is **What**; one that scores both gets both.

## Status

Labels were drafted by an LLM from each paper's title, topic and summary on 2026-11-22, following this rubric. They have not been checked by a person yet; papers read in full get their tags checked by hand. The old seven sections stay in `papers.yaml` as `section` but are not shown.
