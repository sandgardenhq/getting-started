# Local Developer Mode Notes

Local developer mode runs the director in a container in a local docker image.

* Vanilla
* Dev Container

## Improvements

* [ ] Dev mode routing
* [ ] Fill in an example workflow
* [x] Remove postgres database
* [x] Simplify configuration
* [x] Mount a local volume with code?
* [x] Can we use dev containers?

## Docker demo env

### Starting
```bash
    docker compose build sandgarden
    docker compose up -d
```

### Connecting to the shell
```bash
    docker compose exec -it sandgarden /bin/bash
```

### Show logs
```bash
    docker compose logs -f sandgarden
```

### Stopping
```bash
    docker compose down
```