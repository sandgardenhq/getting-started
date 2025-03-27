import json
import random
import requests

def handler(input, sandgarden):
    # Initialize OpenAI connector
    openai = sandgarden.get_connector('trivia-openai')
    # Get the prompt
    prompt = sandgarden.get_prompt('answer-trivia')
   
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
        q = question['question_text']
        p = question['paragraph_text']
        res = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt.render(question=q, text=p)}
        ])
        answers.append({"question": question, "answer": res.choices[0].message.content})
        
    return {"answers": answers}