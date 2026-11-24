---
name: "Jason"
---

**when: In the training stage, by a predetermined method. Here it works on trajectories that the original model runs by itself. From them it takes several middle points (the paper does not say how). At each decision point, each of the four preset action types is forced once, run to the end, and scored by final success. This is used to learn a controller. In the prediction stage, the controller scores every turn and decides which type of action to take; the model itself does the actual action. If the controller proposes the same type three times in a row, control goes back to the original model, and the controller never steps in again. what: not handled. One of the four preset action types is asking the user. The controller only decides "ask in this turn"; the original model writes the question itself. So the final results are very poor.**

In detail, in the training stage: A task comes in. The original model (untrained Qwen3-8B or 14B) talks with a simulated user and calls tools in ToolSandbox, and plays one full game by itself. In this game, each time before the original model takes an action, the environment state is saved. Each save is one decision point (the paper only says "take decision points from the trajectory" and does not say how; judging from the numbers and wording, a save is probably made every turn). There are 1,036 decision points in total.

At each decision point, every action type that is allowed at that moment is forced once: ask the user (no tools in this turn; it can only write one sentence to the simulated user), read-only query (only tools that do not change the state are open), reversible action, and irreversible action (only that kind of state-changing tool is open, and it must call one). After this forced turn, the limits are removed, and the original model finishes the rest of the game by itself. Each type runs only once, at temperature 0, to the end.

Each run goes to the end, and three numbers are recorded: success (by ToolSandbox's evaluator), interaction cost (from a fixed cost table; the table is not given), and critical error (an irreversible action done without permission, 0 or 1). Label = success − cost − critical error, all with weight 1. This number does only one thing: it is the training target of the controller. The original model is not updated.

The controller is a frozen Qwen3-1.7B plus a small set of trainable LoRA parameters and a linear output head. It reads the last 12 turns of the conversation, the environment ID, which types are allowed, and a marker for "which type is being scored now", and outputs a predicted score. The controller's training goal is to make the predicted score of each action type close to the real label from its run.

- Data: ToolSandbox (Apple 2024; phone-style tools that keep state; an LLM plays the user and answers based on "user goal + knowledge boundary + example dialogue")
- Baselines of the same kind: the clarification rule of SAGE-Agent and the cost-sensitive rule of Calibrate-Then-Act (only the rules were copied, not the original systems; both rules step in at every decision point, and 92% of the time they ask)
- Heuristic baselines: no intervention (the original model runs by itself), the best fixed action in hindsight, and fixed schedules that step in about as often.
