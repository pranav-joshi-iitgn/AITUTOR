from GetInstr import InstructionCatcher
from Hinter import Hinter, HintEvaluator
from KCExtractor import KCExtractor, Sequencer, GoalSetter
from summarisation import Summariser
from LEP import ErrorCatcher, ESF, LEFilter, LEPredictor, SEC, PlanPredictor, Clarifier
from agent import Agent, SummConvoAgent

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
HintEvaluator_agent = HintEvaluator()
Solution_agent = Agent(system_prompt="file:Solution.txt",model='gpt-oss')
Selector_agent = SummConvoAgent(system_prompt='file:Selector.txt')
GoalSetter_agent = GoalSetter()

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

def ask(convo:list[str],prompt=("-"*10 + "\n▶ ")) -> str:
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
    solution = Solution_agent.generate(f"Material\n:{material}\n\nGoal:\n{g}")
    log("solution=\n"+solution)
    prereqs = Sequencer_agent.prerequisites(g,solution,stage=1)
    log(f"prereqs (stage 1) =")
    for x in prereqs: log(x)
    for stage in [3,4]: # removed stage 2
        prereqs = Sequencer_agent.prerequisites(g,prereqs=prereqs,stage=stage)
        log(f"prereqs (stage {stage}) =")
        for x in prereqs: log(x)
    if not prereqs: prereqs = [g]
    prereqs = prereqs[::-1]
    log("prereqs=")
    for x in prereqs: log(x)
    SP = None
    while len(prereqs) > 0:
        # E,lev = pop_next_E_i(mastery,prereqs,MASTERY_THRESH)
        # prompt = Selector_agent.format_convo_summ(convo,Summ) + "\n\nKnowledge Components" + "\n".join(prereqs[::-1])
        # idx = Selector_agent.generate(prompt)
        # try: 
        #     idx = int(idx)
        #     E = prereqs.pop(idx)
        # except:
        #     E = prereqs.pop()
        E = prereqs.pop()
        log("E=" + str(E))
        if convo:
            good = SEC().is_correct(None,Summ,convo,E,None)
            log("good=",str(good))
            if good: continue
        lev = 4
        # # lev is not a level of mastery, but a level of "frustration"
        # if lev < 0 and depth < MAX_DEPTH:
        #     g_new = Create_new_goal_for_KC(g,Summ,convo,E)
        #     start_new_thread(g_new,mastery,depth+1,convo)
        #     continue # after teaching g_new
        # HS = Hinter_agent.hint_seq(E,Summ,convo,None,SP)
        for hl in range(lev,0,-1):
            log("hl=",str(hl))
            H = Hinter_agent.hint(E,Summ,convo,g,SP,hl)
            log("H="+H)
            good = HintEvaluator_agent.evaluate(g,H,convo)
            log("good="+str(good))
            if good:break
        else: H = Hinter_agent.hint(E,Summ,convo,g,SP,0)

        # log("HS =")
        # for x in HS : log("-"*10 + "\n" + x)
        # send("",HS[lev],convo)
        # log("H=\n"+H)
        send("",H,convo)
        S = ask(convo)
        new_Summ = Summariser_agent.summarise(S,convo,Summ)
        log("new_Summ=\n"+new_Summ)
        # LE = LEPredictor_agent.predict_Learning_Events(S,new_Summ,convo,None,None)
        # log("LE=")
        # for x in LE:log(x)
        # new_LE = LEFilter_agent.filter_out_old_LE(S,new_Summ,convo,LE)
        # log("new_LE=")
        # for x in new_LE:log(x)
        # predict plan from new_Summ, LE, convo, S
        SPC,SP =PlanPredictor_agent.predict_plan(g,E,Summ,None,convo,S)
        log("SPC="+str(SPC))
        log("SP=\n"+SP)
        more = False
        for i in range(3): # ask for clarification 
            if SPC != -1:break
            more = True
            clar = Clarifier_agent.clarification(g,E,new_Summ,None,convo,S,SP) # TODO : Add back LE once fixed
            send("",clar,convo,S)
            S = ask(convo)
            new_Summ = Summariser_agent.summarise(S,convo,new_Summ)
            log("new_Summ= ")
            log(new_Summ)
            SPC,SP =PlanPredictor_agent.predict_plan(g,E,new_Summ,None,convo,S) # TODO : Add back LE once fixed
            log("SPC="+str(SPC))
            log("SP=\n"+SP)
        # if more:
            # updated_convo = convo + ["Student : " + S]
            # Summ = new_Summ
            # HS = Hinter_agent.hint(E,Summ,updated_convo,None,SP)
            # log("HS =")
            # for x in HS : log("-"*10 + "\n" + x)
        if SPC == 1: # Again predict the plan that we need to take for teaching
            prereqs = Sequencer_agent.prerequisites(g,material,convo,new_Summ,S,SP,prereqs[::-1])
            log("prereqs=")
            for x in prereqs: log(x)
            send("","It seems you are doing something different than what I thought you would. I'll try to follow the path you are taking. Let's start over.",convo,S)
            continue
        # ET,SED,feedback_article = ErrorCatcher_agent.catch_error(Summ,convo,S,LE)
        if SPC == 0:
            ET = 0
            SED = "Student seems to be stuck. Potential plan : "+SP
        else:ET,SED = ErrorCatcher_agent.catch_error(new_Summ,convo,S,None)
        log("ET =" + str(ET))
        log("SED = " + SED)
        # if ET > 0:
        #     ED = get_error_desc(Summ,convo,S,LE,ET,SED)
        #     possible_MC = get_misconcepts(ED,NUM_MISCON)
        #     LE = predict_Learning_Events(Summ,convo,S,ED,possible_MC)
        # learnt_KC = get_KCs(new_LE)
        # KTU(mastery,learnt_KC)
        if ET < 0: continue
        convo = convo + ["Student : " + S]
        # if ET > 0: HS = ESF_agent.generate_ESF_sequence(Summ,convo[:-1],S,LE,SED,None)
        # elif ET ==0 :HS = Hinter_agent.hint_seq(E,new_Summ,convo,None,SP)
        lev -= 1
        # log("HS=")
        # for x in HS: log("-"*10 + "\n" + x)
        # From this point onwards, the only focus will be on correcting the error
        # or helping the student start. Nothing that the student says in this section will be evaluated
        direct_ans = skip_E = False
        old_Summ = Summ
        Summ = new_Summ
        while (lev > 0 or direct_ans) and (not skip_E):
            log("lev="+str(lev))
            if direct_ans:
                lev = 0
                direct_ans = False
            # send("Let's try again.",HS[lev],convo)
            if ET > 0 : H = ESF_agent.generate_ESF(Summ,convo[:-1],S,None,SED,None,lev)
            elif ET == 0 : H = Hinter_agent.hint(E,Summ,convo,None,SP,lev)
            log("H=" + H)
            send("",H,convo)
            S = ask(convo)
            instr = InstructionCatcher_agent.catch_instruction(convo + ["Student : " + S])
            log("instr="+str(instr))
            if instr == 0 or instr == 1: # skip
                send("OK, Let's skip this then.","",convo,S)
                skip_E = True
            elif instr == 2: lev -= 2 # stumped
            elif instr == 3: # asking for bottom out hint
                direct_ans = True
                send("I'll give you a direct answer then. But just this once.","",convo,S)
            elif instr== 4: # student is asking to discuss another thing.
                send("Ok, let's move to a new goal then","",convo,S) # TODO : Remove this in future
                new_goal = GoalSetter_agent.create_new_goal(convo)
                send("Let's talk about.." + new_goal,convo)
                new_convo = start_new_thread(new_goal,mastery,depth+1,[])
                convo.extend(new_convo)
                send("Now, let's come back",convo)
                skip_E = True # after teaching new goal
            elif instr==5: # student is telling us we are wrong
                ET,SED = ErrorCatcher_agent.catch_error(Summ,convo,S)
                send("I'm listening. Let me re-consider",'',convo,S)
                Summ = Summariser_agent.summarise(None,convo)
                if ET < 0 : 
                    send("",Clarifier_agent.clarification(g,E,None,None,convo[:-2],S,SP,SED),convo)
                    skip_E = True
            else:
                good = SEC().is_correct(S,old_Summ,convo,E,None)
                log("good=",str(good))
                Summ = new_Summ
                if good is None: # partial application
                    LE = LEPredictor_agent.predict_Learning_Events(S,Summ,convo,None,None)
                    log("LE=")
                    for x in LE:log(x)
                    Summ = Summariser_agent.summarise(S,convo,Summ)
                    log("Summ= ")
                    log(Summ)
                    # HS = Hinter_agent.hint(E,Summ,convo,None,SP) # re-formulate hints based on new conversation
                    # log("HS =")
                    # for x in HS : log("-"*10 + "\n" + x)
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
        H = Hinter_agent.hint(E,Summ,convo,None,SP,0)
        send("",H,convo) # bottom out hint

    return convo

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