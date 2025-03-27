from pydantic import BaseModel

class Judgment(BaseModel):
    question_id: str
    correct: bool
    explanation: str

def handler(input, sandgarden):
    # Initialize the OpenAI connectors
    openai = sandgarden.get_connector('trivia-openai')
    system_prompt = sandgarden.get_prompt('judge-system-prompt')
    judgements = []
    for response in input['answers']:
        id = response['question']['question_id']
        question = response['question']['question_text']
        reference_text = response['question']['paragraph_text']
        answer = response['question']['annotation']['answer'][0]['paragraph_reference']['string']
        given_answer = response['answer']
        
        rag = {
            "id":id, 
            "question":question, 
            "reference_text":reference_text, 
            "answer":answer, 
            "given_answer":given_answer
        }
        
        prompt = sandgarden.render_prompt('check-answers', rag)   
        res = openai.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format=Judgment
        )     
        judgment = res.choices[0].message.parsed.dict()
        judgements.append(judgment)

    return { "judgments": judgements }