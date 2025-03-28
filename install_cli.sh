#!/bin/bash

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
        exit 1
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
DEFAULT_DIR=""

# Check preferred locations first
for dir in "/usr/local/bin" "$HOME/bin"; do
    if [ -w "$dir" ]; then
        DEFAULT_DIR="$dir"
        break
    fi
done

# Fall back to first writable directory in PATH if no preferred location is available
if [ -z "$DEFAULT_DIR" ]; then
    for dir in ${PATH//:/ }; do
        if [ -w "$dir" ]; then
            DEFAULT_DIR="$dir"
            break
        fi
    done
fi

if [ -z "$DEFAULT_DIR" ]; then
    echo "No writable directory found in PATH"
    exit 1
fi

# Prompt for installation directory
read -p "Enter installation directory [$DEFAULT_DIR]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_DIR}
INSTALL_DIR=$(echo "$INSTALL_DIR" | sed "s|~|$HOME|")
INSTALL_DIR=$(realpath "$INSTALL_DIR")

# Verify directory is writable
if [ ! -w "$INSTALL_DIR" ]; then
    echo "Error: Directory $INSTALL_DIR is not writable"
    exit 1
fi

# Move binary to installation directory
echo "Installing to $INSTALL_DIR..."
mv sand "$INSTALL_DIR"

# Cleanup
cd - > /dev/null
rm -rf "$TMP_DIR"

echo "Sandgarden CLI installed successfully!"
