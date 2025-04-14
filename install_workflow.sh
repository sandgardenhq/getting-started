#!/bin/bash

# Parse command line arguments
FORCE=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --force) FORCE=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Check if we're in the root of the getting-started repo
if [[ "$FORCE" == false && ($(basename "$PWD") != "getting-started" || $(basename "$PWD") != "sandgarden") ]]; then
    echo "Error: This script must be run from the root of the getting-started repo"
    echo "If you cloned the repo into a different directory, use --force to bypass this check"
    exit 1
fi

# Check if sand CLI is installed
if ! command -v sand &> /dev/null; then
    echo "sand CLI not found. Installing..."
    if [ -f "install_cli.sh" ]; then
        bash install_cli.sh
    else
        echo "Error: install_cli.sh not found"
        exit 1
    fi
fi

# Get Sandgarden API Key
if [ -z "$SAND_API_KEY" ]; then
    echo "Please visit https://app.sandgarden.com/settings/api-keys to create an API key."
    echo "Click 'Create API Key' and make sure to select director access."
    read -p "Enter your API key: " SAND_API_KEY
fi

# Create a cluster
if ! sand clusters create --name getting-started --tag getting-started 2>&1 | grep -q "Error: remote operation failed: failed to create cluster: conflict: ERROR: duplicate key value violates unique constraint"; then
    echo "Cluster created successfully"
else
    echo "Cluster 'getting-started' already exists"
fi

# Prompt for OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    read -p "Enter your OpenAI API key: " OPENAI_API_KEY
fi

# Create an OpenAI connector
sand connectors create openai --name="trivia-openai" --api-key="${OPENAI_API_KEY}"

# Create the prompts
sand prompts create --name answer-trivia --content=${HOST_PATH:-$PWD}/workflow/steps/001_answer_some_questions/prompts/answer-trivia.txt

# Create the first step
sand steps create local --name=answer-some-questions --volumeMountPath ${HOST_PATH:-$PWD}/workflow/steps/001_answer_some_questions --connector trivia-openai --tag=latest --prompt answer-trivia:1 --cluster getting-started

# Create the second step
sand prompts create --name judge-system-prompt --content=${HOST_PATH:-$PWD}/workflow/steps/002_check_your_work/prompts/judge-system-prompt.txt
sand prompts create --name check-answers --content=${HOST_PATH:-$PWD}/workflow/steps/002_check_your_work/prompts/check-answers.txt
sand steps create local --name=check-your-work --volumeMountPath ${HOST_PATH:-$PWD}/workflow/steps/002_check_your_work --connector trivia-openai --prompt check-answers:1 --prompt judge-system-prompt:1 --tag latest  --cluster getting-started

# Create the workflow
sand workflows create --name trivia --description "An example workflow using GPT-4o-mini to answer questions from the CF-TriviaQA Dataset" --stages='[{"step":"answer-some-questions:latest"},{"step":"check-your-work:latest"}]'  --tag latest --cluster getting-started

echo "✅ Workflow successfully pushed to Sandgarden!"

