# Getting Started with Sandgarden

Sandgarden is a platform to prototype, iterate, and deploy AI applications. It takes away overhead of configuring and creating a pipeline of all the tools and processes you need to even begin testing AI securely with your data, in your environment. Then it makes it trivial to turn a prototype into a production application without having to figure out how to deploy, monitor, and scale the stack.

To get started with Sandgarden you need to get a Director running to execute your code. Directors organize, execute, and route workflows in real-time. They are also responsible for coordinating complex batch processes and ensuring that your code has the access to the infrastructure it needs. 

There are two ways tor un directors.

* For development you can [run a director locally](/local/README.md).
* You can [deploy a pool of directors remotely in AWS](/aws/vpc/README.md)

_The director is a stateless Go binary. Directors are designed to be deployed in pools behind a load balancer for redundancy and scalability. They run entirely in your environment and communicate with the control plane (app.sandgarden.com) to share configuration, logs, and metrics._

