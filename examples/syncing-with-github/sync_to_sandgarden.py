#!/usr/bin/env python3
import os
import sys
import json
import requests
from typing import Dict, Any, List
from pathlib import Path

def get_changed_files() -> List[str]:
    """Get list of files changed in the PR using GitHub API."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        print("No event data found")
        return []
        
    try:
        with open(event_path) as f:
            event_data = json.load(f)
            
        # For PR merge events, we need to get the PR number from the event
        if "pull_request" not in event_data:
            print("No PR data found in event")
            return []
            
        pr_number = event_data["pull_request"]["number"]
        repo = event_data["repository"]["full_name"]
        github_token = os.environ.get("GITHUB_TOKEN")
        
        if not github_token:
            print("No GitHub token found")
            return []
            
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return [file["filename"] for file in response.json()]
        else:
            print(f"Error fetching PR files: {response.text}")
            
    except Exception as e:
        print(f"Error processing event data: {e}")
        
    return []

def find_prompts(step_dir: Path, changed_files: List[str]) -> List[Dict[str, Any]]:
    """Find all prompts for a step."""
    prompts = []
    prompts_dir = step_dir / "prompts"
    
    if not prompts_dir.exists():
        return prompts
    
    for prompt_file in prompts_dir.glob("*.txt"):
        prompt_data = None
        try:
            # Try to get prompt data from sand CLI
            import subprocess
            result = subprocess.run(
                ["/usr/local/bin/sand", "prompts", "list", "--name", f"{step_dir.parent.parent.name}/{step_dir.name}/{prompt_file.stem}", "--json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                prompts_list = json.loads(result.stdout)
                if prompts_list:
                    # Get the latest version
                    latest_prompt = max(prompts_list, key=lambda x: x.get("version", 0))
                    prompt_data = latest_prompt.get("content")
        except Exception as e:
            print(f"Error getting prompt data from sand CLI for {prompt_file.name}: {e}")
        
        # Check if this prompt file was changed in the PR or not found in Sandgarden
        prompt_path = str(prompt_file.relative_to(step_dir.parent.parent.parent))
        is_updated = prompt_path in changed_files or prompt_data is None
        
        prompts.append({
            "name": prompt_file.stem,
            "path": str(prompt_file.relative_to(step_dir)),
            "content": prompt_data,
            "updated": is_updated
        })
    
    return prompts

def find_steps(workflow_dir: Path, changed_files: List[str]) -> List[Dict[str, Any]]:
    """Find all steps for a workflow."""
    steps = []
    steps_dir = workflow_dir / "steps"
    
    if not steps_dir.exists():
        return steps
    
    for step_dir in steps_dir.iterdir():
        if not step_dir.is_dir():
            continue
            
        step_data = None
        try:
            # Try to get step data from sand CLI
            import subprocess
            result = subprocess.run(
                ["/usr/local/bin/sand", "steps", "list", "--name", f"{workflow_dir.name}/{step_dir.name}", "--json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                steps_list = json.loads(result.stdout)
                if steps_list:
                    # Get the latest version
                    latest_step = max(steps_list, key=lambda x: x.get("version", 0))
                    step_data = latest_step.get("config")
        except Exception as e:
            print(f"Error getting step data from sand CLI for {step_dir.name}: {e}")
        
        # Check if any files in the step directory (except prompts) have changed
        step_path = str(step_dir.relative_to(workflow_dir))
        is_updated = False
        for changed_file in changed_files:
            if changed_file.startswith(f"{step_path}/") and not changed_file.startswith(f"{step_path}/prompts/"):
                is_updated = True
                break
        
        # Find prompts for this step
        prompts = find_prompts(step_dir, changed_files)
        
        steps.append({
            "name": step_dir.name,
            "path": str(step_dir.relative_to(workflow_dir)),
            "config": step_data,
            "prompts": prompts,
            "updated": is_updated or step_data is None
        })
    
    return steps

def find_workflows(workspace_path: Path, changed_files: List[str]) -> List[Dict[str, Any]]:
    """Find all Sandgarden workflows in the workspace."""
    workflows = []
    workflows_dir = workspace_path / "workflows"
    
    if not workflows_dir.exists():
        print(f"No workflows directory found at {workflows_dir}")
        return workflows
    
    for workflow_dir in workflows_dir.iterdir():
        if not workflow_dir.is_dir():
            continue
            
        workflow_json = workflow_dir / "workflow.json"
        workflow_data = None
        
        if workflow_json.exists():
            try:
                with open(workflow_json) as f:
                    workflow_data = json.load(f)
            except Exception as e:
                print(f"Error reading workflow.json in {workflow_dir}: {e}")
        
        if not workflow_data:
            try:
                # Try to get workflow data from sand CLI
                import subprocess
                result = subprocess.run(
                    ["/usr/local/bin/sand", "workflows", "list", "--name", workflow_dir.name, "--json"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    workflows_list = json.loads(result.stdout)
                    if workflows_list:
                        # Get the latest version
                        latest_workflow = max(workflows_list, key=lambda x: x.get("version", 0))
                        workflow_data = latest_workflow.get("config")
            except Exception as e:
                print(f"Error getting workflow data from sand CLI for {workflow_dir.name}: {e}")
        
        # Check if workflow.json has changed
        workflow_path = str(workflow_dir.relative_to(workspace_path))
        is_updated = False
        for changed_file in changed_files:
            if changed_file == f"{workflow_path}/workflow.json":
                is_updated = True
                break
        
        # Find steps for this workflow
        steps = find_steps(workflow_dir, changed_files)
        
        workflows.append({
            "name": workflow_dir.name,
            "path": str(workflow_dir.relative_to(workspace_path)),
            "config": workflow_data,
            "steps": steps,
            "updated": is_updated or workflow_data is None
        })
    
    return workflows

# TODO: How to find and include connectors?
# TODO: How to find and include env VARS?
# TODO: How to find and include schemas for steps and workflows?
def update_resource(resource_type: str, name: str, data: Dict[str, Any], branch: str) -> None:
    """Update a resource in Sandgarden using the sand utility."""
    try:
        import subprocess
        if resource_type == "prompts":
            # For prompts, we need to write content to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(data["content"])
                temp_path = f.name
            
            cmd = [
                "/usr/local/bin/sand", "prompts", "create",
                "--content", temp_path,
                "--name", name,
                "--tag", branch
            ]
        elif resource_type == "steps":
            cmd = [
                "/usr/local/bin/sand", "steps", "push", "docker",
                "--name", name,
                "--description", "Updated via GitHub sync",
                "--file", data["path"],
                "--tag", branch
            ]
            # Add any prompts associated with this step
            for prompt in data.get("prompts", []):
                cmd.extend(["--prompt", f"{name}/{prompt['name']}"])
        else:  # workflows
            cmd = [
                "/usr/local/bin/sand", "workflows", "push",
                "--name", name,
                "--description", "Updated via GitHub sync",
                "--stages", json.dumps(data["config"]),
                "--tag", branch
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully updated {resource_type} {name}")
        else:
            print(f"Error updating {resource_type} {name}: {result.stderr}")
            
        if resource_type == "prompts":
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"Error updating {resource_type} {name}: {e}")

def sync_to_sandgarden(branch: str, environment: str) -> Dict[str, Any]:
    """Sync code to Sandgarden using the provided branch and environment."""
    api_key = os.environ.get("SAND_API_KEY")
    api_url = os.environ.get("SAND_API_URL")
    
    if not api_key or not api_url:
        raise ValueError("SAND_API_KEY and SAND_API_URL environment variables must be set")
    
    # Get the GitHub workspace directory
    github_workspace = os.environ.get("GITHUB_WORKSPACE")
    if not github_workspace:
        raise ValueError("GITHUB_WORKSPACE environment variable must be set")
    
    workspace_path = Path(github_workspace)
    
    # Get list of changed files from PR
    changed_files = get_changed_files()
    
    # Find all workflows
    workflows = find_workflows(workspace_path, changed_files)
    if not workflows:
        raise ValueError("No valid Sandgarden workflows found")
    
    print(f"Found {len(workflows)} workflows to sync")
    
    # Track synced resources
    synced_resources = {
        "workflows": [],
        "steps": [],
        "prompts": []
    }
    
    # Update resources in Sandgarden
    for workflow in workflows:
        for step in workflow.get("steps", []):
            for prompt in step.get("prompts", []):
                if prompt.get("updated"):
                    print(f"\nUpdating prompt: {workflow['name']}/{step['name']}/{prompt['name']}")
                    update_resource("prompts", f"{workflow['name']}/{step['name']}/{prompt['name']}", prompt, branch)
                    synced_resources["prompts"].append(f"{workflow['name']}/{step['name']}/{prompt['name']}")
            
            if step.get("updated"):
                print(f"\nUpdating step: {workflow['name']}/{step['name']}")
                update_resource("steps", f"{workflow['name']}/{step['name']}", step, branch)
                synced_resources["steps"].append(f"{workflow['name']}/{step['name']}")
            
        
        if workflow.get("updated"):
            print(f"\nUpdating workflow: {workflow['name']}")
            update_resource("workflows", workflow["name"], workflow, branch)
            synced_resources["workflows"].append(workflow["name"])
    
    return synced_resources

def post_pr_comment(message: str) -> None:
    """Post a comment on the PR using GitHub API."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        print("No PR event data found, skipping comment")
        return
        
    try:
        with open(event_path) as f:
            event_data = json.load(f)
            if "pull_request" not in event_data:
                print("No PR data found, skipping comment")
                return
                
            pr_number = event_data["pull_request"]["number"]
            repo = event_data["repository"]["full_name"]
            
            # Get GitHub token from environment
            github_token = os.environ.get("GITHUB_TOKEN")
            if not github_token:
                print("No GitHub token found, skipping comment")
                return
                
            # Post comment using GitHub API
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
            data = {"body": message}
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 201:
                print(f"Failed to post comment: {response.text}")
                
    except Exception as e:
        print(f"Error posting PR comment: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sync_to_sandgarden.py <branch> <environment>")
        sys.exit(1)
        
    branch = sys.argv[1]
    environment = sys.argv[2]
    
    try:
        synced = sync_to_sandgarden(branch, environment)
        print(f"Successfully synced to Sandgarden")
        
        # Build success message
        message = "# ✅ Sandgarden Sync Complete\n\n"
        message += "Successfully synced the following resources to Sandgarden:\n\n"
        
        for resource_type, resources in synced.items():
            if resources:
                message += f"## {resource_type.title()}\n"
                for resource in resources:
                    message += f"- `{resource}`\n"
                message += "\n"
        
        print("\nSynced resources:")
        for resource_type, resources in synced.items():
            if resources:
                print(f"\n{resource_type.title()}:")
                for resource in resources:
                    print(f"  - {resource}")
                    
        # Post success comment
        post_pr_comment(message)
        
    except Exception as e:
        error_msg = "# ❌ Sandgarden Sync Failed\n\n"
        error_msg += f"Failed to sync to Sandgarden with the following error:\n\n"
        error_msg += f"```\n{str(e)}\n```"
        print(error_msg, file=sys.stderr)
        # Post error comment
        post_pr_comment(error_msg)
        sys.exit(1) 