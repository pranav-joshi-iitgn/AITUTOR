## Dialog Structure

The dialog structures that AutoTutor tries to mimic are
- Curriculum script : Didactic content and problems on the content. This is set before the conversation even start. Just to be clear, AutoTutor is a lecturer, not an assistant. The content to teach is already set by an instructor, not infered from questions that the students ask. We can of-course change this with RAG. 
- 5-step tutoring frame :
    1. Present the main question
    2. Student gives initial answer
    3. Give short feedback on answer
    4. Student tries to correct his answer
    5. If answer still not satisfactory, go back to step 3. If satisfacory, evaluate student's understanding and ask if he understands the main concepts (with reference to the convo.)
- Expectation and Misconception Tailored (EMT) dialog : The tutor guides the student in articulating (and potentially constructing) the knowledge concepts that needs to be learnt/payed attention to so that the main question may be solved. For this we use these dialog moves: 
    - pumps ("What else") : No info, no pointing (minimal feedback)
    - hints ("What about X") : Directing (pointing) attention
    - prompts ("X is a type of what?") : Prompting to extract a particular fact or relationship.
    - assertions ("X is a type of Y") : Just stating the fact in abstract (teaching hint).
    - asnwers ("since X is a type of Y..") : Connecting to the main question (reasoning hint).
- Conversational turn management : Every turn of any tutor (humans too) has 3 slots
    - Feedback ("very good", "not quite", etc.)
    - Dialogue Move (prompt, assertion, etc.)
    - Cue for the student to start talking ("you try it now", "want to give it a try?")

## Student Model

The Expectations (KCs to cover) and Misconceptions (known incorrect KCs that might occur) are manually input into the system. All that happens is that the student's responses are matched to known Expectations $E_i$ and Misconceptions $M_i$ using a very primitive NLP technique called LSA. Any time the similarity of the articulation and any expection is above a threshold it's considered to be covered.

The next expectation to cover is the one that matches the most with articulations done so far by the student, but isn't covered yet.

Deep Tutor is a modification of Auto-Tutor that uses DL and recursive planning and multi-goal agendas.

## Affective Auto-Tutor

Here, they are also monitoring the emotional state of the student. This happens via physiological changes and changes in expression of the student, as well as changes in the manner that the student is speaking.

While this is personally interesting, it's not relevant to the project. So I won't do this.