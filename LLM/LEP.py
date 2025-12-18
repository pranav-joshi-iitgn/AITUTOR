from agent import SummConvoAgent,FullStateAgent

class LEPredictor(SummConvoAgent):
    def __init__(self,model="gpt-oss",system_prompt="file:LEP.txt",system_prompt2="file:LEP2.txt"):
        if system_prompt2.startswith('file:'):
            with open(system_prompt2.split(":",1)[1],'r') as f:
                system_prompt2 = f.read()
        super().__init__(system_prompt,model)
        self.sysprompt2 = system_prompt2


    def predict_Learning_Events(self,
        S:str,
        Summ:(str|None) = None, # before adding S
        convo:(list[str]|None) = None,
        ED:(str|None) = None,
        possible_MC:(list|None) = None
        ) -> list[str]:
        """
        Predicts a sequence of mental steps taken by the student to do the physical step S, given his stance/work `Summ` so far, in context of the full conversation `convo`.
        Optionally, if the student has made an error with error description `ED`, and possible known misconceptions `possible_MC`, predicts LE sequences that can induce that error.
        """

        prompt = self.format_convo_summ(convo,Summ)
        if ED is not None:
            prompt += "\nError Description:\n" + ED
        if possible_MC is not None:
            prompt += "\nPossible Misconceptions\n" + "\n".join("- " + m for m in possible_MC)
        LE = self.generate(prompt)
        LE = [x.strip("\n") for x in LE.split("\n\n")]
        LE = LE[0] # TODO : rank according to mastery to get most probable sequence
        prompt += "\nPossible Learning Events:\n" + LE
        LE = self.generate(prompt,self.sysprompt2)
        LE = [x.strip() for x in LE.split("\n") if x.strip()] 
        return LE

class LEFilter(SummConvoAgent):

    def __init__(self,model="gpt-oss",system_prompt="file:LEF.txt"):
        super().__init__(system_prompt,model)

    def filter_out_old_LE(self,
        S:str,
        Summ:str, # before step S
        convo:list[str],
        LE:list[str]
        ) -> list[str]:
        """
        Given learning events that occured for a step S, filters out those that have already occured before in the conversation `convo` till step S, summaried as `Summ`.
        """
        if len(LE) == 0 : return LE
        prompt = self.format_convo_summ(convo,Summ)
        prompt += "\nStudent's new response:\n" + S
        prompt += "\nLearning Events:\n" + "\n".join(LE)
        LE = self.generate(prompt)
        LE = [x.strip() for x in LE.split("\n") if x.strip()]
        return LE
    
class ErrorCatcher(SummConvoAgent):
    def __init__(self,model="gpt-oss",system_prompt="file:ErrorCatcher.txt"):
        super().__init__(system_prompt,model)

    def catch_error(self,
        Summ:str, # before adding S
        convo:list[str],
        S:str,
        LE:list[str]
        ) -> tuple[int,str]:
        """
        Gives the category of error (arithmetic,wrong formula, etc.) made by the student in step S, with summary Summ of previous work in context of conversation `convo`, and the possible learning even sequence LE.
        If there is no error, returns -1.
        If the student reports he/she is stuck, returns 0.
        Also returns a short one-line description of the error.
        """
        prompt = self.format_convo_summ(convo,Summ)
        prompt += "\nStudent's new response:\n" + S
        if LE : prompt += "\nPossible Learning Events:\n" + "\n".join(LE)
        error = self.generate(prompt).strip("\n").strip()
        error = error.split("\n")
        assert len(error) == 2, f"Bad formatting:\n{error}"
        error_code = int(error[0])
        error_desc = error[1]
        return error_code,error_desc

