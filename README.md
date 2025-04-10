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

### Running Directors

There are two ways to run directors:

* For development: [Run a director locally](/local/README.md)
* For production: [Deploy a pool of directors remotely in AWS](/aws/README.md)

_Technical Note: The director is a stateless Go binary designed to run in pools behind a load balancer for redundancy and scalability. Directors operate entirely in your environment while communicating with the control plane (app.sandgarden.com) for configuration, logs, and metrics._
