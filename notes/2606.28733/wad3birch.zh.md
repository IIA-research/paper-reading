---
name: "Han Bao"
---

benchmark paper

没有user参与，但是问user也属于abstention；每一步agent有三种选择：行动，作答和放弃；

三个场景：webshop（分为能做和不能做的，其中不能做的分为两种：环境中没有目标商品，二是请求有问题），terminal-bench（能做，前提错误或自相矛盾。意图不明确，缺少必要条件），absentation bench。

及时放弃率（AbsRec@K）：在该放弃的题目里，agent 在"最早可以判断出该放弃的那一步"之后的 K 步内放弃的比例。
