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
        rag = {
            "question":question['question_text'], 
            "text":question['paragraph_text']
        }
        res = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": sandgarden.render_prompt('answer-trivia',rag)}
        ])
        answers.append({"question": question, "answer": res.choices[0].message.content})
        
    return {"answers": answers}