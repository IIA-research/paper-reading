---
name: "Han Bao"
---

Lets an agent learn the user's intent from the user's corrections, forming an "asset", similar to a skill.

The asset is used at two points in each task: before starting work, and in a final check after finishing.

The experiment has two parts, learning and an exam. The first pass is learning, essentially going through the exam questions once to build its own intent "assets"; the second pass is the exam, with no user, and covers both the original questions and transfer questions.

Example asset:

> **Context:** product review script — connect the features to the user's daily life; personal experience must be genuine.
>
> **Intent**
> - *Rationale:* the user writes reviews for a real audience, who care about "what this does for my life", not a spec sheet; the review also speaks in the user's own voice, so made-up experiences hurt credibility.
> - *Requirements:* ① explain how the product's features simplify the user's daily routine; ② don't write any number the user hasn't measured — use a [my time] placeholder.
> - *Facts:* the user is busy in the mornings (source: the user's first correction); the user has never timed this styler (source: the user's second correction).
