# Local Developer Mode - Docker Compose

Local developer mode runs a Sandgarden director in a local docker image on your development machine.
It's a simple way to get started with Sandgarden without having to set up a cloud environment, and it lets you test your changes as you make them.

## Docker Compose

This is very similar to the Dev Container mode and will start a Sandgarden Director in a local docker container with a complete development environment for Sandgarden workflows.

### Setup

1. From the root directory of the `getting-started` repo, start the docker container:
   ```bash
   docker compose -f docker_compose/docker-compose.yml --env-file .env up --detach
   ```

2. From the root directory of the `getting-started` repo, run the script to install the Sandgarden CLI:
   ```bash
   source ./install_cli.sh
   ```

3. Run `sand directors list` to confirm everything was successful - you should see an active Director listed. You should also see an active Director in the [Sandgarden Admin UI](https://app.sandgarden.com/infrastructure/directors).
   ```bash
   sand directors list
   ```

If a Director is active, and the Sandgarden CLI is functioning, then your workspace is ready for workflow development. 

Go to [the workflow directory](https://github.com/sandgardenhq/getting-started/workflow/README.md) in the `getting-started` repo and follow the ReadMe instructions there to try one of our pre-built workflows, or get started building your own project :)
