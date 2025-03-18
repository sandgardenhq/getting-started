# Triggering Sandgarden Workflows from GitHub Actions

This example demonstrates how to trigger and execute Sandgarden workflows directly from GitHub Actions.

## Getting Started

1. Get your Sandgarden API Key:
   - Visit [Sandgarden API Keys](https://app.sandgarden.com/settings/api-keys)
   - Click "Create API Key"
   - Save the key securely - you'll need it in step 3

2. Copy `github-workflow.yml` to your repository's `.github/workflows` directory and rename it appropriately (e.g., `summarize-pr.yml`, `process-issue.yml`)

3. Customize the workflow file:

   a. Configure trigger events:
   ```yaml
   on:
     # Replace with your desired trigger events
     pull_request:
       types: [opened, synchronize, reopened]
   ```

   b. Set up secrets in your GitHub repository:
   - Go to Settings → Secrets and variables → Actions
   - Add `SAND_API_KEY` with your Sandgarden API key
   - Add `SAND_API_URL` with your workflow's endpoint URL (found on your workflow's page at app.sandgarden.com)

   c. Configure workflow inputs:
   ```yaml
   -d "{\"input\": {\"text\": \"WHATEVER INPUTS YOU WANT\", \"number\": 3}}"
   ```
   Replace with your workflow's input schema. You can reference GitHub context using `${{ github.event.xxx }}`.

   Example for PR processing:
   ```yaml
   -d "{\"input\": {\"pr_title\": \"${{ github.event.pull_request.title }}\", \"pr_body\": \"${{ github.event.pull_request.body }}\"}}"
   ```

### 🤷 But what if I just want to run an individual step? 🤷 

Steps work exactly the same way. Just use the URL of the step you want to run as your `SAND_API_URL`.
