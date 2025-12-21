from agent import Agent

class InstructionCatcher(Agent):
    def __init__(self,model="gpt-oss",system_prompt="file:GetInst.txt"):
        super().__init__(model,system_prompt)
    def catch_instruction_old(self,S:str) -> (int|None):
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
        res = self.generate("Student's message :\n"+S).strip("\n").strip()
        if res.lower() == "none": return None
        return int(res)
    def catch_instruction(self,convo:list[str]) -> (int|None):
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
        self.convo = []
        for msg in convo:
            if msg.startswith("Student"):
                self.hear(msg.split(":",1)[1])
            elif msg.startswith("Tutor"):
                self.speak(msg.split(":",1)[1])
        return self.speak()

if __name__=="__main__":
    ag = InstructionCatcher()
    prompts = [
        "I've had enough. Can we stop?",
        ]
    for x in prompts:
        print("Student:",x)
        print("Instruction:",ag.catch_instruction(x))

