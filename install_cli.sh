#!/bin/bash

# Function to safely exit or return
safe_exit() {
    if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
        # If sourced, use return
        return 1
    else
        # If executed directly, use exit
        exit 1
    fi
}

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | tr '[:upper:]' '[:lower:]')

# Map architecture to download URL format
case $ARCH in
    "arm64"|"aarch64")
        ARCH="arm64"
        ;;
    "x86_64")
        ARCH="amd64"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        safe_exit
        ;;
esac

#Map OS to download URL format
case $OS in
    "darwin")
        OS="osx"
        ;;
    "linux")
        OS="linux"
        ;;
    *)
        echo "Unsupported OS: $OS"
        safe_exit
        ;;
esac

# Construct download URL
URL="https://api.sandgarden.com/api/v1/assets/sand/latest/sand_${OS}_${ARCH}"

# Create temporary directory
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# Download binary
echo "Downloading Sandgarden CLI..."
curl -L "$URL" -o sand

# Make binary executable
chmod 0755 sand

# Find a suitable location in PATH
DEFAULT_DIR="$HOME/bin"

# Check if ~/bin exists, if not, create it
if [ ! -d "$DEFAULT_DIR" ]; then
    echo "Creating directory $DEFAULT_DIR"
    mkdir -p "$DEFAULT_DIR"
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo "Adding $DEFAULT_DIR to PATH in your shell profile"
        # Determine shell and update appropriate profile
        if [ -n "$BASH_VERSION" ]; then
            echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bashrc"
        elif [ -n "$ZSH_VERSION" ]; then
            echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
        else
            echo "Please add $DEFAULT_DIR to your PATH manually"
        fi
    fi
fi

# Double check the directory is writable
if [ ! -w "$DEFAULT_DIR" ]; then
    echo "WARNING: $DEFAULT_DIR is not writable. Trying /usr/local/bin instead."
    DEFAULT_DIR="/usr/local/bin"
    if [ ! -w "$DEFAULT_DIR" ]; then
        echo "ERROR: Neither $HOME/bin nor /usr/local/bin are writable."
        echo "Please specify a writable directory manually."
        DEFAULT_DIR=""
    fi
fi

# If we still don't have a default dir, check PATH directories
if [ -z "$DEFAULT_DIR" ]; then
    IFS=':' read -ra DIRS <<< "$PATH"
    for dir in "${DIRS[@]}"; do
        if [ -d "$dir" ] && [ -w "$dir" ]; then
            DEFAULT_DIR="$dir"
            break
        fi
    done
fi

# If still no writable directory found
if [ -z "$DEFAULT_DIR" ]; then
    echo "No writable directory found in PATH."
    echo "Will install to current directory."
    DEFAULT_DIR="$(pwd)"
fi

# Prompt for installation directory - handling different shells
echo "Enter installation directory [$DEFAULT_DIR]: "
read INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_DIR}

# Handle ~ expansion
INSTALL_DIR="${INSTALL_DIR/#\~/$HOME}"

# Create directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Directory $INSTALL_DIR does not exist. Creating it..."
    mkdir -p "$INSTALL_DIR" || {
        echo "Failed to create directory $INSTALL_DIR"
        safe_exit
    }
fi

# Verify directory is writable
if [ ! -w "$INSTALL_DIR" ]; then
    echo "Error: Directory $INSTALL_DIR is not writable"
    safe_exit
fi

# Move binary to installation directory
echo "Installing to $INSTALL_DIR..."
mv sand "$INSTALL_DIR/"

# Cleanup
cd "$OLDPWD" || cd "$HOME"
rm -rf "$TMP_DIR"

# Export the API Key from .env file and set it as an env var for CLI usage
if [ -f ".env" ]; then
    set -o allexport
    source .env
    set +o allexport
    echo "Loaded environment variables from .env file"
else
    echo "Warning: .env file not found. SAND_API_KEY not set."
fi

echo "Sandgarden CLI installed successfully to $INSTALL_DIR/sand"
echo "Make sure $INSTALL_DIR is in your PATH"

# Verify the API key is set
if [ -n "$SAND_API_KEY" ]; then
    echo "SAND_API_KEY is set"
else
    echo "SAND_API_KEY is not set. Please set it manually or create a .env file"
fi