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
        res = self.generate(prompt)
        return res

    
if __name__ == "__main__":
    convo = [
        "Tutor : What is the derivative of $x^12+3x$",
        "Student : It is $11x^11 + 3$",
        "Tutor : Are you sure? Do you remember what the derivative of x^n is ?",
        "Student : It is nx^{n-1}",
        "Tutor : Good. Then what is the derivative of x^12?",
    ]
    Summ = "1. Derivative of x^12 + 3x is 11x^11+3 [S1].\n2. Derivative of x^n is nx^{n-1} [S2]"
    S = "It should be 12x^11 then"
    agent = LEPredictor()
    res = agent.predict_Learning_Events(S,Summ,convo)
    print(res)