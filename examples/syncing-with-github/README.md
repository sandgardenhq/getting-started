# GitHub Actions Integration with Sandgarden

This example demonstrates how to use GitHub Actions to synchronize code and automatically deploy to Sandgarden.

## Workflow Outline

Imagine your team develops using feature branches. You do you work on a branch name something like `feature/my-cool-thing` and then when you are ready to start the deployment process you merge into the `development` branch using a pull request. `development` is the on deck version for your next release. It will be automatically deployed by your CICD system to your internal preview environment, for QA and verification. If everything goes ok, `development` gets merged into production and automatically deployed for customers to use.

In this example we use a github action to automatically synchronize and deploy code to Sandgarden whenever a pull request is merged into a branch that will be deployed by your CICD system. PRs merged into `development` get tagged  `development` and deployed to your  `development` Sandgarden cluster, and the same for `production`.

## How it Works

### GitHub Actions Workflow

The workflow is triggered when a pull request is merged into either `development` or `production` branches:

```yaml
on:
  pull_request:
    types: [closed]
    branches:
      - development
      - production
```

### Sync Process

1. **Environment Setup**
   - Uses Ubuntu latest runner
   - Sets up Python 3.12
   - Installs project dependencies
   - Installs Sandgarden CLI

2. **Resource Detection**
   The sync script (`sync_to_sandgarden.py`) automatically detects:
   - Changed workflows in `/workflows/*/workflow.json`
   - Changed steps in `/workflows/*/steps/*`
   - Changed prompts in `/workflows/*/steps/*/prompts/*`

3. **Resource Updates**
   For each changed resource:
   - Prompts are updated using `sand prompts create`
   - Steps are updated using `sand steps push docker`
   - Workflows are updated using `sand workflows push`
   - All resources are tagged with the target branch name

4. **Feedback**
   - Success/failure status is posted as a PR comment
   - Detailed logs show which resources were updated
   - Error messages include full context for debugging

### Required Secrets

Set these secrets in your GitHub repository:
- `SAND_API_KEY`: Your Sandgarden API key
- `SAND_API_URL`: Your Sandgarden API URL

### Project Structure

The sync process expects your Sandgarden workflows to follow the standard structure:
```
/workflows/
└── my-workflow/
    ├── workflow.json
    ├── steps/
    │   ├── 0001-first-step/
    │   │   ├── main.py
    │   │   ├── requirements.txt
    │   │   └── prompts/
    │   └── 0002-second-step/
    └── ...
```

## Usage

1. Copy `github-workflow.yml` to `.github/workflows/` in your repository
2. Set up the required secrets in your GitHub repository settings
3. Ensure your workflows follow the standard project structure
4. Create PRs targeting `development` or `production` branches

The sync will automatically run when PRs are merged, deploying your changes to the appropriate Sandgarden environment.

