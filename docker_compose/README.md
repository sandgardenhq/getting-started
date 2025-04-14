# Local Developer Mode - Docker Compose

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


## Docker Compose

This is very similar to the Dev Container mode and will start a Sandgarden Director in a local docker container with a complete development environment for Sandgarden workflows.

### Setup

1. Make a copy of the `docker_compose/.env.example` file, keeping it in the same directory, and rename the copy as `.env`. You can also execute this command in your terminal:
   ```bash
   cp docker_compose/.env.example docker_compose/.env
   ```

2. Edit the `.env` and replace the `YOUR_SAND_API_KEY` string with your actual Sandgarden Director API key.

3. From the root directory of the `getting-started` repo, start the docker container:
   ```bash
   docker compose -f docker_compose/docker-compose.yml up --detach
   ```

4. From the root directory of the `getting-started` repo, run the script to install the Sandgarden CLI:
   ```bash
   ./install_cli.sh
   ```

5. Run `sand directors list` to confirm everything was successful - you should see an active Director listed. You should also see an active Director in the [Sandgarden Admin UI](https://app.sandgarden.com/infrastructure/directors).
   ```bash
   sand directors list
   ```

If a Director is active, and the Sandgarden CLI is functioning, then your workspace is ready for workflow development. Go to [the workflow directory](https://github.com/sandgardenhq/getting-started/workflow/README.md) in the `getting-started` repo and follow the ReadMe instructions there to try one of our pre-built workflows, or get started building your own project :)
