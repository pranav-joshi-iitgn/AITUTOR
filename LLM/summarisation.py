from agent import Agent

class Summariser(Agent):
    def __init__(self,model="qwen3:4B",system_prompt=None):
        if system_prompt is None:
            f = open('summarisation.txt','r')
            system_prompt = f.read()
            f.close()
        super().__init__(model,system_prompt)
    
if __name__ == "__main__":
    example = "\n".join([
        "Conversation",
        "1: Tutor : What is the derivative of $x^12+3x$",
        "1: Student : It is $11x^11 + 3$",
        "2: Tutor : Are you sure? Do you remember what the derivative of x^n is ?",
        "2: Student : It is nx^{n-1}",
        "3: Tutor : Good. Then what is the derivative of x^12?",
        "",
        "Summary :",
        "1. Derivative of x^12 + 3x is 11x^11+3 [S1].\n2. Derivative of x^n is nx^{n-1} [S2]",
        "",
        "Student's new response."
        "Student : It should be 12x^11 then"
    ])
    agent = Summariser("mistral")
    res = agent.generate(example)
    print(res)
