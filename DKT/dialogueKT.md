# OKT (Open-ended Knowledge Tracing)

Normal DKT uses question-response pairs, where the question might be text or encoded as a number, and the response is either binary (correct or incorrect) or is converted into a correct-or-incorrect binary value.

OKT avoids the correct-or-incorrect restriction. Here, both the question and the response are converted to embeddings, the embeddings are concatenated and then fed into a RNN to update the hidden mastery state of the student.

# LLMKT

This is another leap towards conversation based assessment. Here, rather than questions and answers, we as student messages and tutor messages in a turn. From these, knowledge concepts are extracted. The knowledge concept enriched turn is then either fed into an LLM and the LLM is also prompted to find whether a particular KC was exhibited by the student. The same thing is repeated for all KCs.
This is done by using only the probabilities for the "true" and "false" tokens that the GPT (transformer) outputs.

The problem of needing labelled KCs is still there.

But this model does achieve slightly higher accuracy (68%) than BKT (~60%).

So, we will use simply BKT.

# Latent KC LLMKT

This is my proposed architecture. There are many flaws in this and I don't plan on using it.

Every KC is first articulated in text using am LLM. Then, using a sentence transformer, it is converted to an embedding.

Then, that embedding is further passed into a shallow neural network that gives the mastery of True Knowledge Concepts (TKC) which are numerous in numbers.

Let $K_i$ be the knowledge concept, $\vec k_i$ be the sentence embedding and $\vec \beta_i$ be the mastery in TKCs.

Now, for each turn, with teacher message T and student message S, we will 

1. Extract knowledge concepts $K_i$ from $T$ and $K_j$ from $S$.
2. Convert to embeddings $\vec k_i$ and $\vec k_j$
3. Feed into a neural network, with first a linear layer that converts $\vec k_i$ to $\vec \beta_i$ and $\vec k_j$ to $\vec \beta_j$, with $\vec\alpha$ (the student mastery) as another input to the NN (not input to the linear layer though)
4. Feed $\vec \beta_i$, and $\vec \alpha$ into a transformer to predict $\vec \beta_j$

The loss will simply be the RMSE between $\vec \beta_j$ and $\vec \beta_{j,\text{pred}}$. 

We can initialise the linear layer using PCA of KCs. 
Namely, extract a big corpus of verbalised KCs $K_i$. Convert each to embeddings $\vec k_i$. Some will be similar, some not. But the TKCs _must_ not be similar.
From here, we will construct the matrix $\bold{K} = [\vec k_i]_i$ and do QR decomposition as

$$
\bold{K} = W^T\bold{B} \iff
\bold{B} = W\bold{K} \iff
\vec \beta_i = W \vec k_i
$$

The weights will be initialised as $W$ and the bias will be initialised as $\vec b = -[\min_j{\beta_{i,j}}]_i$ for the linear layer, with ReLu activation.