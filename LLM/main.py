from GetInstr import InstructionCatcher
from Hinter import Hinter
from KCExtractor import KCExtractor, Sequencer
from summarisation import Summariser
from LEP import ErrorCatcher, ESF, LEFilter, LEPredictor, SEC, PlanPredictor, Clarifier

InstructionCatcher_agent = InstructionCatcher()
Hinter_agent = Hinter() 
KCExtractor_agent = KCExtractor() 
Summariser_agent = Summariser() 
ErrorCatcher_agent = ErrorCatcher() 
ESF_agent = ESF() 
LEFilter_agent = LEFilter() 
LEPredictor_agent = LEPredictor() 
SEC_agent = SEC() 
PlanPredictor_agent = PlanPredictor()
Clarifier_agent = Clarifier()
Sequencer_agent = Sequencer()

MAX_DEPTH = 3
MASTERY_THRESH = None
NUM_MISCON = None

def send(feedback_article:str,R:str,convo:list[str],S=None):
    global log
    if S is not None:convo.append("Student : " + S) 
    if R.startswith("R_") and ":" in R[:6]: R = R.split(":",1)[1]
    if feedback_article.strip():
        R = feedback_article.strip() + " "+ R
    print(R)
    log(R)
    convo.append("Tutor : " + R)

def ask(convo:list[str],prompt="> ") -> str:
    S = input(prompt)
    log("> " + S)
    return S

f = open("transcript.txt",'w')
def log(*args,**kwargs):
    global f
    print(*args,**kwargs,file=f,flush=True)

# TODO : Make a proper search
MATERIAL = {}
MATERIAL["Prove that square root of 2 is irrational."] = "\n".join([
        r"One can prove that root of a prime p is irrational by contradiction.",
        r"Suppose that root p were rational, then we can write \(\sqrt{p} = \frac{a}{b}\) where a and b are coprime integers and b is not 0",
        r"Then, we have \(p = \frac{a^2}{b^2}\) which implies that \(a^2 = pb^2\) is divisible by \(p\)",
        r"But that means \(a\) is divisible by \(p\) and that means \(a=kp\) which means \(a=k^2p^2\).",
        r"This means that \(k^2p^2 = pb^2 \implies k^2p = b^2\) and thus \(b^2\) is divisible by p",
        r"But then b is divisible by p. Thus, a and b, both a divisible by p and they aren't coprime.",
        r"Thus hypothesis is incorrect. Thus, p cannot be rational."
    ])
def search_material(g):return MATERIAL[g]

