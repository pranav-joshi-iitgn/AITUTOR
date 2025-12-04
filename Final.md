# Recursive ITS

The outer loop is mostly irrelevant to what I am trying to do.

For the inner loop, let's define some notation :

- $t$ is a turn / time
- $S_t$ is the step done by the student, usually just the text input into a chatbox.
- $L_{t,i}$ is the $i^\text{th}$ learning event for a step (text).
- $\vec L_{t,i}$ is the sentence embedding of $L_t$
- $R_t$ is the response given by the tutor for step $S_t$
- $\vec r_t$ is the sentence embedding of $R_t$
- $\vec x_t$ is the sentence embedding of $S_t$
- $K_{t,i}$ is the knowledge component for the learning event $L_{t,i}$ (either text or number).
- $\vec k_{t,i}$ is the embedding for the knowledge component $K_{t,i}$
- $M_i$ is a known misconception (as text).
- $\vec m_i$ is the sentence embedding for the known misconception $M_i$.
- $\alpha_i \in \mathbb{R}$ is the mastery for a knowledge concept numbered $i$. This can be labelled or hidden.
- $\beta_{E,i} \in \mathbb{R}$ is the required mastery of a KC for a step $E_i$ to be done correctly.
- $\vec \beta_{E,i}$ is a vector with $\beta_{E,i}$ as the only non-zero entry.
- $E_t$ is the current KC to cover. 
- $y_t$ is the probability that $E_t$ will be convered in learing events for $S_t$ 
- $G$ is a stack of goals, with topmost element as current goal.

The inner loop goes like this:

1. $S_0$ is just student describing his problem / topic of interest. The student has master levels $\vec \alpha_{t=0}$. Initially, $G$ is empty.
2. Extract the current goal $g$ and add it to $G$.
3. while $G$ is not empty
4. ____Pop $G$ to get current goal $g$ (text)
5. ____Search material for teaching (using RAG pipeline)
6. ____State "Now, we are going to learn (or resuming) $g$" (conversation turn management)
7. ____Decomponse $g$ into pre-requisite KCs $\text{prereqs} = \{E_i\}_i$.
8. ____while $\text{prereps}$ is not empty
9.  _______From $\text{prereqs}$ pop $E_i$ with highest $\alpha_i - \beta_i$
10. _______# next step hint
11. _______if $\alpha_i-\beta_i$ is very low, 
12. __________put $g$ back in $G$
13. __________put $E_i$ in $G$. 
14. __________break to step 3
15. ______generate bottom out hint $R_B$ (the exact knowledge concept is given within the context)
16. ______generate reasoning hint $R_R$ (where facts are given in context of question)
17. ______generate teaching hint $R_T$ (where facts are given in abstract)
18. ______generate prompting (fill-in-the-blank) hint $R_F$ (where a relationship or categorisation is suggested)
19. ______generate pointing hint $R_P$ (where only attention is directed to a part of question)
20. ______generate pump $R_M$ (this only prompts the student to think more and doesn't bring attention to anything)
21. ______define hint sequence $\text{HS} = [R_B,R_R,R_T,R_F,R_P,R_M]$
22. ______Threshold $\alpha_i - \beta_i$ to give $\text{lev} \in \{0,1,2\}$
23. ______send $\text{HS}[\text{lev}]$ to student
24. ______$S$ is response by student.
25. ______# analysis of $S$
26. ______Expand/Complete $S$ in context of the past messages.
27. ______Expand $S_t$ by predicting the most probable sequence of learning events $L_{t,i}$.
28. ______if $S$ has an error
29. __________# Error specific feedback
30. __________categorise the kind of error made (arithmetic,wrong formula,etc.)
31. __________get the error-template for that kind of error.
32. __________Fill the error template in context of $S$
33. __________Convert the filled template to embedding $\vec e$
34. __________Search among $M_j$ for whom $\vec m_j\cdot \vec e$ is highest
35. __________Expand original $S_t$ by predicting the most probable sequence of learning events $L_{t,i}$, with $M_j$ included.
36. ______for each $L_{t,i}$, 
37. __________identify the knowledge component used, namely $K_{t,i}$
38. __________if $K_{t,i}$ is repeated, continue
39. __________Update $\vec \alpha$ for $K_{t,i}$ (via simple counters or complicated RNNs)
40. ______if $S$ had an error
41. __________re-define hints $R_B,R_R,R_T,R_F,R_P$ and generate minimal feedback $R_M$
42. __________define hint sequence $\text{HS} = [R_B,R_R,R_T,R_F,R_P,R_M]$
43. __________based on category of error, decrement $\text{lev}$
44. __________if $\text{lev}==0$ and $\text{len}(G)$ is small : 
45. _____________put $g$ back in $G$
46. _____________put $M_j$ (with error description) in $G$.
47. _____________break to step 3
48. ______while $S$ is not proceeding towards $E_i$
49. __________if $\text{lev}==0$ and $\text{len}(G)$ is small : 
50. _____________put $g$ back in $G$
51. _____________put $E_i$ in $G$.
52. _____________break to step 3
53. __________send $\text{HS}[\text{lev}]$ to student
54. __________$S$ is response by student.
55. __________decrement $\text{lev}$
56. ______Generate a response $R$ that summarises the learning for $E_i$
57. ______Send $R$ to student


This is mostly derived from working of AutoTutor, which uses most of the stages of socratic method, but doesn't use the self-contradiction or counter-example methods in Elenchus (the stage after hypothesis creation). It instead gives _hints_ to the student, directing attention to facts and parts of question.

The main goal is to devise how to _effectively_ extend the algorithm to also include self-contradiction.
Things that can be added are :

1. Clarification stage after student response. This also solves the unrecognisable error issue.
2. Setting an easier task as new goal when a misconception is found or when student is stuck (think, trial runs for finding a recursive relation)
3. A prepositional graph of $E_{i_1}\land E_{i_2}\implies \neg M_j$ that can facilitate self-contradiction.
4. Including timing to avoid help abuse and help refusal.
5. Analysis of partial solutions given by students.


Knowledge Tracing works perfectly for questions-answer pairs and tests, but not for discussions.
How to use DL to do student modeling here is an issue.