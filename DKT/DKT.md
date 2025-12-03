# Deep Knowledge Tracing

- Knowledge Tracing is the task of modeling knowledge of student over time, essentialy fine-grained assessment
- Bayesian Knowledge Tracing (BKT) uses Hidden Markov Models (HMM) to predict whether the student has mastered a knowledge component or not. The knowledge components are the nodes of the HMM. 
- Recent extension of BKT also account for randomness due to guessing and slips, as well as mastery decaying with time.
- Partially Observable Markov Decision Processes (POMDPs) has also been used. This is the most flexible in theory, but require exploration of a very large state space (latent variables).
- Performance Factors Analysis (PFA) and Learning Factors Analysis (LFA) have better accuracy than BKT.
- Emsemble methods show superior results to just BKT and PFA
- All these models involve labeling the knowledge components of a step by a human. 
  
In this paper, they used RNNs to predicts whether what problems the student will be able to do at any stage. 

For each question $q_i$ and answer $a_i$ pair in their dataset, they choose a random vector in a high dimensional space as the embedding $\vec x_i$. This is only possible becuase $q_i,a_i$ can be converted to question and answer numbers. Basically, it's only possible for MCQ type questions.

For each student, we have a sequence of these $q_t,a_t$ pairs at different times $t$. At time, $t$, the student has done all questions with $t' \le t$. The hidden state $h_t$ in the RNN represents the complex storage of the schema in the students LTM.

The output vector $y_t$ is a one-hot encoded vector that gives the probabilities of the student being able to answer a question.

This model is much more accurate than BKT or PFA, but isn't very interpretable.

This model can also be used to create the dependency graph of concepts. 

This is done by recording the computed probabilities that a question $q_j$ can be done by the student given that a question $q_i$ was done correctly in the last time step, namely $y(q_j|q_i)$. Then, these probabilities are used to compute this dependency measure:
$$
J(j|i) = \frac{y(q_j|q_i)}{\sum_k y(q_j|q_k)}
$$


The dependency graphs are actually really accurate.


# Problems

- They are just randomly assigning embedding. Using an embedding matrix might be better. It might also allow getting dependence more easily.
- They are not using the actual text for the question and answer.. just the number and answer option. That's not nice. To resolve this, we can use the sentence embeddings of the question and answers. 
- Why use RNNs when we can use transformers now. This is solved by SAKT which uses self-attention over skill emebeddings. The current SoTA is AlignKT. 

# Extra stuff

### 3PL ITR

They also mention the item response theory briefly. According to it, suppose a question/step $S$ involves a single knowledge concept $i$ with difficulty level of $\beta_{S,i} \in \mathbb{R}$. And suppose the proficiency of the student in that knowledge concept is $h_i \in \mathbb{R}$, then we have

$$
y_S = g_S + (1-g_S)\sigma (w_{S,i}(h_i-\beta_{S,i}))
$$

### MITR

Now, we extend to multiple concepts required for a step $S$ as :

$$
y_S = g_S + (1-g_S)\sigma (\sum_i w_{S,i}(h_i-\beta_{S,i})) \\
= g_S + (1-g_S)\sigma ([\sum_i w_{S,i}h_i] -b_S) \\ 
\text{where } b_S = \sum w_{S,i}\beta_{S,i}
$$

If we set $g_S = 0$, we get the familiar fully connected layer equation (in Neural Networks). This layer is converting the skill vector $\vector h$ to the success probability vector $y_i$.

Ofc this looses the extra parameters g_S which could've improved prediction. This is solved by the Deep-IRT paper that adds difficulty and discrimination to their DL model.