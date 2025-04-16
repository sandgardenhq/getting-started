# Local Developer Mode - Dev Container

Local developer mode runs a Sandgarden director in a local docker image on your development machine.
It's a simple way to get started with Sandgarden without having to set up a cloud environment, and it lets you test your changes as you make them.

## Prerequisites

To get started in local developer mode, first prepare the following:

1. Clone [this getting-started repo](https://github.com/sandgardenhq/getting-started.git), through either Git or VS Code.
2. Create a Sandgarden API Key [through the Admin UI](https://app.sandgarden.com/settings/api-keys/new).
   - Give a descriptive API Key Name (e.g. `deployment-key`).
   - For Key Type, select "Director Key".
   - For Expiration Date, choose a date conveniently far enough into the future (e.g. 30 days out).
3. _(Optional)_ Create an OpenAI API Key and keep it handy, if you would like to try one of our provided example workflows after deploying a Director.

## Dev Container

Dev Container provides a complete development environment for Sandgarden workflows:

- VS Code configured with Python tooling
- Sandgarden Director running as a sidecar service
- Your code is mounted in the container as `/workspaces/sandgarden`

### Setup

1. Open the .devcontainer directory from the `getting-started` repo in VS Code, then make a copy of the `.env.example` file in the same directory and rename the copy as `.env`. You can also execute this command in your terminal:
   ```bash
   cp .devcontainer/.env.example .devcontainer/.env
   ```

2. Edit the `.env` and replace the `YOUR_SAND_API_KEY` string with your actual Sandgarden Director API key.

3. Click the "Open a Remote Window" button in the bottom-left corner and select "Reopen in Container" from the menu.
   - This will start building the Dev Container, the first time you do it may take a few minutes to fully download build. Click “show log” in VSCode to check progress and as long as stuff is happening, it's all good.

4. When the Dev Container finishes building, open another VS Code terminal and run `sand directors list` to confirm everything was successful - you should see an active Director listed. You should also see an active Director in the [Sandgarden Admin UI](https://app.sandgarden.com/infrastructure/directors).
   ```bash
   sand directors list
   ```

If a Director is active then your workspace will be mounted and ready for workflow development. 

Go to [the workflow directory](https://github.com/sandgardenhq/getting-started/workflow/README.md) in the `getting-started` repo and follow the ReadMe instructions there to try one of our pre-built workflows, or get started building your own project :)
