# Getting Started with Sandgarden

Sandgarden is a platform to prototype, iterate, and deploy AI applications. It eliminates the overhead of:

1. Configuring and creating pipelines for AI tools and processes
2. Setting up secure testing environments for your data
3. Managing the deployment, monitoring, and scaling of production applications

It takes away overhead of configuring and creating a pipeline of all the tools and processes you need to even begin testing AI securely with your data, in your environment. Then it makes it easy to turn a prototype into a production application without having to figure out how to deploy, monitor, and scale the stack.

## Directors

To get started with Sandgarden you need a Director running to execute your code. The Director is a core component that executes your code and manages workflows. Directors:

- Organize and route workflows in real-time
- Coordinate complex batch processes
- Ensure your code has access to required infrastructure

_Technical Note: The director is a stateless Go binary designed to run in pools behind a load balancer for redundancy and scalability. Directors operate entirely in your environment while communicating with the control plane (app.sandgarden.com) for configuration, logs, and metrics._

## Running Directors

There are two ways to run directors:

### For local development:

#### Prerequisites for Local Development

To get started in local developer mode, first prepare the following:

1. Clone [this getting-started repo](https://github.com/sandgardenhq/getting-started.git), through either Git or VS Code.
2. Create a Sandgarden API Key [through the Admin UI](https://app.sandgarden.com/settings/api-keys/new).
   - Give a descriptive API Key Name (e.g. `deployment-key`).
   - For Key Type, select "Director Key".
   - For Expiration Date, choose a date conveniently far enough into the future (e.g. 30 days out).
3. Make a copy of the `.env.example` file in the root directory where you cloned this project, renaming it `.env`
   - `cp .env.example .env`
   - Update `SAND_API_KEY=YOUR_SAND_API_KEY` and replace `YOUR_SAND_API_KEY` with the Sandgarden Director key you just created.
3. _(Optional)_ Create an OpenAI API Key and keep it handy, if you would like to try one of our provided example workflows after deploying a Director.

  - [Run a director locally with Docker compose](/docker_compose/README.md)
  - [Run a dev container locally with VS Code or Cursor](/.devcontainer/README.md)


### For production:
  - [Deploy a pool of directors remotely in AWS](/aws/README.md)