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


# Possible algorithm

After considering all possible ways to implement a recursive ITS that can use the socratic method effectively, this is the algorithm that I have devised :

```python
def Teach(
    g:str, # The goal
    Summ:str, # A summary of the stance of the student
    mastery:dict[KC,float], # mastery of student in different KCs
    convo:list[str], # The full conversation on this topic (excluding convo from new threads)
    depth:int=0, # How deep we are in recursion. Going too deep leads to frustration
    ):
    global MASTERY_THRESH,MAX_DEPTH,NUM_MISCON # constant parameters that can be set before run-time
    material:str = search_material(g)
    R = generate_next_topic_prompt(Summ,convo,g,"Great")
    send("",R,convo)
    prereqs = extract_E_i(g,material,False)
    while len(prereqs) > 0:
        E,lev = pop_next_E_i(mastery,prereqs,MASTERY_THRESH)
        # lev is not a level of mastery, but a level of "frustration"
        if lev < 0 and depth < MAX_DEPTH:
            g_new = Create_new_goal_for_KC(g,Summ,convo,E)
            start_new_thread(g_new,mastery,depth+1,convo)
            continue # after teaching g_new
        HS = generate_hint_sequence(Summ,convo,E)
        send("",HS[lev],convo)
        S = ask(convo)
        LE = predict_Learning_Events(Summ,convo,S,None,None)
        new_Summ = summarise(Summ,convo,S)
        ET,SED,feedback_article = catch_error(Summ,convo,S,LE)
        if ET > 0:
            ED = get_error_desc(Summ,convo,S,LE,ET,SED)
            possible_MC = get_misconcepts(ED,NUM_MISCON)
            LE = predict_Learning_Events(Summ,convo,S,ED,possible_MC)
        new_LE = filter_out_old_LE(Summ,convo,S,LE)
        learnt_KC = get_KCs(new_LE)
        KTU(mastery,learnt_KC)
        if ET < 0: return
        if ET > 0: HS = generate_ESF_sequence(Summ,convo,S,LE,ED,possible_MC)
        # From this point onwards, the only focus will be on correcting the error
        # or helping the student start. Nothing that the student says in this section will be evaluated
        direct_ans = skip_E = False
        while (lev > 0 or direct_ans) and (not skip_E):
            if direct_ans:
                lev = 0
                direct_ans = False
            send("Let's try again.",HS[lev],convo)
            S = ask(convo)
            instr = catch_instruction(S)
            if instr == 0 or instr == 1: # skip
                send("OK, Let's skip this then.","",convo)
                skip_E = True
            elif instr == 2: lev -= 2 # stumped
            elif instr == 3: # asking for bottom out hint
                direct_ans = True
                send("I'll give you a direct answer then. But just this once.","",convo)
            elif instr== 4: # student is asking to discuss another thing.
                new_goal = Create_new_goal_from_Doubt(g,Summ,convo,S)
                start_new_thread(new_goal,mastery,depth,convo)
                skip_E = True # after teaching new goal
            elif is_correct(S): skip_E = True # student got it
            else: lev -= 1 # easier hint
        if skip_E: continue
        # Now, lev == 0. We have two options
        Summ = summarise(new_Summ,convo,S)
        if depth < MAX_DEPTH:
            if ET > 1:g_new = Create_new_goal_for_MC(g,Summ,convo,ED,possible_MC)
            elif ET ==0 : g_new = Create_new_goal_for_KC(g,Summ,convo,E)
            start_new_thread(g_new,mastery,depth+1,convo)
        else: send("",HS[0],convo) # bottom out hint
```

The functions and classes that will need to be implemented for this are

