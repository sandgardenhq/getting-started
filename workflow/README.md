# Sandgarden Example Workflow

This is an example workflow that loads the CF-TriviaQA dataset and answers some questions based on it. Then is checks the answers using an LLM-as-Judge pattern. In this example we use GPT-4o-mini to check the itself.

## Prerequisites

* The steps below assume that you have a local director running either in a Dev Container, or using docker-compose.
* All of the bash commands assume you are starting from the root directory of this repo.

### What's all that `${HOST_PATH:-$PWD}` stuff?

The instructions were written so that they could work either in a Dev Container, or running on the host machine (if you were using docker-compose for example). The paths are a little different in those cases, so this is just a little bit of BASH trickery to make it so one command can serve both cases.

## 1. Create the workflow

```bash
cd workflow
sand workflows create --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"answer-some-questions:latest"}] --cluster $(jq -r .cluster ../.devcontainer/.sandgarden/staticcfg.json)'
```

## 2. Create an OpenAI connector

```bash
sand connectors create openai --name="trivia-openai" --api-key="FILL_IN"
```

## 3. Create the step - answer some questions

```bash
sand steps create local --name=answer-some-questions --volumeMountPath ${HOST_PATH:-$PWD}/workflow/steps/001_answer_some_questions --connector trivia-openai --tag=latest --outputSchema "$(cat workflow/steps/001_answer_some_questions/response_schema.json)" --cluster $(jq -r .cluster ./.devcontainer/.sandgarden/staticcfg.json)
```

## 4. Create Step 3 - check the answers

```bash
sand steps create local --name=check-your-work --volumeMountPath ${HOST_PATH:-$PWD}/workflow/steps/002_check_your_work --connector trivia-openai --outputSchema "$(cat workflow/steps/002_check_your_work/output_schema.json)" --tag latest --inputSchema "$(cat workflow/steps/002_check_your_work/input_schema.json)" --cluster $(jq -r .cluster ./.devcontainer/.sandgarden/staticcfg.json)
```

## 5. Update the workflow

```bash
sand workflows push --sync --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"answer-some-questions:latest"},{"step":"check-your-work:latest"}]'  --tag latest --cluster $(jq -r .cluster ./.devcontainer/.sandgarden/staticcfg.json)
```

## 6. Run it!

```bash
sand runs start --workflow=trivia:latest --cluster $(jq -r .cluster ./.devcontainer/.sandgarden/staticcfg.json)
```