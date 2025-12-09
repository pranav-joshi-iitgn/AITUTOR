from agent import Agent

class InstructionCatcher(Agent):
    def __init__(self,model="gpt-oss",system_prompt="file:GetInst.txt"):
        super().__init__(model,system_prompt)
    def catch_instruction(self,S:str) -> (int|None):
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

if __name__=="__main__":
    ag = InstructionCatcher()
    prompts = [
        "I've had enough. Can we stop?",
        ]
    for x in prompts:
        print("Student:",x)
        print("Instruction:",ag.catch_instruction(x))

