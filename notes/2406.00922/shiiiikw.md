---
name: "Kevin"
---

MediQ studies whether an LLM can ask follow-up questions when a clinical case is incomplete and decide when it has enough information to answer. At each turn, the doctor model assesses its confidence. If confidence is low, it asks a question and the patient model answers with relevant facts from the full case. In the best-performing setup, the doctor explains its judgment before rating its confidence on a five-point scale. It repeats the assessment three times and answers once the average rating reaches the threshold.

The authors adapt MedQA and CRAFT-MD into iMedQA and iCRAFT-MD. They keep the original question and answer choices. Initially, the doctor sees only the patient's age, sex, and chief complaint. It must ask for the remaining case details. The main experiments use Llama-3-8B, Llama-3-70B, GPT-3.5, and GPT-4. Baselines include Full information, Initial information, No information, and Basic, in which the model chooses whether to ask or answer. The stopping strategies use a binary confidence judgment, a numerical score from 0 to 1, a rating from 1 to 5, or a fixed number of questions. The authors also test the effects of explaining a judgment and sampling it repeatedly.