```python
class KC:
    """
    representation of a Knowledge Concept
    """
    id:(int|str) # unique identifier for the KC. Can be an integer or a string depending on implementation
    text:str # the actual text for the KC, might be None
    embedding # the sentence embedding of the KC

class MC(KC):
    """
    A kind of knowledge concept that is not good to have. 

    In addition to other attributes of a KC, it also has a list of KC learning which can remedy the MC, in decreasing priority.

    This can be used for self-contradiction, for example.
    """
    remedies:list[KC] 

def search_material(g:str) -> str:
    """
    Given goal g, searches relevant material.
    """

def extract_E_i(
    g:str,
    material:str,
    full_map:bool
    ) -> dict[KC,float]:
    """
    Given goal g and meatrial, extracts pre-requisite KCs and mastery levels required.
    These KCs are set by the instructor.
    Returns a mapping from goal KCs to the mastery level required.
    The map can be full or shortened (via thresholding of mastery levels)
    """

def pop_next_E_i(
    alpha:dict[KC,float],
    beta:dict[KC,float],
    thresh:float
    ) -> tuple[KC,int]:
    """
    Extracts KC `E` in beta with highest value of `alpha[E] - beta[E]` under a threshold `thresh`.
    Threshold the alpha[E] - beta[E] values to get `lev` (an integer)
    Returns tuple `(E, lev)`
    """

def summarise(
    Summ:str,
    convo:list[str],
    S:str
    ) -> str:
    """
    `convo` is the conversation done till now.
    `Summ` is a summary of student's work/stance/reasoning on a topic
    `S` is a new response by the student
    Returns an updated summary of the conversation.
    """

def generate_hint_sequence(
    Summ:str,
    convo:list[str],
    E:KC,
    ) -> list[str]:
    """
    Summ is the summary of the student's work on a problem. The summary also refers to the conversation `convo` sometimed.
    E is the KC to teach. 
    Generates the bottom out hint R_B based on Summ
    Generates reasoning hint R_R,
    Generates the teaching hint R_T, 
    the prompting (fill in the blank) hint R_F,
    ,pointing hint R_P
    ,and the pump R_M
    returns hint sequence [R_B,R_R,R_T,R_F,R_P,R_M]
    """

def predict_Learning_Events(
    Summ:str, # before adding S
    convo:list[str],
    S:str,
    ED:(str|None),
    possible_MC:(list[MC]|None)
    ) -> list[str]:
    """
    Predicts a sequence of mental steps taken by the student to do the physical step S, given his stance/work `Summ` so far, in context of the full conversation `convo`.
    Optionally, if the student has made an error with error description `ED`, and possible known misconceptions `possible_MC`, predicts LE sequences that can induce that error.
    """

def filter_out_old_LE(
    Summ:str, # before step S
    convo:list[str],
    S:str,
    LE:list[str]
    ) -> list[str]:
    """
    Given learning events that occured for a step S, filters out those that have already occured before in the conversation `convo` till step S, summaried as `Summ`.
    """

def get_KCs(LE:list[str]) -> dict[KC,float]:
    """
    Identifies Knowledge concepts involved in the sequence of learning events (LE) as well as difficulty for applying each KC for the learning events.

    This can be used for predicting best LE path as well as for knowledge tracing updates (KTU).
    """

def catch_error(
    Summ:str, # before adding S
    convo:list[str],
    S:str,
    LE:list[str]
    ) -> tuple[int,str,str]:
    """
    Gives the category of error (arithmetic,wrong formula, etc.) made by the student in step S, with summary Summ of previous work in context of conversation `convo`, and the possible learning even sequence LE.
    If there is no error, returns -1.
    If the student reports he is stuck, returns 0.
    Also returns a short one-line description of the error,
    and feeback article ("Great","Good","Not-quite",etc.).
    """

def get_error_desc(
    Summ:str, # summary of work before S
    convo:list[str], # conversation before S
    S:str, # last step done by student
    LE:list[str], # predicted learning events in S
    ET:int, # category of error
    SED:str # a short desc. of error
    ) -> str:
    """
    Gets a template for the given error category `ET`, and fills the slots using the information given such as the 
    """

def get_misconcepts(ED:str,k:int) -> list[MC]:
    """
    Gets top k misconceptions M_j for whom the embedding e of the error description ED matches with their embedding m_j.

    Optionally, one might filter based on total effect of remedial KCs mastered by the student (prior), which would give a score for each MC, describing a posterior probability of not having that misconception.
    """

def KTU(alpha:dict[KC,float],beta:[KC,float]):
    """
    Knowledge Tracing Update
    Updates `alpha`, the mapping of required KCs to their mastery by the student by using the KCs applied in the learning events LE and the difficulty of application.

    I still don't know what a good update rule might be.
    """

def generate_ESF_sequence(
    Summ:str, # before Step S
    convo:list[str],
    S:str, # faulty step by student
    LE:list[str], # possible learning events
    ED:str, # Error description
    possible_MC:list[MC] # Possible misconceptions
    ) -> list[str]:
    """ 
    Generates Error-Specific-Feedback (ESF) at different levels:
    - Clarification R_B goes in detail about what mistake the student might have made, as well as presents LE to the student
    - Socratic question R_R : Questions the student by presenting a counter-example, or by finding prepositions A,B from which falsity of step S follows, and deriving not-S (nor not-C where C is a false preposition). 
    - Socratic nudge R_T : Just presents a counter-example or finds prepositions A,B that student made earlier from which the falsity of the step S follows.
    - Pointing hint R_P : asks student to check for a specific kind of mistake
    - Pump R_M : Just asks student to check for any mistakes
    returns sequence [R_B,R_R,R_T,R_F,R_P,R_M]
    """

def generate_next_topic_prompt(
    Summ:(str|None),
    convo:list[str],
    g:str,
    feedback_article:str,
    ) -> str:
    """
    States things like 
    "<feedback_article>. Now we are going to learn topic <g>"
    """

def catch_instruction(S:str) -> (int|None):
    """
    Analyses the input by student and checks for any explicit 
    instructions that the student might be giving, namely
    0. I want to skip this task. 
    1. I have understood it by myself. We can move on.
    2. I'm having difficulty in getting started.
    3. Just give the answer.
    4. Student has doubt in another concept
    Returns None if nothing found
    """

def is_correct(
    S:str,
    Summ:str,
    convo:list[str],
    E:KC,
    possible_MC:list[MC]
    ) -> bool:
    """
    Checks if the step is correct and matches with the KC E
    or still contains any of the misconceptions `possible_MC`
    """

def send(feedback_article:str,R:str,convo:list[str]):
    if feedback_article.strip():
        R = feedback_article.strip() + " "+ R
    print(R)
    convo.append("Tutor : " + R)

def ask(convo:list[str],prompt="> ") -> str:
    S = input(prompt)
    convo.append("Student : " + S)
    return S

def create_new_goal_for_MC(
    old_goal:str,
    Summ:str,
    convo:list[str],
    ED:str,
    possible_MC:list[MC]
    ) -> str:
    """
    Creates a new goal, mainly to fix a misconception
    """

def create_new_goal_for_KC(
    old_goal:str,
    Summ:str,
    convo:list[str],
    E:KC,
    ) -> str:
    """
    Creates a new goal, mainly to teach a pre-requisite
    KC E.
    """

def create_new_goal_from_Doubt(
    old_goal:str,
    Summ:str,
    convo:list[str],
    S:str,
    ) -> str:
    """
    Creates a new goal, mainly to rectify a doubt explicitly presented in S
    """

def start_new_thread(g,mastery,depth,convo):
    send("Let's discuss a few things first.","",convo)
    Teach(g_new,"",mastery,[],depth) # starting fresh for this
    send("Great. Now let's go back.","",convo)
```