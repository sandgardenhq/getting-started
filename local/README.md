# Local Developer Mode

Local developer mode runs a Sandgarden director in a local docker image on your development machine.
It's a simple way to get started with Sandgarden without having to set up a cloud environment, and
it lets you test your changes as you make them.

## Setup

To get started in local developer mode, first prepare the following:

1. Clone [this getting-started repo](https://github.com/sandgardenhq/getting-started.git), through either Git or VS Code.


There are four different ways to use local developer mode:

1. Dev Container - a VS Code dev container that automatically runs the director (also works in Cursor)
2. Github Codespaces - same as dev container, but remotely in Codespaces
3. Docker Compose - run the director locally in docker

## Dev Container

Dev Container provides a complete development environment for Sandgarden workflows:

- VS Code configured with Python tooling
- Sandgarden Director running as a sidecar service
- Your code is mounted in the container as `/workspaces/sandgarden`

### Setup

1. Copy the environment file and add your API key:
   ```bash
   cp .devcontainer/.env.example .devcontainer/.env
   ```

2. Edit `.env` and replace `YOUR_SAND_API_KEY` with your actual Sand API key

3. Open this directory in VS Code and click "Reopen in Container" when prompted

The Director service will be available at `http://localhost:8987` and visible in the [Sandgarden UI](https://app.sandgarden.com). Your workspace will be mounted and ready for workflow development.

## Docker Compose

This will start the Sandgarden Director in a local docker container. The Director service will be available at `http://localhost:8987` and should be visible in the [Sandgarden UI](https://app.sandgarden.com).

### Setup

1. Copy the environment file and add your API key:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and replace `YOUR_SAND_API_KEY` with your actual Sand API key

3. _(Optional)_ Edit `docker-compose.yml` to change the workspace mount path:
   ```yaml
   volumes:
     - /path/to/your/workspace:/workspaces/sandgarden
   ```

4. Start the environment:
   ```bash
   docker compose up
   ```


### Other Commands

#### Starting
```bash
    docker compose build sandgarden
    docker compose up -d
```

#### Connecting to the shell
```bash
    docker compose exec -it sandgarden /bin/bash
```

#### Show logs
```bash
    docker compose logs -f sandgarden
```

#### Stopping
```bash
    docker compose down
```
