# Sandgarden Example Workflow

This is an example workflow that loads the CF-TriviaQA dataset and answers some questions based on it.
Then is checks the answers using an LLM-as-Judge pattern. In this example we use GPT-4o-mini to check the itself.

## 1. Create the workflow

```bash
# OLD
sand workflows create --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"answer-some-questions:latest"}]'

# NEW
sand workflows create trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset"

# This not only creates the workflow definition, but also creates a new directory with the name of the workflow.
# ./trivia/
# ./trivia/workflow.json
# ./trivia/input_schema.json
# ./trivia/output_schema.json
# ./trivia/steps/
# ./trivia/prompts/
```

## 2. Create an OpenAI connector

```bash
# OLD
sand connectors create openai --name="trivia-openai" --api-key="FILL_IN"

# NEW
sand connectors create --type openai trivia-openai 
enter your API key: *******

# Honestly, this one is actually decent as is. 
```

## 3. Create the step - answer some questions

```bash
# OLD
cd /workspaces/sandgarden/workflow/steps/001_answer_some_questions && sand steps create docker --name=answer-some-questions --file=. --baseImage="python:3.12" --entrypoint="handler.handler" --connector trivia-openai --tag=latest --outputSchema "$(cat response_schema.json)" --cluster $(jq -r .cluster /workspaces/sandgarden/.devcontainer/.sandgarden/staticcfg.json)

# NEW
cd trivia
sand steps add answer-some-questions --connector trivia-openai
# TODO: add templates as a flag `--template openai@latest
# TODO: interactive question asking mode

# This will create a new directory with the name of the step and its sequence number.
# ./trivia/steps/001_answer_some_questions/
# ./trivia/steps/001_answer_some_questions/step.json
# ./trivia/steps/001_answer_some_questions/handler.py
# ./trivia/steps/001_answer_some_questions/input_schema.json
# ./trivia/steps/001_answer_some_questions/output_schema.json
# An alternative to the *_schema.json files would be to have specially named pydantic objects exported from the handler.py file.
```

## 4. Edit your step and test it 

There is no OLD and NEW in the example below because this step does not exist in 
the old workflow.

```bash
cd trivia/steps/001_answer_some_questions
# Edit the handler.py file to add your logic.
# ...
# To test the step, you can use the following command:
sand steps run --dev
# TODO: add `--watch` flag
```

### 5. Push the step

```bash
# OLD
cd /workspaces/sandgarden/workflow/steps/001_answer_some_questions && sand steps push docker --name=answer-some-questions --file=. --baseImage="python:3.12" --entrypoint="handler.handler" --connector trivia-openai --tag=latest --outputSchema "$(cat response_schema.json)" --cluster $(jq -r .cluster /workspaces/sandgarden/.devcontainer/.sandgarden/staticcfg.json)

# NEW
cd trivia/steps/001_answer_some_questions
sand steps push [path]
```

## 5. Create Step 3 - check the answers

```bash
# OLD
cd /workspaces/sandgarden/workflow/steps/002_check_your_work && sand steps create docker --name=check-your-work --file=. --baseImage="python:3.12" --entrypoint="handler.handler" --connector trivia-openai --outputSchema "$(cat output_schema.json)" --tag latest --inputSchema "$(cat input_schema.json)" --cluster $(jq -r .cluster /workspaces/sandgarden/.devcontainer/.sandgarden/staticcfg.json)

# NEW
cd trivia
sand steps add check-your-work
cd steps/002_check_your_work
# ...
sand steps add-connector trivia-openai
```

## 5. Update the workflow

```bash
# OLD
sand workflows push --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"answer-some-questions:latest"},{"step":"check-your-work:latest"}]'  --tag latest

# NEW
cd trivia
sand workflows push --tag latest
```

## 6. Run it!

```bash
# OLD
sand runs start --workflow=trivia:latest --cluster $(jq -r .cluster /workspaces/sandgarden/.devcontainer/.sandgarden/staticcfg.json)

# NEW
cd trivia
sand workflows run
# Dev mode
sand workflows run --dev
```

```bash
# TODO: add a sync command to sync a workflow and all its steps and configuration
```