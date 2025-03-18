# Sandgarden Examples

This directory contains examples showcasing different capabilities of Sandgarden, a platform for deploying AI-assisted workflows. Each example follows Sandgarden's project structure guidelines with properly organized steps, prompts, and configuration files.

```
workflows/
  trivia/ 
  pr-summarizer/
triggering-a-workflow-from-cicd/ 
syncing-with-github/ 
```

## Workflows

Located in [workflows/](./workflows/):

- **[Trivia](./workflows/trivia/)**: A simple workflow using an _LLM as judge_ pattern to illustrate how to build workflows with Sandgarden.
- **[PR Summarizer](./workflows/pr-summarizer/)**: A production-ready workflow that automatically adds AI-generated summaries to Pull Requests on GitHub, improving code review efficiency.


## Integrations

- **[Triggering a Workflow from CICD](./triggering-a-workflow-from-cicd/)**: An example of triggering a workflow from Github Actions.
- **[Syncing with GitHub](./syncing-with-github/)**: An example of setting up continuous deployment between Sandgarden and GitHub.

