from agent import Agent

class Hinter(Agent):
    def __init__(self,model="gpt-oss",system_prompt = "file:Hinter.txt", system_prompt2="file:Hinter2.txt", system_prompt3 = "file:Hinter3.txt"):
        if system_prompt2.startswith('file'):
            with open(system_prompt2.split(":",1)[1],'r') as f:
                system_prompt2 = f.read()
        if system_prompt3.startswith('file'):
            with open(system_prompt3.split(":",1)[1],'r') as f:
                system_prompt3 = f.read()
        super().__init__(model,system_prompt)
        self.sysprompt2 = system_prompt2
        self.sysprompt3 = system_prompt3
        self.turn = 0
        self.Summ = ""
        # self.hint_desc = [
        #     "R_B: Bottom-out hint. Give the student the direct step needed to correctly apply the KC and explain in detail the reasoning for the correct step.",
        #     "R_R: Reasoning hint. Explain the key idea or logic behind the KC and why it might be applicable here.",
        #     "R_T: Teaching hint. Give a concise instructional explanation of the KC, but don't relate it to the context.",
        #     "R_F: Prompting or fill-in-the-blank hint. Prompt the student to supply a missing step or idea tied to the KC. For example, \"We can separate the frequencies in a signal using ____.\"",
        #     "R_P: Pointing hint. Direct the student to the specific part of their earlier reasoning or the question/task that relates to the KC, but don't tell them what to do. For example, \"We are given a signal that seems to be composed of multiple frequencies\"",
        #     "R_M: Pump. Give a gentle nudge that encourages further thinking about the KC without giving any other information or directing attention to anything. For example, \"Let's look at the big picture again and retry." or "Just take a guess\".",
        # ]
        self.hint_desc = []
        for ht in ["R_B","R_R","R_T","R_F","R_P","R_M"]:
            with open(f"HD/{ht}.txt",'r') as f :
                self.hint_desc.append(f.read())
        
    def hint_old(self,E:str,Summ=None,convo=None,g=None,SP=None) -> list[str]:
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
        if convo is not None:
            self.turn = 0
            for msg in convo: 
                if not msg.strip():continue
                self.add_convo_message(msg.strip())
        if Summ is not None: self.Summ = Summ
        prompt = ""
        if self.convo: prompt += "\nConversation:\n" + "\n".join(self.convo)
        if self.Summ: prompt += "\n\nSummary:\n" + self.Summ
        prompt += "\n\nTarget Knowlege Concept to teach:\n" + E
        if g: prompt += "\n\nMain goal:\n" + g
        if SP: prompt += "\n\nPossible plan that student is following:\n" + SP
        HS = self.generate(prompt)
        prompt += "\nHints:\n" + HS
        HS = self.generate(prompt,self.sysprompt2)
        HS = [x.strip() for x in HS.split("\n") if x.strip()]
        assert len(HS) == 6 , f"Wrong number of hints: \n" + '\n'.join(HS)
        return HS

    def hint_seq(self,E:str,Summ=None,convo=None,g=None,SP=None) -> list[str]:
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
        if convo is not None:
            self.turn = 0
            for msg in convo: 
                if not msg.strip():continue
                self.add_convo_message(msg.strip())
        if Summ is not None: self.Summ = Summ
        prompt = ""
        if self.convo: prompt += "\nConversation:\n" + "\n".join(self.convo)
        if self.Summ: prompt += "\n\nSummary:\n" + self.Summ
        prompt += "\n\nTarget Knowlege Concept to teach:\n" + E
        if g: prompt += "\n\nMain goal:\n" + g
        if SP: prompt += "\n\nPossible plan that student is following:\n" + SP
        og_prompt = prompt
        L = []
        for desc in self.hint_desc:
            prompt = og_prompt + "\n\nHint Description:\n" + desc 
            res = self.generate(prompt,self.sysprompt3)
            L.append(res)
        return L

    def hint(self,E:str,Summ=None,convo=None,g=None,SP=None,level=0) -> str:
        """
        Summ is the summary of the student's work on a problem. The summary also refers to the conversation `convo` sometimed.
        E is the KC to teach. 
        Generates the bottom out hint R_B based on Summ
        Generates reasoning hint R_R,
        Generates the teaching hint R_T, 
        the prompting (fill in the blank) hint R_F,
        ,pointing hint R_P
        ,and the pump R_M
        """
        if convo is not None:
            self.turn = 0
            for msg in convo: 
                if not msg.strip():continue
                self.add_convo_message(msg.strip())
        if Summ is not None: self.Summ = Summ
        prompt = ""
        if self.convo: prompt += "\nConversation:\n" + "\n".join(self.convo)
        if self.Summ: prompt += "\n\nSummary:\n" + self.Summ
        prompt += "\n\nTarget Knowlege Concept to teach:\n" + E
        if g: prompt += "\n\nMain goal:\n" + g
        if SP: prompt += "\n\nPossible plan that student is following:\n" + SP
        prompt += "\n\nHint Description:\n" + self.hint_desc[level]
        return self.generate(prompt,self.sysprompt3)

    def add_convo_message(self,msg:str):
        role, msg = msg.split(":",1)
        role = role.strip().lower().capitalize()
        if role == "Tutor":self.turn += 1
        assert role in ["Tutor","Student"], f"unknown role {role}"
        self.convo.append(f"{self.turn}: {role} : {msg.strip()}")

class HintEvaluator(Agent):
    def __init__(self,model="gpt-oss",system_prompt = "file:HintEval.txt"):
        super().__init__(model,system_prompt)
    def evaluate(self,g:str,H:str,convo:list[str]=None):
        """
        Checks if the hint H is conversationally correct
        """
        self.convo = []
        self.speak(g)
        if convo is not None:
            for msg in convo: 
                if not msg.strip():continue
                if msg.lower().startswith("student"):
                    self.speak(msg.split(":",1)[1].strip())
                elif msg.lower().startswith("tutor"):
                    self.hear(msg.split(":",1)[1].strip())
        self.hear(H)
        res = self.speak()
        return (res.lower() in ["true","t",'y','yes','1','ok','good'])

    

if __name__ == "__main__":
    g = "What is the derivative of $x^12+3x$"
    convo = [
        "Tutor : What is the derivative of $x^12+3x$",
        "Student : It is $11x^11 + 3$",
        "Tutor : Are you sure? Do you remember what the derivative of x^n is ?",
        "Student : It is nx^{n-1}",
    ]
    Summ = "1. Derivative of x^12 + 3x is 11x^11+3 [S1].\n2. Derivative of x^n is nx^{n-1} [S2]"
    convo = []
    Summ = None
    E = "Power rule in differentiation"
    H = Hinter().hint(E,Summ,convo,g,level=4)
    print("Hint:",H)
    res = HintEvaluator().evaluate(g,H,convo)
    print("Hint Evaluator:",res)
