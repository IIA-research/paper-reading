---
name: "Han Bao"
---

An AI assistant that serves the same user over a long period should, while the user is online, proactively ask for personal preferences that the current task does not need but future tasks will.

Each user is given a set of hidden preference rules in advance; the evaluator knows them, the agent does not. Every rule corresponds to a future test task, and whether that task is done right depends on knowing the rule. All agents use the same memory mechanism.

There are two phases, learning and testing, with different data but the same users.