class ESF(SummConvoAgent):
    def __init__(self,model="gpt-oss",system_prompt="file:ESF.txt",system_prompt2="file:ESF2.txt"):
        if system_prompt2.startswith("file"):
            with open(system_prompt2.split(":",1)[1],'r') as f:
                system_prompt2 = f.read()
        super().__init__(system_prompt,model)
        self.sysprompt2 = system_prompt2
        self.FD = []
        for x in ["R_B","R_R","R_T","R_F","R_P","R_M"]:
            with open(f"ESF/{x}.txt",'r') as f:
                self.FD.append(f.read())

    def generate_ESF_sequence(self,
        Summ:str, # before Step S
        convo:list[str],
        S:str, # faulty step by student
        LE:list[str], # possible learning events
        ED:str, # Error description
        possible_MC:(list|None)=None, # Possible misconceptions
        attempts=0
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

        prompt = self.format_convo_summ(convo,Summ)
        prompt += "\nStudent's new response:\n" + S
        if LE : prompt += "\nPossible Learning Events:\n" + "\n".join(LE)
        if ED : prompt += "\nPossible Error:\n" + ED
        HS_0 = HS = self.generate(prompt)

        try:
            HS = HS.split("\n")
            HS = [x for x in HS if x.strip()]
            assert len(HS) == 6, f"Incorrect HS:\n{HS}"
            return HS
        except:
            sysprompt = (
            "You are a formatting expert. You will be given statements/hints that you need to put in a specific format given WITHOUT changing the content." 
            + "\nThe format is:\nR_B : ....\nR_R : .....\nR_T : .....\nR_F : .....\nR_P : .....\nR_M : ....."
            + "\n\nIn case it's not easy to figure it out, just return 0, with no other text."
            )
            prompt = f"Statements : \n{HS}\n"
            HS = HS_0.strip("\n").strip().strip("\n")
            HS = self.generate(HS)
        try:
            HS = int(HS)
            assert HS == 0
            if HS == 0 and attempts < 2: 
                return self.generate_ESF_sequence(Summ,convo,S,LE,ED,possible_MC,attempts+1)
        except:pass
        HS = HS.split("\n")
        HS = [x for x in HS if x.strip()]
        assert len(HS) == 6, f"Incorrect HS:\n{HS}"
        return HS


    def generate_ESF(self,
        Summ:str, # before Step S
        convo:list[str],
        S:str, # faulty step by student
        LE:list[str], # possible learning events
        ED:str, # Error description
        possible_MC:(list|None)=None, # Possible misconceptions
        level=0, # The level of feedback
        ) -> str:
        """ 
        Generates Error-Specific-Feedback (ESF) at different levels:
        - Clarification R_B goes in detail about what mistake the student might have made, as well as presents LE to the student
        - Socratic question R_R : Questions the student by presenting a counter-example, or by finding prepositions A,B from which falsity of step S follows, and deriving not-S (nor not-C where C is a false preposition). 
        - Socratic nudge R_T : Just presents a counter-example or finds prepositions A,B that student made earlier from which the falsity of the step S follows.
        - Pointing hint R_P : asks student to check for a specific kind of mistake
        - Pump R_M : Just asks student to check for any mistakes
        returns a hint 
        """
        
        prompt = self.format_convo_summ(convo,Summ)
        if S : prompt += "\nStudent's new response:\n" + S
        if LE : prompt += "\nPossible Learning Events:\n" + "\n".join(LE)
        if ED : prompt += "\nPossible Error:\n" + ED
        prompt += "\nFeedback Description : " + self.FD[level]
        return self.generate(prompt,self.sysprompt2)

class SEC(SummConvoAgent):
    def __init__(self,model="gpt-oss",system_prompt="file:SEC.txt"):
        "Simple Error Catcher"
        super().__init__(system_prompt,model)
    def is_correct(self,
        S:str,
        Summ:str,
        convo:list[str],
        E,
        possible_MC:(list|None) = None
        ) -> (bool|None):
        """
        Checks if the step is correct and matches with the KC E
        or still contains any of the misconceptions `possible_MC`
        """
        prompt = self.format_convo_summ(convo,Summ)
        if S : prompt += "\nStudent's new response:\n" + S
        # prompt += "\nPossible Learning Events:\n" + "\n".join(LE)
        if E : prompt += "\nKnowledge Concept\n" + str(E)
        if possible_MC is not None: 
            prompt += "\nMisconceptions:\n" + "\n".join(
                ["- " + str(x) for x in possible_MC])
        good = self.generate(prompt).strip("\n").strip()
        if good.lower() in ["false","no","n"]:return False
        elif good.lower() in ["true","yes","y"]:return True
        elif good.lower() in["partial","incomplete","almost"]:return None
        return bool(int(good))

class PlanPredictor(FullStateAgent):
    def __init__(self,model="gpt-oss",system_prompt='file:plan.txt'):
        super().__init__(model,system_prompt)
    def predict_plan(self,g,E,new_Summ, LE, convo, S,ED = None,possible_MC=None) -> str:
        prompt = self.format_convo_summ(S,convo,new_Summ,LE,ED,possible_MC)
        if E : prompt += "\n\nKnowledge Concept:\n" + E
        prompt += "\n\nMain Goal:\n" + g
        plan = self.generate(prompt).strip().strip("\n").strip()
        code,plan = plan.split("\n",1)
        code = int(code)
        return code,plan

class Clarifier(FullStateAgent):
    def __init__(self,model="gpt-oss",system_prompt='file:clarify.txt'):
        super().__init__(model,system_prompt)
    def clarification(self,g,E,new_Summ,LE,convo,S,SP,ED=None,possible_MC=None) -> str:
        """
        Asks the student for clarification
        """
        prompt = self.format_convo_summ(S,convo,new_Summ,LE,ED,possible_MC)
        prompt += "Knowledge Concept:\n" + E
        prompt += "Main Goal:\n" + g
        prompt += "Student's plan:\n" + SP
        return self.generate(prompt).strip().strip("\n").strip()

if __name__ == "__main__":
    convo = [
        "Tutor : What is the derivative of \(x^12+3x\)",
        "Student : It is \(11x^11 + 2\)",
        "Tutor : Are you sure? Do you remember what the derivative of x^n is ?",
        "Student : It is nx^{n-1}",
        "Tutor : Good. Then what is the derivative of x^12?",
    ]
    g = "Derivative of \(x^12+3x\)"
    Summ = "1. Derivative of \(x^12 + 3x\) is \(11x^11+3\) [S1].\n2. Derivative of x^n is nx^{n-1} [S2]"
    S = "It should be 12x^11 then. So, the answer should be 12x^11 + 2"
    E = "Derivatives of polynomials"

    LE = LEPredictor().predict_Learning_Events(S,Summ,convo)
    print("Unfiltered:")
    for x in LE : print(x)

    SPC,SP = PlanPredictor().predict_plan(g,E,Summ,LE,convo,S)
    print("Student Plan Code:",SPC)
    print("Student Plan:\n"+SP)

    clarification = Clarifier().clarification(g,E,Summ,LE,convo,S,SP)
    print("Clarification:\n" +clarification)

    LE = LEFilter().filter_out_old_LE(S,Summ,convo,LE)
    print("Filtered")
    for x in LE: print(x)

    good = SEC().is_correct(S,Summ,convo,E,None)
    print("Is Correct ? :",good)

    ET,SED = ErrorCatcher().catch_error(Summ,convo,S,LE)
    print("Error type : ",ET)
    print("Short Error Description :",SED)

    HS = ESF().generate_ESF_sequence(Summ,convo,S,LE,SED,None)
    print("ESF:")
    for x in HS : print(x)