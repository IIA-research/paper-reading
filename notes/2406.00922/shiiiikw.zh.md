---
name: "Kevin"
---

MediQ研究LLM在病例信息不完整时，能否主动追问，并判断什么时候可以回答医疗问题。它让医生模型每轮先判断自己有没有把握，没有把握就提问，病人模型从完整病例中选出相关事实回复；效果最好的设置是先解释判断理由，再按1—5级给信心打分，重复3次取平均值，达到阈值后作答。benchmark将MedQA和CRAFT-MD改成iMedQA和iCRAFT-MD，保留原题及选项，只给年龄、性别和主诉信息，其余病例信息需要询问才能获得。 主实验包括Llama-3-8B/70B、GPT-3.5和GPT-4，baseline包括Full information、Initial information、No information，以及让模型自行选择提问或作答的Basic。停止策略包括Binary（是／否置信判断）、Numerical（0—1打分）、Scale（1—5分级）和固定提问轮数，并测试解释判断理由、重复采样的效果。
