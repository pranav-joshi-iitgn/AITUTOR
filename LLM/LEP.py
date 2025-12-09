from agent import SummConvoAgent

class LEPredictor(SummConvoAgent):
    def __init__(self,model="gpt-oss",system_prompt="file:LEP.txt"):
        super().__init__(system_prompt,model)

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
        LE = [[x.strip() for x in y.split("\n") if x.strip()] for y in LE]
        # TODO : rank according to mastery to get most probable sequence
        return LE[0]

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
        prompt += "\nPossible Learning Events:\n" + "\n".join(LE)
        error = self.generate(prompt).strip("\n").strip()
        error = error.split("\n")
        assert len(error) == 2, f"Bad formatting:\n{error}"
        error_code = int(error[0])
        error_desc = error[1]
        return error_code,error_desc

class ESF(SummConvoAgent):
    def __init__(self,model="gpt-oss",system_prompt="file:ESF.txt"):
        super().__init__(system_prompt,model)

    def generate_ESF_sequence(self,
        Summ:str, # before Step S
        convo:list[str],
        S:str, # faulty step by student
        LE:list[str], # possible learning events
        ED:str, # Error description
        possible_MC:(list|None)=None # Possible misconceptions
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
        prompt += "\nPossible Learning Events:\n" + "\n".join(LE)
        prompt += "\nPossible Error:\n" + ED
        HS = self.generate(prompt)
        HS = HS.strip("\n").strip().split("\n")
        HS = [x for x in HS if x.strip()]
        assert len(HS) == 6, f"Incorrect HS:\n{HS}"
        return HS

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
        prompt += "\nStudent's new response:\n" + S
        prompt += "\nPossible Learning Events:\n" + "\n".join(LE)
        prompt += "\nKnowledge Concept\n" + str(E)
        if possible_MC is not None: 
            prompt += "\nMisconceptions:\n" + "\n".join(
                ["- " + str(x) for x in possible_MC])
        good = self.generate(prompt).strip("\n").strip()
        if good.lower() in ["false","no","n"]:return False
        elif good.lower() == ["true","yes","y"]:return True
        elif good.lower() in["partial","incomplete","almost"]:return None
        return bool(int(good))

if __name__ == "__main__":
    convo = [
        "Tutor : What is the derivative of $x^12+3x$",
        "Student : It is $11x^11 + 2$",
        "Tutor : Are you sure? Do you remember what the derivative of x^n is ?",
        "Student : It is nx^{n-1}",
        "Tutor : Good. Then what is the derivative of x^12?",
    ]
    Summ = "1. Derivative of x^12 + 3x is 11x^11+3 [S1].\n2. Derivative of x^n is nx^{n-1} [S2]"
    S = "It should be 12x^11 then. So, the answer should be 12x^11 + 2"
    E = "Derivatives of polynomials"

    LE = LEPredictor().predict_Learning_Events(S,Summ,convo)
    print("Unfiltered:")
    for x in LE : print(x)

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