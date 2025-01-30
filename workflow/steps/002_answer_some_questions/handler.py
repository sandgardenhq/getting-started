import sandgarden_runtime
import json
import random
from pydantic import BaseModel
from typing import List, Optional

class ParagraphReference(BaseModel):
    string: str

class AnswerAnnotation(BaseModel):
    paragraph_reference: ParagraphReference

class Question(BaseModel):
    question_text: str
    paragraph_text: str
    annotation: Optional[AnswerAnnotation]
    question_id: str

class Answer(BaseModel):
    question: Question
    answer: str

class HandlerResponse(BaseModel):
    answers: List[Answer]

def handler(input, sandgarden, runtime_context):
    bucket_name = "sandgarden-trivia-challenge"
    key = "har_dataset.jsonl"
    
    # Initialize S3 module
    sandgarden_runtime.initialize_modules(['sandgarden-trivia-challenge', 'trivia-openai'], sandgarden)
    s3 = sandgarden.modules['sandgarden-trivia-challenge']['s3']
    openai = sandgarden.modules['tickets-openai']
    
    # Load the file from S3
    response = s3.get_object(Bucket=bucket_name, Key=key)
    dataset = response['Body'].read().decode('utf-8')
    
    # Parse the JSONL
    questions = [Question(**json.loads(line)) for line in dataset.splitlines()]
    
    # Choose twenty questions at random
    to_answer = random.sample(questions, 20)
    
    # Generate answers
    answers = []
    for question in to_answer:
        answer = answer_question(openai, prompt(question))
        answers.append(Answer(question=question, answer=answer))
        
    return HandlerResponse(answers=answers).dict()

def prompt(question):
    q = question.question_text
    p = question.paragraph_text
    return f"Do your best to answer the following question: {q}\n\nThe answer is contained in the following text: {p}\n\nOnly answer based on the information in the text."
    
def answer_question(openai, context):
    res = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": context}
        ])
    
    return res.choices[0].message.content

