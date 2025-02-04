# Sandgarden Example Workflow

This is an example workflow that loads the CF-TriviaQA dataset and answers some questions based on it.
Then is checks the answers using an LLM-as-Judge pattern. In this example we use GPT-4o-mini to check the itself.

## 1. Create the workflow

```bash
sand workflows create --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"load-trivia-dataset:latest"}]'
```

## 2. Create the first step - load the dataset

```bash
cd steps/001_load_trivia_dataset
sand steps create docker --name=load-trivia-dataset --file=. --baseImage="python:3.12" --entrypoint="handler.handler" --tag=latest
```

## 3. Create the S3 connector

```bash
sand connectors create s3 --name="sandgarden-trivia-challenge" --access-key-id="FILL_IN" --secret-access-key="FILL_IN" --session-token="FILL_IN" --region="FILL_IN" 
```

### 3.1 Attach the S3 connector to the step

```bash
sand steps push docker --name=load-trivia-dataset --file=. --baseImage="python:3.12" --entrypoint="handler.handler" --connector sandgarden-trivia-challenge --tag=latest
```

## 4. Create an OpenAI connector

```bash
sand connectors create openai --name="trivia-openai" --api-key="FILL_IN"
```

## 5. Create Step 2 - answer some questions

```bash
cd steps/002_answer_some_questions
sand steps create  docker --name=answer-some-questions --file=. --baseImage="python:3.12" --entrypoint="handler.handler"  --connector sandgarden-trivia-challenge --connector trivia-openai --tag=latest --outputSchema "$(cat response_schema.json)"
```

### 5.1 Add the step to the workflow

```bash
sand workflows push --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"load-trivia-dataset:latest"},{"step":"answer-some-questions:latest"}]'
```

## 6. Create Step 3 - check the answers

```bash
cd steps/003_check_your_work
sand steps create docker --name=check-your-work --file=. --baseImage="python:3.12" --entrypoint="handler.handler" --connector trivia-openai --outputSchema "$(cat output_schema.json)" --tag latest --inputSchema "$(cat input_schema.json)"
```

## 7. Update the workflow

```bash
sand workflows push --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"load-trivia-dataset:latest"},{"step":"answer-some-questions:latest"},{"step":"check-your-work:latest"}]'
```
