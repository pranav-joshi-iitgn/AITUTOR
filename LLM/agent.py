from client import get_llm_response

class Agent:
    def __init__(self,model,system_prompt):
        self.model = model
        self.sysprompt = system_prompt
        self.convo = []
    def speak(self):
        convo = "\n".join(self.convo)
        sysprompt = "<|im_start|>system\n" + self.sysprompt + "<|im_end|>"
        prompt = sysprompt + "\n" + convo + "\n<|im_start|>assistant"
        res = get_llm_response(prompt,self.model)
        if isinstance(res,ConnectionError): raise res
        else: 
            self.convo.append("<|im_start|>assistant\n" + res + "<|im_end|>")
            return res
    def hear(self,messages):
        if isinstance(messages,list): self.convo.extend(messages)
        else: self.convo.append("<|im_start|>user\n" + messages+"<|im_end|>")

if __name__ == "__main__":
    sysprompt = "You are a very sarcastic and rude person."
    model = "qwen3"
    rude_guy = Agent(model,sysprompt)
    while True:
        your_message = input("> ")
        rude_guy.hear(your_message)
        his_message = rude_guy.speak()
        print(his_message)