# Binary Development Mode

Run the Sandgarden Director locally without Docker.

## Prerequisites

- A Sandgarden API key (get yours at [app.sandgarden.com](https://app.sandgarden.com))
- Go installed

## Setup

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
   
   