def Teach(
    g:str, # The goal
    Summ:str="", # A summary of the stance of the student
    mastery:dict = {}, # mastery of student in different KCs
    convo:list[str] = [], # The full conversation on this topic (excluding convo from new threads)
    depth:int=0, # How deep we are in recursion. Going too deep leads to frustration
    ):
    global MASTERY_THRESH,MAX_DEPTH,NUM_MISCON, log # constant parameters that can be set before run-time
    material:str = search_material(g)
    # log("material=")
    # log(material)
    # R = generate_next_topic_prompt(Summ,convo,g,"Great")
    # send("",R,convo)
    # prereqs:list = list(KCExtractor_agent.extract_E_i(g,material,False).keys())
    # log("prereqs=")
    # for x in prereqs: log(x)
    # prereqs = [g] # TODO: Need to figure out what tf AutoTutor was doing. 
    prereqs = Sequencer_agent.prerequisites(g,material)
    log("prereqs=")
    for x in prereqs: log(x)
    SP = None
    while len(prereqs) > 0:
        # E,lev = pop_next_E_i(mastery,prereqs,MASTERY_THRESH)
        E = prereqs.pop()
        log("E=" + str(E))
        lev = 5
        # # lev is not a level of mastery, but a level of "frustration"
        # if lev < 0 and depth < MAX_DEPTH:
        #     g_new = Create_new_goal_for_KC(g,Summ,convo,E)
        #     start_new_thread(g_new,mastery,depth+1,convo)
        #     continue # after teaching g_new
        HS = Hinter_agent.hint(E,Summ,convo,g,SP)
        log("HS =")
        for x in HS : log(x)
        send("",HS[lev],convo)
        S = ask(convo)
        LE = LEPredictor_agent.predict_Learning_Events(S,Summ,convo,None,None)
        log("LE=")
        for x in LE:log(x)
        new_LE = LEFilter_agent.filter_out_old_LE(S,Summ,convo,LE)
        log("new_LE=")
        for x in new_LE:log(x)
        new_Summ = Summariser_agent.summarise(S,convo,Summ)
        log("new_Summ=\n"+new_Summ)
        # predict plan from new_Summ, LE, convo, S
        SPC,SP =PlanPredictor_agent.predict_plan(g,E,new_Summ,LE,convo,S)
        log("SPC="+str(SPC))
        log("SP=\n"+SP)
        more = False
        for i in range(3): # ask for clarification
            if SPC != -1:break
            more = True
            clar = Clarifier_agent.clarification(g,E,new_Summ,LE,convo,S,SP)
            send("",clar,convo,S)
            S = ask(convo)
            new_Summ = Summariser_agent.summarise(S,convo,Summ)
            log("new_Summ= ")
            log(new_Summ)
            SPC,SP =PlanPredictor_agent.predict_plan(g,E,new_Summ,LE,convo,S)
            log("SPC="+str(SPC))
            log("SP=\n"+SP)
        if more:
            updated_convo = convo + ["Student : " + S]
            HS = Hinter_agent.hint(E,new_Summ,updated_convo,g,SP)
            log("HS =")
            for x in HS : log(x)
        if SPC == 1: # Again predict the plan that we need to take for teaching
            prereqs = Sequencer_agent.prerequisites(g,material,convo,new_Summ,S,SP,prereqs)
            log("prereqs=")
            for x in prereqs: log(x)
            send("","It seems you are doing something different than what I thought you would. I'll try to follow the path you are taking. Let's start over.",convo,S)
            continue
        # ET,SED,feedback_article = ErrorCatcher_agent.catch_error(Summ,convo,S,LE)
        if SPC == 0:
            ET = 0
            SED = "Student seems to be stuck. Potential plan : "+SP
        else:ET,SED = ErrorCatcher_agent.catch_error(Summ,convo,S,new_LE)
        log("ET =" + str(ET))
        log("SED = " + SED)
        # if ET > 0:
        #     ED = get_error_desc(Summ,convo,S,LE,ET,SED)
        #     possible_MC = get_misconcepts(ED,NUM_MISCON)
        #     LE = predict_Learning_Events(Summ,convo,S,ED,possible_MC)
        # learnt_KC = get_KCs(new_LE)
        # KTU(mastery,learnt_KC)
        if ET < 0: continue
        updated_convo = convo + ["Student : " + S]
        if ET > 0: HS = ESF_agent.generate_ESF_sequence(Summ,convo,S,LE,SED,None)
        elif ET ==0 :HS = Hinter_agent.hint(E,new_Summ,updated_convo,g,SP)
        convo = updated_convo
        lev -= 1
        log("HS=")
        for x in HS: log(x)
        # From this point onwards, the only focus will be on correcting the error
        # or helping the student start. Nothing that the student says in this section will be evaluated
        direct_ans = skip_E = False
        while (lev > 0 or direct_ans) and (not skip_E):
            log("lev="+str(lev))
            if direct_ans:
                lev = 0
                direct_ans = False
            send("Let's try again.",HS[lev],convo)
            S = ask(convo)
            instr = InstructionCatcher_agent.catch_instruction(S)
            log("instr="+str(instr))
            if instr == 0 or instr == 1: # skip
                send("OK, Let's skip this then.","",convo,S)
                skip_E = True
            elif instr == 2: lev -= 2 # stumped
            elif instr == 3: # asking for bottom out hint
                direct_ans = True
                send("I'll give you a direct answer then. But just this once.","",convo,S)
            elif instr== 4: # student is asking to discuss another thing.
                send("No. Stick to one task till end.","",convo,S) # TODO : Remove this in future
                # new_goal = Create_new_goal_from_Doubt(g,Summ,convo,S)
                # start_new_thread(new_goal,mastery,depth,convo)
                # skip_E = True # after teaching new goal
            else:
                good = SEC().is_correct(S,Summ,convo,E,None)
                log("good=",str(good))
                Summ = new_Summ
                if good is None: # partial application
                    LE = LEPredictor_agent.predict_Learning_Events(S,Summ,convo,None,None)
                    log("LE=")
                    for x in LE:log(x)
                    Summ = Summariser_agent.summarise(S,convo,Summ)
                    log("Summ= ")
                    log(Summ)
                    HS = Hinter_agent.hint(E,Summ,convo) # re-formulate hints baed on new conversation
                    log("HS =")
                    for x in HS : log(x)
                elif good: skip_E = True # student got it
                else: lev -= 1 # easier hint
                convo.append("Student : " + S)
        if skip_E: continue
        # # Now, lev == 0. We have two options
        # Summ = Summariser_agent.summarise(S,convo,Summ)
        # if depth < MAX_DEPTH:
        #     if ET > 1:g_new = Create_new_goal_for_MC(g,Summ,convo,ED,possible_MC)
        #     elif ET ==0 : g_new = Create_new_goal_for_KC(g,Summ,convo,E)
        #     start_new_thread(g_new,mastery,depth+1,convo)
        # else: send("",HS[0],convo) # bottom out hint
        send("",HS[0],convo)


if __name__ == "__main__":
    KCExtractor_agent.KCList = [
        "Proof by contradiction",
        "Hypothesis",
        "If a^2 is divisible by prime p, then a is divisible by prime p",
        "Definition of divisibility",
        "Definition of rational number and irrational number",
    ]
    g = "Prove that square root of 2 is irrational."
    Teach(g)