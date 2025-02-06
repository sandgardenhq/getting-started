#!/bin/bash
set -e  # Exit on any error

# Determine whether this is linux or macos
if [ "$(uname)" == "Darwin" ]; then
    OS="osx"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    OS="linux"
else
    echo "Unsupported OS"
    exit 1
fi

# Determine whether this is arm64 or x86_64
if [ "$(uname -m)" == "arm64" ]; then
    ARCH="arm64"
elif [ "$(uname -m)" == "x86_64" ]; then
    ARCH="amd64"
else
    echo "Unsupported architecture"
    exit 1
fi

# Check that curl is installed
if ! command -v curl &> /dev/null; then
    echo "Curl is not installed. Please install Curl before running this script."
    exit 1
fi

# Check that go is installed
if ! command -v go &> /dev/null; then
    echo "Go is not installed. Please install Go before running this script."
    exit 1
fi

# Create .sandgarden/bin directory if it doesn't exist
mkdir -p .sandgarden/bin

echo "Downloading Sandgarden Director..."
if ! OUTPUT=$(curl -fsSL "https://api.sandgarden.com/api/v1/assets/sgdirector/latest/sgdirector_${OS}_${ARCH}" -o ./.sandgarden/bin/sgdirector 2>&1); then
    echo "❌ Failed to download Director binary:"
    echo "$OUTPUT"
    exit 1
fi

chmod +x .sandgarden/bin/sgdirector

# Install dependencies
echo "Installing dependencies..."
go install cirello.io/runner@latest

# Ask for the SAND_API_KEY
echo "Please enter your SAND_API_KEY:"
read -s SAND_API_KEY

# Create the .env file
echo "Creating .env file..."
echo "SAND_API_KEY=$SAND_API_KEY" > ./.sandgarden/.env
echo "SAND_HOME=./.sandgarden" >> ./.sandgarden/.env
echo '{"restarted": true}' > ./.sandgarden/staticcfg.json

echo "Setup complete. You can start the director with the following command:"
echo "runner --env ./.sandgarden/.env"
