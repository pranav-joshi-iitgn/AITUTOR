from client import get_llm_response

SYSTEM_START_TOKEN = {
    "qwen3":"<|im_start|>system\n",
    "gpt-oss":"<|im_start|>system\n",
    "mistral":"<s>[INST] <<SYS>>\n",
}
SYSTEM_END_TOKEN = {
    "qwen3":"<|im_end|>",
    "gpt-oss":"<|im_end|>",
    "mistral":"<</SYS>>\n"
}
ASSISTANT_START_TOKEN = {
    "qwen3":"<|im_start|>assistant\n",
    "gpt-oss":"<|im_start|>assistant\n",
    "mistral":""
}
ASSISTANT_END_TOKEN = {
    "qwen3":"<|im_end|>",
    "gpt-oss":"<|im_end|>",
    "mistral":"</s>"
}
USER_START_TOKEN = {
    "qwen3":"<|im_start|>user\n",
    "gpt-oss":"<|im_start|>user\n",
    "mistral":"<s>[INST]"
}
USER_END_TOKEN = {
    "qwen3":"<|im_end|>",
    "gpt-oss":"<|im_end|>",
    "mistral":"[/INST]"
}


class Agent:
    def __init__(self,model,system_prompt):
        self.model = model
        if system_prompt.startswith("file:"):
            f = system_prompt.split(':',1)[1]
            f = open(f,'r')
            system_prompt = f.read()
            f.close()
        self.sysprompt = system_prompt
        self.convo = []
    def speak(self):
        m = self.model.split(":")[0]
        convo = "\n".join(self.convo)
        sysprompt = SYSTEM_START_TOKEN[m] + self.sysprompt + SYSTEM_END_TOKEN[m]
        prompt = sysprompt + "\n" + convo + "\n" + ASSISTANT_START_TOKEN[m]

        res = get_llm_response(prompt,self.model)
        if isinstance(res,ConnectionError): raise res
        else: 
            self.convo.append(ASSISTANT_START_TOKEN[m] + res + ASSISTANT_END_TOKEN[m])
            return res
    def hear(self,messages):
        m = self.model.split(":")[0]
        if isinstance(messages,list): self.convo.extend(messages)
        elif m == "mistral" and len(self.convo)==0:
            self.convo.append(messages+USER_END_TOKEN[m])
        else:
            self.convo.append(USER_START_TOKEN[m] + messages + USER_END_TOKEN[m])
    def generate(self,prompt,sysprompt=None):
        """Memory-less prompting"""
        m = self.model.split(":")[0]
        if sysprompt is None: sysprompt = self.sysprompt
        sysprompt = SYSTEM_START_TOKEN[m] + sysprompt + SYSTEM_END_TOKEN[m]
        if m == "mistral":
            userprompt =  prompt + USER_END_TOKEN[m]            
        userprompt = USER_START_TOKEN[m] + prompt + USER_END_TOKEN[m]
        fullprompt = sysprompt + "\n" + userprompt + "\n" + ASSISTANT_START_TOKEN[m]
        res = get_llm_response(fullprompt,self.model)
        if isinstance(res,ConnectionError): raise res
        else: return res

class SummConvoAgent(Agent):
    def __init__(self,system_prompt,model="gpt-oss"):
        super().__init__(model,system_prompt)
        self.turn = 0
        self.Summ = ""
    def format_convo_summ(self,convo=None,Summ=None):
        if convo is not None:
            self.turn = 0
            for msg in convo: 
                if not msg.strip():continue
                self.add_convo_message(msg.strip())
        if Summ is not None: self.Summ = Summ
        prompt = ""
        if self.convo: prompt += "\nConversation:\n" + "\n".join(self.convo)
        if self.Summ: prompt += "\n\nSummary:\n" + self.Summ
        return prompt
    def add_convo_message(self,msg:str):
        role, msg = msg.split(":",1)
        role = role.strip().lower().capitalize()
        if role == "Tutor":self.turn += 1
        assert role in ["Tutor","Student"], f"unknown role {role}"
        self.convo.append(f"{self.turn}: {role} : {msg.strip()}")

if __name__ == "__main__":
    sysprompt = "You are a very sarcastic and rude person."
    model = "gpt-oss"
    rude_guy = Agent(model,sysprompt)
    while True:
        your_message = input("> ")
        rude_guy.hear(your_message)
        his_message = rude_guy.speak()
        print(his_message)