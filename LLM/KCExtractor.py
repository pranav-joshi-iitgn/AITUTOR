from agent import Agent,SummConvoAgent
from sentence_transformers import SentenceTransformer

# Load a pre-trained model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class KC:
    """
    representation of a Knowledge Concept
    """
    def __init__(self,text):
        self.text = text
        self.embed()
    def embed(self):
        global embedding_model
        self.embedding = embedding_model.encode(self.text)
    def __hash__(self):return hash(self.text)
    def __eq__(self,other):
        return (self.text == other.text)
    def __repr__(self): return self.text

class MC(KC):
    """
    A kind of knowledge concept that is not good to have. 

    In addition to other attributes of a KC, it also has a list of KC learning which can remedy the MC, in decreasing priority.

    This can be used for self-contradiction, for example.
    """
    remedies:list

class KCExtractor(Agent):
    def __init__(self,model="gpt-oss",system_prompt='file:KCExtractor.txt',KCList =[]):
        super().__init__(model,system_prompt)
        # self.KCList = [KC(x) for x in [
        #     "power rule of differentiation, i.e. d/dx (x^n) = n x^{n-1}",
        #     "distributive property of differentiation over addition",
        #     "derivative of constant is 0",
        #     "distributive property of multiplication over addition",
        #     "abelian groups have commutivity",
        # ]]
        self.KCList = KCList
        # print("KCs loaded")

    def extract_E_i(self,
        g:str,
        material:str,
        full_map:bool = True
        ) -> dict[KC,float]:
        """
        Given goal g and matrial, extracts pre-requisite KCs and mastery levels required.
        These KCs are set by the instructor.
        Returns a mapping from goal KCs to the mastery level required.
        The map can be full or shortened (via thresholding of mastery levels)
        """
        beta = {}
        for k in self.KCList:
            prompt = f"Material:\n{material}\nGoal:\n{g}\nKnowledge Concept:\n{k}"
            res = self.generate(prompt)
            beta[k] = float(res)
            # print(k,":",res)
        return beta


class Sequencer(SummConvoAgent):
    def __init__(self,model="gpt-oss",system_prompt='file:Sequencer.txt',
        system_prompt2="file:Sequencer2.txt",
        system_prompt3="file:Sequencer3.txt",
        system_prompt4="file:Sequencer4.txt"):
        if system_prompt2.startswith("file"):
            with open(system_prompt2.split(":",1)[1],'r') as f :
                system_prompt2 = f.read()
        if system_prompt3.startswith("file"):
            with open(system_prompt3.split(":",1)[1],'r') as f :
                system_prompt3 = f.read()
        if system_prompt4.startswith("file"):
            with open(system_prompt4.split(":",1)[1],'r') as f :
                system_prompt4 = f.read()
        super().__init__(system_prompt,model)
        self.sysprompt2 = system_prompt2
        self.sysprompt3 = system_prompt3
        self.sysprompt4 = system_prompt4

    def prerequisites(self,g,material=None,convo=None,Summ=None,S=None,SP=None,prereqs=None,stage=None) -> list:
        if material: prompt = "Solution:\n" + material + "\n\n\n"
        else: prompt = ""
        if convo is not None : prompt += self.format_convo_summ(convo,Summ) + "\n\n"
        if S: prompt += "Student's next message:\n" + S + "\n\n"
        prompt += "Final goal:\n" + g + "\n\n"
        og_prompt = prompt
        if SP : prompt += f"Student's plan:\n{SP}\n\n"
        if prereqs: prompt += "Old Sequence of Knowledge Components:\n" + "\n".join((str(x) for x in prereqs))

        if stage ==1 or stage is None:
            # Main generative step
            L = self.generate(prompt).strip().strip("\n").strip()
            if not L : return prereqs
            else: prereqs=[x.strip() for x in L.split('\n') if x.strip()]

        if stage ==2 or stage is None:
            # Reductive stage 1
            prompt = f"Final Goal:\n{g}\n\nOld sequence:\n" + '\n'.join(prereqs)
            L = self.generate(prompt,self.sysprompt2).strip().strip("\n").strip()
            if not L : return prereqs
            else: prereqs=[x.strip() for x in L.split('\n') if x.strip()]

        if stage ==3 or stage is None:
            # Reductive stage 2
            prompt = f"Final Goal:\n{g}\n\nOld sequence:\n" + '\n'.join(prereqs)
            L = self.generate(prompt,self.sysprompt3).strip().strip("\n").strip()
            if not L : return prereqs
            else: prereqs=[x.strip() for x in L.split('\n') if x.strip()]

        if stage ==4 or stage is None:
            # Reductive stage 3
            prompt = og_prompt + "Old sequence:\n" + "\n".join(prereqs)
            L = self.generate(prompt,self.sysprompt4).strip().strip("\n").strip()
            if not L : return prereqs
            else: prereqs=[x.strip() for x in L.split('\n') if x.strip()]

        return prereqs





if __name__ == "__main__":
    g = "Misconception: Student says derivative of \(x^12 + 3x\) is 11x^11 + 2 but also claims that derivative of x^n is nx^{n-1}"
    material = "No material."
    # res = KCExtractor().extract_E_i(g,material)
    # print(res)
    res = Sequencer().prerequisites(g,material)
    print(res)
