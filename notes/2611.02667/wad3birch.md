---
name: "Han Bao"
---

From a user's past conversations where they asked the AI to revise its answer, extract a vector representing "which direction this user wants answers to move".

When answering new questions later, this vector is added directly inside the model. Three steps: (1) for each user correction, compare the answer before and after and compute the shift; (2) average over all of this user's conversations; (3) when answering a new question, add the vector to the model's latent representation.
