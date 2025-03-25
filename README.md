# Getting Started with Sandgarden

Sandgarden is a platform to prototype, iterate, and deploy AI applications. It eliminates the overhead of:

## Project Structure

This repository is organized to help you get started with Sandgarden workflows:

- `.devcontainer/` - Contains development environment configuration for consistent setup
- `examples/` - Sample code and reference implementations
  - `workflows/` - Example Sandgarden workflows with complete functionality
    - Each workflow follows the standard structure with `steps/`, `prompts/`, and `workflow.json`
  - `syncing-with-github/` - Guide for syncing workflows with GitHub
  - `triggering-workflow-from-github-actions/` - Examples of GitHub Actions integration
- `director-setup/` - Tools for setting up Sandgarden Director (workflow orchestration)

When creating your own workflows, follow the standard structure:
```
workflows/
└── my-workflow/               # Your workflow folder
    ├── workflow.json          # Workflow configuration
    ├── README.md              # Documentation
    ├── prompts/               # Prompt templates
    └── steps/                 # Executable steps
        ├── 001-first-step/    # Step with sequential numbering
        │   ├── main.py        # Handler function
        │   ├── requirements.txt
        │   ├── input.json     # Optional schema
        │   └── output.json    # Optional schema
        └── 002-second-step/
            └── ...
```

## Development Environment Setup

The fastest to get started is to use the devcontainer configuration included in this project. This repository includes a devcontainer configuration for a consistent development environment. The devcontainer provides:

- Python 3.12.5
- Sandgarden CLI pre-installed
- Docker support for local testing
- AWS CLI and other development tools
- All necessary VS Code extensions

### Prerequisites

- [Cursor](https://www.cursor.com/) or [VS Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or something similar like [OrbStack](https://orbstack.dev/)
- [VS Code Remote Development extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

### Getting Started with the Devcontainer

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/getting-started.git
   cd getting-started
   ```

2. Create a `.env` file in the `.devcontainer` directory:
   ```bash
   cp .devcontainer/.env.example .devcontainer/.env
   ```

3. Edit the `.env` file and add your Sandgarden API key:
   ```
   SAND_API_KEY=your_sandgarden_api_key
   SSH_AUTH_SOCK_PATH=/run/host-services/ssh-auth.sock
   GIT_USER_NAME="Your Name"
   GIT_USER_EMAIL="Your Email Address"
   ```

4. Open the project in Cursor:
   ```bash
   cursor .
   ```

5. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container"

6. The container will build and start, installing all the necessary dependencies. The setup script will automatically download and configure the Sandgarden CLI.

7. Once the container is running, you're ready to develop and deploy Sandgarden workflows!

## Updates

* [ ] Rewrite this README
* [x] Add Cursor rules
* [x] Restructure directories
    * [x] Remove devcontainer duplication
    * [x] Remove aws/vpc
* [ ] Improve local exec guides
    * [ ] Explain local steps
* [ ] Update workflow for new SDK
* [ ] Switch guides to steps/functions first
* [x] Add Github actions
    * [x] triggering
    * [x] workflow syncing
* [ ] Add more workflows
    * [ ] Summary of the last time I talked to someone (email, notes)
    * [ ] AWS access review based on title and org chart
* [ ] Add guides
    * [ ] Creating a Workflow
    * [ ] Deploying a Workflow
* [ ] Devcontainer improvements
    * [x] Host SSH
    * [x] extensions

