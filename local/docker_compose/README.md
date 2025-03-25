# Docker Compose Development Mode

Start the Sandgarden Director in a local docker container.

## Setup

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

The Director service will be available at `http://localhost:8987` and should be visible in the [Sandgarden UI](https://app.sandgarden.com).
