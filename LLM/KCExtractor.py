from agent import Agent
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
    def __init__(self,model="gpt-oss",system_prompt='file:KCExtractor.txt'):
        super().__init__(model,system_prompt)
        self.KCList = [KC(x) for x in [
            "power rule of differentiation, i.e. d/dx (x^n) = n x^{n-1}",
            "distributive property of differentiation over addition",
            "derivative of constant is 0",
            "distributive property of multiplication over addition",
            "abelian groups have commutivity",
        ]]
        print("KCs loaded")

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
        global KCList
        beta = {}
        for k in KCList:
            prompt = f"Material:\n{material}\nGoal:\n{g}\nKnowledge Concept:\n{k}"
            res = self.generate(prompt)
            beta[k] = float(res)
            print(k,":",res)
        return beta

if __name__ == "__main__":
    g = "Misconception: Student says derivative of \(x^12 + 3x\) is 11x^11 + 2 but also claims that derivative of x^n is nx^{n-1}"
    material = "No material."
    agent = KCExtractor()
    res = agent.extract_E_i(g,material)
    print(res)
