## Directors

To get started with Sandgarden you need a Director running to execute your code. The Director is a core component that executes your code and manages workflows. Directors:
- Organize and route workflows in real-time
- Coordinate complex batch processes
- Ensure your code has access to required infrastructure

### Running Directors

There are two ways to run directors:

* For development: [Run a director locally](/local/README.md)
* For production: [Deploy a pool of directors remotely in AWS](/aws/vpc/README.md)

_Technical Note: The director is a stateless Go binary designed to run in pools behind a load balancer for redundancy and scalability. Directors operate entirely in your environment while communicating with the control plane (app.sandgarden.com) for configuration, logs, and metrics._
