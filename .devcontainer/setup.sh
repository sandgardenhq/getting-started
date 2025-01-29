#!/bin/sh

# Hi 👋
# You don't need to edit or run this script.
# It's just here to make sure the devcontainer is set up correctly.

echo "Setting up devcontainer"
echo "Downloading Sandgarden CLI..."
curl https://api.sandgarden.com/api/v1/assets/sand/latest/sand_linux_amd64 -L -o sand
sudo mv sand /usr/local/bin/sand
sudo chown vscode:vscode /usr/local/bin/sand
sudo chmod 0755 /usr/local/bin/sand
sudo chown -R vscode:vscode /workspaces/sandgarden
echo "Done"