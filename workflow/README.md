# Sandgarden Example Workflow

This is an example workflow that loads the CF-TriviaQA dataset and answers some questions based on it. Then is checks the answers using an LLM-as-Judge pattern. In this example we use GPT-4o-mini to check the itself. The example steps completely go through creation of a cluster, connector, steps, and workflow all in Sandgarden.

### Prerequisites

* The steps below assume that you have a local director running either in a Dev Container, or are using docker-compose.
* All of the bash commands assume you are starting from the root directory of this `getting-started` repo.

## Directions - The Easy Way

### 1. Run install_workflow.sh
```bash
./install_workflow.sh
```

### 2. Run it!
```bash
sand runs start --workflow=trivia:latest --cluster getting-started
```

## Directions - Do It Yourself

Basically this is all the stuff scripted in `install_workflow.sh`.

## 1. Create a cluster
A cluster is [a logical grouping of Directors](https://privatedocs.sandgarden.com/docs/using/concepts) that will run the workflow.

```bash
sand clusters create --name getting-started --tag getting-started
```

## 2. Create an OpenAI connector

```bash
sand connectors create openai --name="trivia-openai" --api-key="FILL_IN"
```

## 3. Create the first step - answer some questions
Here you will create a prompt and turn it into a step.

```bash
sand prompts create --name answer-trivia --content=${HOST_PATH:-$PWD}/workflow/steps/001_answer_some_questions/prompts/answer-trivia.txt
sand steps create local --name=answer-some-questions --volumeMountPath ${HOST_PATH:-$PWD}/workflow/steps/001_answer_some_questions --connector trivia-openai --tag=latest --prompt answer-trivia:1 --cluster getting-started
```

## 4. Create the second step - check the answers
Here you create some additional prompts and a step using them.

```bash
sand prompts create --name judge-system-prompt --content=${HOST_PATH:-$PWD}/workflow/steps/002_check_your_work/prompts/judge-system-prompt.txt
sand prompts create --name check-answers --content=${HOST_PATH:-$PWD}/workflow/steps/002_check_your_work/prompts/check-answers.txt
sand steps create local --name=check-your-work --volumeMountPath ${HOST_PATH:-$PWD}/workflow/steps/002_check_your_work --connector trivia-openai --prompt check-answers --prompt judge-system-prompt --tag latest  --cluster getting-started
```

## 5. Create the workflow
Now create a workflow that combines the previously created steps.

```bash
sand workflows create --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"answer-some-questions:latest"},{"step":"check-your-work:latest"}]'  --tag latest --cluster getting-started
```

## 6. Run it!

```bash
sand runs start --workflow=trivia:latest --cluster getting-started
```

### What's all that `${HOST_PATH:-$PWD}` stuff?

The instructions were written so that they could work either in a Dev Container, or running on the host machine (if you were using docker-compose for example). The paths are a little different in those cases, so this is just a little bit of BASH trickery to make it so one command can serve both cases.
