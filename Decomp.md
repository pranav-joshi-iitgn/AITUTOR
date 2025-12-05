We can decompose the Recursive ITS workflow like this :

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
    MC:(list[MC]|None)
    ) -> list[str]:
    """
    Predicts a sequence of mental steps taken by the student to do the physical step S, given his stance/work `Summ` so far, in context of the full conversation `convo`.
    Optionally, if the student has made an error with error description `ED`, and possible known misconceptions MC, predicts LE sequences that can induce that error.
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
    ) -> tuple[int,str]:
    """
    Gives the category of error (arithmetic,wrong formula, etc.) made by the student in step S, with summary Summ of previous work in context of conversation `convo`, and the possible learning even sequence LE.
    If there is no error, returns 0.
    Also returns a short one-line description of the error.
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

def KTU(alpha:dict[KC,float],beta[KC,float]):
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

def Teach(g:str):
    material = search_material(g)
```