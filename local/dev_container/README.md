# Dev Container Development Mode

This configuration provides a complete development environment for Sandgarden workflows:

- VS Code configured with Python tooling
- Sandgarden Director running as a sidecar service
- Your code is mounted in the container as `/workspaces/sandgarden`

## Setup

0. GO TO  `../../.devcontainer to see the config`

1. Copy the environment file and fill in your API key and git info:
   ```bash
   cp .devcontainer/.env.example .devcontainer/.env
   ```

2. Edit `.env`
   1. Replace `YOUR_SAND_API_KEY` with your actual Sand API key
   1. Replace `GIT_USER_NAME` with your user name for git
   1. Replace `GIT_USER_EMAIL` with your email address

3. Open this directory in Cursor or VS Code and click "Reopen in Container" when prompted (or use the control pane if not prompted)

The Director service will be available at `http://localhost:8987` and visible in the [Sandgarden UI](https://app.sandgarden.com). Your workspace will be mounted and ready for workflow development.
