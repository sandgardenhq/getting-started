# Sandgarden Hello World

This is a simple "hello world" example using Sandgarden. It generates a haiku in homage to the tradition of writing "Hello World!" as the first example in any programming language.

### Prerequisites

* The steps below assume that you have a local director running either in a Dev Container, or are using docker-compose.
* All of the bash commands assume you are starting from the root directory of this `getting-started` repo.


### 1. Run install_workflow.sh
```bash
source ./install_workflow.sh
```

### 2. Run it!
```bash
sand runs start --workflow=trivia:latest --cluster getting-started
```