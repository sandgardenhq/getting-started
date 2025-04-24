#!/bin/bash

safe_exit() {
    if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
        # If sourced, use return
        return 1
    else
        # If executed directly, use exit
        exit 1
    fi
}

# Check if sand CLI is installed
if ! command -v sand &> /dev/null; then
    echo "sand CLI not found. Installing..."
    if [ -f "install_cli.sh" ]; then
        bash install_cli.sh
    else
        echo "Error: install_cli.sh not found"
        safe_exit
    fi
fi

# Export the API Key from .env file and set it as an env var for CLI usage
set -o allexport; source .env; set +o allexport


# Get Sandgarden API Key
if [ -z "$SAND_API_KEY" ]; then
    echo "Please visit https://app.sandgarden.com/settings/api-keys to create an API key."
    echo "Click 'Create API Key' and make sure to select director access."
    echo "Enter your API key: "
    read SAND_API_KEY
fi

# Create a cluster
if ! sand clusters create --name getting-started --tag getting-started 2>&1 | grep -q "Error: remote operation failed: failed to create cluster: conflict: ERROR: duplicate key value violates unique constraint"; then
    echo "Cluster created successfully"
else
    echo "Cluster 'getting-started' already exists"
fi

# Prompt for OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Enter your OpenAI API key: "
    read OPENAI_API_KEY
fi

# Create an OpenAI connector
sand connectors create openai --name="haiku-openai" --api-key="${OPENAI_API_KEY}"

# Create the prompt
sand prompts create --name hello-world-haiku --content=${HOST_PATH:-$PWD}/function/001_hello_world_haiku/prompts/hello_world_haiku.txt

# Create the function
sand steps create local --name=hello-world-haiku --volumeMountPath ${HOST_PATH:-$PWD}/function/001_hello_world_haiku --connector haiku-openai --tag=latest --prompt hello-world-haiku:1 --cluster getting-started

echo
echo

# Run the function
curl -sS -X POST -d "{}" -H "Authorization: Bearer $SAND_API_KEY" https://api.sandgarden.com/api/v1/runs/hello-world-haiku:latest | jq -r '.output.haiku'

#echo "✅ Workflow successfully pushed to Sandgarden!"

