from agent import Agent

class Hinter(Agent):
    def __init__(self,model="gpt-oss",system_prompt = "file:Hinter.txt"):
        super().__init__(model,system_prompt)
        self.turn = 0
        self.Summ = ""
    def hint(self,E:str,Summ=None,convo=None):
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
        HS = self.generate(prompt)
        HS = [x.strip() for x in HS.split("\n") if x.strip()]
        assert len(HS) == 6 , "Wrong number of hints"
        return HS
    def add_convo_message(self,msg:str):
        role, msg = msg.split(":",1)
        role = role.strip().lower().capitalize()
        if role == "Tutor":self.turn += 1
        assert role in ["Tutor","Student"], f"unknown role {role}"
        self.convo.append(f"{self.turn}: {role} : {msg.strip()}")

if __name__ == "__main__":
    convo = [
        "Tutor : What is the derivative of $x^12+3x$",
        "Student : It is $11x^11 + 3$",
        "Tutor : Are you sure? Do you remember what the derivative of x^n is ?",
        "Student : It is nx^{n-1}",
    ]
    Summ = "1. Derivative of x^12 + 3x is 11x^11+3 [S1].\n2. Derivative of x^n is nx^{n-1} [S2]"
    E = "Power rule in differentiation"
    agent = Hinter()
    HS = agent.hint(E,Summ,convo)
    print(HS)
