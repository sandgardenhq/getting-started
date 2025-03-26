import json
import random
import requests

def handler(input, sandgarden):
    # Initialize OpenAI connector
    openai = sandgarden.get_connector('trivia-openai')
    
    # Load the dataset via HTTP
    url = "https://raw.githubusercontent.com/google-research-datasets/cf_triviaqa/refs/heads/main/har_dataset.jsonl"
    response = requests.get(url)
    dataset = response.text
    
    # Parse the JSONL
    questions = [json.loads(line) for line in dataset.splitlines()]
    
    # Choose twenty questions at random
    to_answer = random.sample(questions, 20)
    
    # Generate answers
    answers = []
    for question in to_answer:
        answer = answer_question(openai, prompt(question))
        answers.append({"question": question, "answer": answer})
        
    return {"answers": answers}

def prompt(question):
    q = question['question_text']
    p = question['paragraph_text']
    return f"Do your best to answer the following question: {q}\n\nThe answer is contained in the following text: {p}\n\nOnly answer based on the information in the text."
    
def answer_question(openai, context):
    res = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": context}
        ])
    
    return res.choices[0].message.content

