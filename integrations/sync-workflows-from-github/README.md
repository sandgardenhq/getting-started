# GitHub Actions Integration with Sandgarden

This script is run by as a Github Action (`.github/workflows/sync-workflows.yml`) and synchronizes all of the workflows steps and prompts from Github to Sandgarden. Whenever, a pull request is merged to `main` it will update all of the affected workflows, steps, and prompts. 

```
NOTE: It does not handle the creation of connectors yet because we haven't implemented secrets handling.
```

## How it Works

### GitHub Actions Workflow

The workflow is triggered when a pull request is merged into `main`:

```yaml
name: Sync to Sandgarden

on:
  pull_request:
    types: [closed]
    branches:
      - main
...
```

### Sync Process

The sync script (`sync_to_sandgarden.py`) automatically detects:
- Changes to workflows in `/workflows/*/**`
- Changes to steps in `/workflows/*/steps/*`
- Changes to prompts in `/workflows/*/steps/*/prompts/*`

Changes percolate up. So, if you update a prompt that a step relies on, the step will be updaetd to use the new version of the prompt, likewise for a work a workflow that depends on a step.

All changes are pushed to Sandgarden using the Sandgarden CLI. _(The script automatically downloads and installs the latest version of the CLI.)_

### Required Secrets

Set these secrets in your GitHub repository:
- `SAND_API_KEY`: Your Sandgarden API key

### Project Structure

The sync process expects your Sandgarden workflows to follow a standard structure:
```
/workflows/
└── my-workflow/
    ├── config.yml
    ├── steps/
    │   ├── 0001-first-step/
    │   │   ├── config.yml
    │   │   ├── main.py
    │   │   ├── requirements.txt
    │   │   └── prompts/
    │   └── 0002-second-step/
    └── ...
```

### `config.yml`

The `config.yml` file steps and workflows is an optional configuration file you can use to control things like the descriptions and tags.

**For steps this is how you can bind connectors.**

1. **Workflow-level config.yml** (in `/workflows/<workflow-name>/config.yml`):
```yaml
# All fields are optional
name: Workflow Name
description: Workflow description
tags:
  - list of tags
# tag of the steps to attach to the workflow, if this is not specified the script
# will just use the most recent version
step_version: stable  
```

2. **Step-level config.yml** (in `/workflows/<workflow-name>/steps/<step-name>/config.yml`):
```yaml
# All fields are optional
name: Step Name
description: Step description
connectors:
  - list of connector names
tags:
  - list of tags
# If this step fails, should the workflow abort and fail or continue
abort_on_error: true  
```

## Usage

1. Copy `gh_action.yml` to `.github/workflows/` in your repository, and rename it to `sync-to-sandgarden.yml` (or whatever you like)
2. Set up the required secrets in your GitHub repository settings
3. Ensure that the branch listed in the configuration is the one you want to sync from
5. Make sure your workflows follow the standard project structure
6. Create PRs targeting your sync branch

The sync will automatically run when PRs are merged.

### Caveats

- This is only written to support a single sync environment. (Multiple branhces and environments coming soon.)
- Steps and workflows will only get tagged with the first tag from your list. (Fix coming soon for that as well.)

