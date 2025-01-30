import sandgarden_runtime
from .schema import HandlerResponse, Judgment

system_prompt = """You are an evaluator tasked with determining whether an answer matches the information provided in a reference text. Your job is to check if the answer aligns with what the text states, regardless of whether the text contains accurate real-world information.

Important rules:
1. Only consider the information provided in the reference text
2. Ignore any real-world knowledge or facts
3. Do not fact-check the text itself
4. Focus solely on whether the answer reflects what the text claims

For each evaluation, you will receive:
- A question
- A reference text
- The answer given

Please evaluate whether the answer correctly represents what is stated in the text. 
If the answer accurately reflects the information in the text then correct should be true, 
if the answer contradicts or does not match the information in the text then correct should be false.

The explanation should be a string that explains why the answer is correct or incorrect citing specific evidence from the text.
id should be the id of the question you were given.
"""



def handler(input: HandlerResponse, sandgarden, runtime_context):
    # Initialize the OpenAI connectors
    sandgarden_runtime.initialize_connectors(['trivia-openai'], sandgarden)
    openai = sandgarden.connectors['trivia-openai']
    
    judgements = []
    for response in input['answers']:
        id = response['question']['question_id']
        question = response['question']['question_text']
        reference_text = response['question']['paragraph_text']
        answer = response['question']['annotation']['paragraph_reference']['string']
        given_answer = response['answer']
        judgment = evaluate_answer(openai, id, question, reference_text, answer, given_answer)
        judgements.append(judgment)

    return judgements

def evaluate_answer(openai, id, question, reference_text, answer, given_answer):
    prompt = f"""
ID: {id}
Question: {question}
Reference Text: {reference_text}
Answer: {given_answer}
Given Answer: {answer}
"""
        
    return openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        response_format=Judgment
    )        