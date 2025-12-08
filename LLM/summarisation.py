from agent import Agent

class Summariser(Agent):
    def __init__(self,model="gpt-oss",system_prompt='file:summarisation.txt'):
        super().__init__(model,system_prompt)
        self.turn = 0
        self.Summ = ""
    def summarise(self,S:str,convo:(str|None)=None,Summ:(str|None)=None) -> str:
        """
        `convo` is the conversation done till now.
        `Summ` is a summary of student's work/stance/reasoning on a topic
        `S` is a new response by the student
        Returns an updated summary of the conversation.
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
        prompt += "\n\nStudent's new response:\n" + S
        print(prompt)
        res = self.generate(prompt)
        return res
    def format_convo_summ(convo=None,Summ=None):
        if convo is not None:
            self.turn = 0
            for msg in convo: 
                if not msg.strip():continue
                self.add_convo_message(msg.strip())
        if Summ is not None: self.Summ = Summ
        prompt = ""
        if self.convo: prompt += "\nConversation:\n" + "\n".join(self.convo)
        if self.Summ: prompt += "\n\nSummary:\n" + self.Summ
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
        "Tutor : Good. Then what is the derivative of x^12?",
    ]
    Summ = "1. Derivative of x^12 + 3x is 11x^11+3 [S1].\n2. Derivative of x^n is nx^{n-1} [S2]"
    S = "It should be 12x^11 then"
    agent = Summariser()
    res = agent.summarise(S,convo,Summ)
    print(res)
