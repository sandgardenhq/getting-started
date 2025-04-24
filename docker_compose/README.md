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
   - If a Director is active then your workspace will be mounted and ready for workflow development. 

4. Run our 'Hello World' script, which will build a simple function generating a haiku using OpenAI :)
   ```bash
   source ./install_workflow.sh
   ```

If you'd like to try a more complex workflow example, go to [the workflow directory](https://github.com/sandgardenhq/getting-started/workflow/README.md) in the `getting-started` repo and follow the ReadMe instructions there. Or just start building your own project :)