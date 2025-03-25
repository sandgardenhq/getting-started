# Binary Development Mode

Run the Sandgarden Director binary locally.

## Prerequisites

- [Docker installed](https://docs.docker.com/get-started/get-docker/)
- A Sandgarden API key (get yours at [app.sandgarden.com](https://app.sandgarden.com))
- Download the Sandgarden CLI from the [downloads page](https://app.sandgarden.com/downloads)

## Setup

1. Run the setup command and provide your API key:

```bash
$ sand dev init
```

2. Run the director:

```bash
$ sand dev start
```

The Director will be available at `https://localhost:8987` and visible in the [Sandgarden UI](https://app.sandgarden.com).
