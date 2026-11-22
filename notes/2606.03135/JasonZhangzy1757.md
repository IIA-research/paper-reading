---
name: "Jason"
---

**Customer service tasks.** The agent talks with the user and uses tools at the same time (τ-bench: in the retail domain, it handles exchanges and returns for orders; in the airline domain, it handles plane tickets). The user has a hidden goal, but does not say all of it at once. The prompt for the simulated user tells it to "reveal it bit by bit." The agent often reaches a step where it is missing one parameter. Each time after the agent uses a tool, a small model on the side reads the conversation once. It decides whether to say nothing or to ask the user one specific question.

---

**Four parts in total, and only one is trained.** The agent that does the task is not trained. The clarifier (Qwen3-1.7B, with thinking mode on) is the only part that is trained. It is called once every time the task agent finishes using a tool. It reads the whole conversation and all the tool records so far. It outputs NO, or YES plus one question. Its prompt gives these rules. Ask only one question at a time, about what the user wants. Do not ask about things the tools can look up. Do not repeat a question that was already asked. The other two parts are a simulated user and a scorer. The scorer is the clarifier itself (its current version); scoring does not train it. It is used to measure "how easy the hidden goal text is to predict."

---

**How the clarifier is trained:** Each step uses 16 samples. For each sample, the clarifier writes 8 outputs (temperature 0.8). Each output is NO, or YES plus one question. Each question goes to a strict simulated user, who answers in one sentence. Then the outputs are scored. In the scoring step, the clarifier does not write anything. It is given the prompt "Sum up the user's hidden intent from the conversation," along with the conversation. Then the reference text (the true hidden intent given by the dataset) is put right after it, as if it were "its answer." The probability it gives to each token of the reference text is read out one by one (teacher forcing). Then the logs of these probabilities are averaged. This number tells how easy it is to predict the true goal text after seeing this conversation. It is computed twice: once on the conversation before the cut point, and once with this question and answer added. The difference is the reward. **The reward measures one thing: whether this question and answer made the true hidden intent easier to predict.** Why does the probability change? The reference text has specific tokens like "gift card 7711863." Once such tokens show up in the conversation, the model can copy them from the earlier text, so their probability goes up a lot. If they are not in the conversation, the model can only guess, so the probability is low. The reward for NO is set to 0. Take the rewards of the 8 outputs. From each one, subtract the group's average, then divide by the group's standard deviation. This gives the advantage. The advantage is multiplied onto every token of that output. So when NO gets strengthened depends on the scores of the other questions in the same group. If most questions get negative scores, NO is above the average. If most get positive scores, NO is below the average. This is the whole way that "when not to ask" is learned. The update uses DAPO (a version of GRPO with uneven lower and upper clipping bounds, 0.20 / 0.28). The learning rate is 5e-7, with 4 PPO epochs per batch. The plan was 2,010 steps. The reported results use the version from step 670.

---

**How testing works:** There are 115 unseen tasks in the retail domain and 50 tasks in the airline domain (training never saw this domain). The user (Qwen3-8B, temperature 1) says one line. The agent (temperature 0.01) replies or uses a tool. Each time after a tool is used, the clarifier (temperature 0) reads the whole history. If it outputs NO, nothing happens. If it outputs YES plus a question, the question is sent to the user. The answer is added to the end of the conversation, and the agent goes on. This continues until the user says STOP or the steps run out. In the main experiment, there is no limit on how many times the clarifier can ask. Only trained on Retail, without no other methods as baselines. 

---


客服类任务，agent 一边和用户对话一边调工具（τ-bench：零售域处理订单换货退货，航空域处理机票）。用户有一份隐藏目标，但不会一次说全，模拟用户的提示词要求"逐步透露"。agent 经常走到某一步时缺一个参数。在 agent 每调一次工具之后，有一个旁边的小模型看一遍对话，决定不说话，还是向用户问一句具体的问题

**总共有四个部件，只训一个**。 执行 agent不训。澄清器（Qwen3-1.7B，开思考模式）是唯一被训练的部件，每次 执行agent 调完工具就被调用一次，读到目前为止的全部对话和工具记录，输出 NO，或者 YES 加一个问题；提示词要求一次只问一个关于用户意图的问题，不问工具能查到的，不重复问过的。还有一个模拟用户和一个打分器，也就是澄清器自己的一份冻结副本，用来算"隐藏目标这段文字有多好预测"。

**澄清器怎么训**：每一步取 16 个样本。每个样本让澄清器写 8 个输出（温度 0.8），每个输出是 NO 或 YES 加一个问题。每个问题交给严格模拟用户答一句。然后打分。打分步骤里，冻结的澄清器不生成任何东西，把"根据对话总结用户的隐藏意图"这个提示词加上对话喂给它，再把参照文字（数据集给定的真实隐藏意图）直接接在后面当作"它的回答"，逐个读出它给参照文字每个 token 的概率（teacher forcing），取对数后平均。这个数的意思就是：看过这段对话之后，真实目标这段文字有多好预测。算两次（切口前的对话；再加上这一问一答），相减就是奖励。**奖励衡量的就是这一问一答有没有让真实的 hidden intent 更好预测**。概率为什么会变：参照文字里有"礼品卡 7711863"这种具体 token，对话里一旦出现了它，模型可以从上文复制，这些 token 的概率大幅上升；对话里没有它，模型只能猜，概率低。NO 的奖励定义为 0。8 个输出的奖励减组内均值、除组内标准差，得到优势，乘到这个输出的全部 token 上。所以 NO 什么时候被加强，取决于同一组里其他问题的分：大多数问题得负分，NO 就高于均值；大多数得正分，NO 就低于均值。这就是"何时不问"被学到的全部机制。更新用 DAPO（GRPO 的一个变体，裁剪上下界不对称 0.20 / 0.28），学习率 5e-7，每批 4 个 PPO 轮次。计划 2,010 步，报告的结果用第 670 步的版本。

**测试时怎么跑**：零售域 115 个没见过的任务，航空域 50 个任务（训练没见过这个域）。用户（Qwen3-8B，温度 1）说一句，agent（温度 0.01）回话或调工具；每次调完工具，澄清器（温度 0）读全部历史，输出 NO 就什么都不发生，输出 YES 加问题就把问题发给用户，回答接到对话后面，agent 继续。直到用户说 STOP 或步数用完。主实验不限制澄清次数。只在Retail上训，没跑其他方法。
