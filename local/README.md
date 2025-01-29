# Local Developer Mode

Local developer mode runs a Sandgarden director in a local docker image on your development machine.
It's a simple way to get started with Sandgarden without having to set up a cloud environment, and
it lets you test your changes as you make them.

There are four different ways to use local developer mode:

1. Dev Container - a VS Code dev container that automatically runs the director _(WARNING: this does not work with Cursor)_
2. Github Codespaces - same as dev container, but remotely in Codespaces
3. Vanilla Binary - starts the director with in a local process
4. Docker Compose - run the director locally in docker

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

## Github Codespaces

Same as dev container, but run remotely in Codespaces:

- VS Code configured with Python tooling
- Sandgarden Director running as a sidecar service
- Your code is mounted in the container as `/workspaces/sandgarden`

### Setup

0. Copy the `.devcontainer/` directory into the root of your repository
   ```bash
   cp -r .devcontainer/ /path/to/your/repo
   ```

1. Create a new Codespace

2. Start the Codespace

3. In the Codespace, copy the environment file and add your API key:
   ```bash
   cp .devcontainer/.env.example .devcontainer/.env
   ```

4. Edit `.env` and replace `YOUR_SAND_API_KEY` with your actual Sand API key

5. Rebuild the container

## Vanilla Binary

This is the simplest way to run the director locally. It's a single binary that you can run in a local process.

### Prerequisites

You will need to make sure you have:

- A Sandgarden API key (get yours at [app.sandgarden.com](https://app.sandgarden.com))
- Go installed

before running the binary.

### Setup

1. Run the setup script:
   ```bash
   ./setup.sh
   ```

2. Follow the prompts to configure your API key. _This will download the Sandgarden binaries and configure a locally running director with your API key._

3. Run the director:
   ```bash
   runner -f Procfile -p .
   ```

The Director will be available at `http://localhost:8987` and visible in the [Sandgarden UI](https://app.sandgarden.com).

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