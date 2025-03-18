# GitHub Actions Integration with Sandgarden

This repository demonstrates how to use GitHub Actions to synchronize code and automatically deploy to Sandgarden.

## Workflow Outline

Imagine your team develops using feature branches. You do you work on a branch name something like `feature/my-cool-thing` and then when you are ready to start the deployment process you merge into the `development` branch using a pull request. `development` is the on deck version for your next release. It will be automatically deployed by your CICD system to your internal preview environment, for QA and verification. If everything goes ok, `development` gets merged into production and automatically deployed for customers to use.

In this example we use a github action to automatically synchronize and deploy code to Sandgarden whenever a pull request is merged into a branch that will be deployed by your CICD system. PRs merged into `development` get tagged  `development` and deployed to your  `development` Sandgarden cluster, and the same for `production`.

