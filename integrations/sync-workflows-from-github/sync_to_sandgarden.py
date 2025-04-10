#!/usr/bin/env python3
import os
import sys
import json
import yaml
import requests
import argparse
from typing import Dict, Any, List
from pathlib import Path
import re
import subprocess
import platform

def download_sand_cli() -> str:
    """Download and setup the Sandgarden CLI.
    
    Returns:
        str: Path to the downloaded CLI binary
    """
    cli_dir = Path("/tmp/sandgarden-cli")
    cli_dir.mkdir(exist_ok=True)
    
    # Determine OS and architecture
    system = platform.system().lower()
    arch = platform.machine().lower()
    if arch == "x86_64":
        arch = "amd64"
    
    # Download URL
    url = f"https://api.sandgarden.com/api/v1/assets/sand/latest/sand_{system}_{arch}"
    
    # Download the CLI
    cli_path = cli_dir / "sand"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(cli_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    # Make it executable
    cli_path.chmod(0o755)
    
    return str(cli_path)

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
            print(f"PR files:")
            for file in response.json():
                print(f"  - {file['filename']}")
            return [file["filename"] for file in response.json()]
        else:
            print(f"Error fetching PR files: {response.text}")
            
    except Exception as e:
        print(f"Error processing event data: {e}")
        
    return []

def sand_command() -> str:
    """Returns the path to the sand command."""
    if os.environ.get("SAND_CLI_PATH"):
        return os.environ.get("SAND_CLI_PATH")
    else:
        return "sand"

def find_prompts(step_dir: Path, changed_files: List[str]) -> List[Dict[str, Any]]:
    """Find all prompts for a step."""
    prompts = []
    prompts_dir = step_dir / "prompts"
    
    if not prompts_dir.exists():
        return prompts
    
    for prompt_file in prompts_dir.glob("*"):
        prompt_data = None
        try:
            # Try to get prompt data from sand CLI
            result = subprocess.run(
                [sand_command(), "prompts", "list", "--name", prompt_file.stem, "--json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                prompts_list = json.loads(result.stdout)
                if prompts_list.get('prompts'):
                    # Get the latest version
                    latest_prompt = max(prompts_list.get('prompts'), key=lambda x: x.get("version", 0))
                    prompt_data = latest_prompt
        except Exception as e:
            print(f"Error getting prompt data from sand CLI for {prompt_file.name}: {e}")

        # Check if this prompt file was changed in the PR or not found in Sandgarden
        prompt_path = str(prompt_file.relative_to(step_dir.parent.parent.parent.parent))
        is_updated = prompt_path in changed_files or prompt_data is None
        updated_content = None
        version = 0
        
        if is_updated:
            updated_content = prompt_file.read_text()
        else:
            updated_content = prompt_data.get("content")
            version = prompt_data.get("version", 0)
        prompts.append({
            "name": prompt_file.stem,
            "path": str(prompt_file.relative_to(step_dir)),
            "content": updated_content,
            "updated": is_updated or prompt_data is None,
            "version": version
        })
    
    return prompts

def format_step_name(step_dir_name: str) -> str:
    """Format step name by removing prefix numbers and underscores.
    
    Args:
        step_dir_name: Name of the step directory (e.g. '0001_first_step')
        
    Returns:
        Formatted step name (e.g. 'first_step')
    """
    # Remove any leading digits and underscores
    return re.sub(r'^\d+_', '', step_dir_name)

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
            result = subprocess.run(
                [sand_command(), "steps", "list", "--name", format_step_name(step_dir.name), "--json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                steps_list = json.loads(result.stdout)
                if steps_list.get('steps'):
                    # Get the latest version
                    latest_step = max(steps_list.get('steps'), key=lambda x: x.get("version", 0))
                    step_data = latest_step
        except Exception as e:
            print(f"Error getting step data from sand CLI for {format_step_name(step_dir.name)}: {e}")
        
        # Check if any files in the step directory (except prompts) have changed
        step_path = str(step_dir.relative_to(workflow_dir.parent))
        is_updated = False
        for changed_file in changed_files:
            if changed_file.startswith(f"workflows/{step_path}") and not changed_file.startswith(f"workflows/{step_path}/prompts/"):
                is_updated = True
                break
        
        # Find prompts for this step
        # TODO: how to handle prompts that are not in a step?
        prompts = find_prompts(step_dir, changed_files)
        
        for prompt in prompts:
            if prompt.get("updated"):
                is_updated = True
                break
        
        # Read config from config.yml if it exists
        connectors = []
        description = None
        config_file = step_dir / "config.yml"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = yaml.safe_load(f)
                    if config:
                        if "connectors" in config:
                            connectors = config["connectors"]
                        if "description" in config:
                            description = config["description"]
            except Exception as e:
                print(f"Error reading config.yml in {step_dir}: {e}")
        
        # If no description in config.yml, try to get it from step_data
        if description is None and step_data and "description" in step_data:
            description = step_data["description"]
            
        # If still no description, use placeholder
        if description is None:
            description = f"Step {format_step_name(step_dir.name)} in workflow {workflow_dir.name}"
        
        steps.append({
            "name": format_step_name(step_dir.name),
            "path": str(step_dir),
            "config": step_data,
            "prompts": prompts,
            "connectors": connectors,
            "description": description,
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
        
        config = {}
        config_file = workflow_dir / "config.yml"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = yaml.safe_load(f)
            except Exception as e:
                print(f"Error reading config.yml in {workflow_dir}: {e}")
                
        workflow_name = config.get("name", workflow_dir.name)    
        workflow_data = None
        try:
            # Try to get workflow data from sand CLI
            result = subprocess.run(
                [sand_command(), "workflows", "list", "--name", workflow_name, "--json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                workflows_list = json.loads(result.stdout)
                if workflows_list.get('workflows'):
                    # Get the latest version
                    latest_workflow = max(workflows_list.get('workflows'), key=lambda x: x.get("version", 0))
                    workflow_data = latest_workflow
        except Exception as e:
            print(f"Error getting workflow data from sand CLI for {workflow_dir.name}: {e}")
        
        
        
        steps_dir = workflow_dir / "steps"
        input_schema = {}
        output_schema = {}
        if steps_dir.exists():
            # Sort step directories to maintain order
            step_dirs = sorted([d for d in steps_dir.iterdir() if d.is_dir()])
            
            for i, step_dir in enumerate(step_dirs):
                # First stage gets workflow input and we check for input schema
                if i == 0:                    
                    # Check for input schema in first step
                    input_schema_path = step_dir / "input.json"
                    if input_schema_path.exists():
                        try:
                            with open(input_schema_path) as f:
                                input_schema = f.read()
                        except Exception as e:
                            print(f"Error reading input schema from {input_schema_path}: {e}")
                # If this is the last step, check for output schema
                if i == len(step_dirs) - 1:
                    output_schema_path = step_dir / "output.json"
                    if output_schema_path.exists():
                        try:
                            with open(output_schema_path) as f:
                                output_schema = f.read()
                        except Exception as e:
                            print(f"Error reading output schema from {output_schema_path}: {e}")
                            
        # Check if workflow.json has changed (still track changes for sync purposes)
        workflow_path = str(workflow_dir.relative_to(workflows_dir))
        is_updated = False
        for changed_file in changed_files:
            # Check if changed file starts with workflow path
            if changed_file.startswith(f"workflows/{workflow_path}") and not changed_file.startswith(f"workflows/{workflow_path}/steps/"):
                is_updated = True
                break
        
        # Find steps for this workflow
        # TODO: what if it is a step that is not in a workflow?
        # rename steps to functions and add a functions directory at the root for functions not in a workflow
        # keep the workflow directory named steps
        # Figure out how to handle functions shared between workflows
        steps = find_steps(workflow_dir, changed_files)
        for step in steps:
            if step.get("updated", False):
                is_updated = True
                break

        workflows.append({
            "name": config.get("name", workflow_dir.name),
            "description": config.get("description", ""),
            "path": str(workflow_path),
            "steps": steps,
            "inputSchema": input_schema,
            "outputSchema": output_schema,
            "updated": is_updated or workflow_data is None
        })
    
    return workflows

def update_resource(resource_type: str, name: str, data: Dict[str, Any], tag: str, dry_run: bool = False) -> Dict[str, Any]:
    """Update a resource in Sandgarden using the sand utility.
    
    Args:
        resource_type: Type of resource (prompts, steps, workflows)
        name: Resource name
        data: Resource data
        tag: tag to apply
        dry_run: If True, only print commands without executing them
        
    Returns:
        Dict[str, Any]: The response from the sand command
        
    Raises:
        ValueError: If the command fails or returns invalid JSON
    """
    if resource_type == "prompts":
        cmd = [
            sand_command(), "prompts", "create",
            "--content", data["content"],
            "--name", name,
            "--json"
        ]
    elif resource_type == "steps":
        cmd = [
            sand_command(), "steps", "push", "docker",
            "--name", name,
            "--description", "Updated via GitHub sync",
            "--file", os.path.relpath(data["path"]),
            "--sync",
            "--tag", tag,
            "--json"
        ]
        # Add any prompts associated with this step
        for prompt in data.get("prompts", []):
            cmd.extend(["--prompt", f"{prompt['name']}:{prompt['version']}"])
        # Add any connectors associated with this step
        for connector in data.get("connectors", []):
            cmd.extend(["--connector", connector])
    elif resource_type == "workflows":  # workflows
        cmd = [
            sand_command(), "workflows", "push",
            "--name", name,
            "--description", "Updated via GitHub sync",
            "--stages", json.dumps(data["stages"]),
            "--tag", tag,
            "--json"
        ]
    else:
        raise ValueError(f"Invalid resource type: {resource_type}")
    
    if dry_run:
        print(f"\nWould run command:\n{' '.join(cmd)}")
        return {"version": 1, "dry_run": True}
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error updating {resource_type} {name}: {result.stdout}\n{result.stderr}")
        raise ValueError(f"Failed to update {resource_type} {name}")
        
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from sand command: {e}")

def build_workflow_config(workflow: Dict[str, Any], workspace_path: str) -> Dict[str, Any]:
    """Build workflow configuration from workflow data.
    
    Args:
        workflow: Dictionary containing workflow data including steps
        
    Returns:
        Dict containing workflow configuration with stages
    """
    stages = []
    steps = workflow.get("steps", [])
    
    # Get workflow config
    workflow_dir = Path(workspace_path / "workflows" / workflow["path"])
    config_file = workflow_dir / "config.yml"
    
    workflow_config = {}
    if config_file.exists():
        try:
            with open(config_file) as f:
                workflow_config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error reading config.yml in {workflow_dir}: {e}")
            
    # Get step_version from workflow config if specified
    step_version = workflow_config.get("step_version")
    
    input_schema = None
    output_schema = None
    for i, step in enumerate(steps):
        # Use workflow step_version if specified, otherwise use step's own version
        version = step_version or step.get("config", {}).get("version")
        if not version:
            raise ValueError(f"Step {step['name']} has no version in its config and no step_version specified in workflow config")
            
        stage = {
            "name": step["name"],
            "step": f"{step['name']}:{version}",
            "abortOnError": True
        }
        
        # First stage gets workflow input
        if i == 0:
            stage["input"] = "runInput"
            stage["workflowRunInput"] = True    
            input_schema = step.get("inputSchema")
        else:
            # Other stages get input from previous stage
            stage["input"] = f"stage{i-1}"
            stage["stageInput"] = i-1
            output_schema = step.get("outputSchema")
            
        stages.append(stage)
    
    return {
        "stages": stages,
        "inputSchema": input_schema if input_schema else "{}",
        "outputSchema": output_schema if output_schema else "{}",
        "step_version": step_version,
        "tags": workflow_config.get("tags", [])
    }

def sync_to_sandgarden(branch: str, dry_run: bool = False) -> Dict[str, Any]:
    """Sync code to Sandgarden using the provided branch and environment."""
    api_key = os.environ.get("SAND_API_KEY")
    
    if not api_key:
        raise ValueError("SAND_API_KEY environment variables must be set")
    
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

    # Print sync status
    for workflow in workflows:
        if workflow.get("updated"):
            print(f"Workflow: {workflow['name']} ⚡")        
        for step in workflow.get("steps", []):
            if step.get("updated"):
                print(f"  Step: {step['name']} ⚡")     
            for prompt in step.get("prompts", []):
                if prompt.get("updated"):
                    print(f"    Prompt: {prompt['name']} ⚡")
            
    # Track synced resources
    synced_resources = {
        "workflows": [],
        "steps": [],
        "prompts": []
    }
    
    # Update resources in Sandgarden
    for workflow in workflows:               
        data = build_workflow_config(workflow, workspace_path)
        for step in workflow.get("steps", []):
            for prompt in step.get("prompts", []):
                if prompt.get("updated"):
                    try:
                        results = update_resource("prompts", prompt["name"], prompt, branch, dry_run)
                        synced_resources["prompts"].append(prompt["name"])
                        prompt["version"] = results["version"]
                    except Exception as e:
                        print(f"Error updating prompt {prompt['name']}: {e}")
                        continue
            if step.get("updated"):
                try:
                    tag = data["step_version"] or branch
                    step_data = step.get("config", {})
                    if step_data["tags"] and len(step_data["tags"]) > 0:
                        tag = step_data["tags"][0]
                    results = update_resource("steps", step["name"], step, tag, dry_run)
                    synced_resources["steps"].append(step["name"])
                    step["version"] = results["version"]
                except Exception as e:
                    print(f"Error updating step {step['name']}: {e}")
                    continue
        
        if workflow.get("updated"):
            try:
                tag = branch
                if data["tags"] and len(data["tags"]) > 0:
                    tag = data["tags"][0]
                update_resource("workflows", workflow["name"], data, tag, dry_run)
                synced_resources["workflows"].append(workflow["name"])
            except Exception as e:
                print(f"Error updating workflow {workflow['name']}: {e}")
                continue
                    
    
    return synced_resources

def post_pr_comment(message: str) -> None:
    """Post a comment on the PR using GitHub API."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise ValueError("GITHUB_EVENT_PATH environment variable must be set")
        
    try:
        with open(event_path) as f:
            event_data = json.load(f)
            if "pull_request" not in event_data:
                raise ValueError("Invalid event data")
                
            pr_number = event_data["pull_request"]["number"]
            repo = event_data["repository"]["full_name"]
            
            # Get GitHub token from environment
            github_token = os.environ.get("GITHUB_TOKEN")
            if not github_token:
                raise ValueError("GITHUB_TOKEN environment variable must be set")
                
            # Post comment using GitHub API
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
            data = {"body": message}
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 201:
                raise Exception(f"Failed to post comment: {response.text}")
                
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to post comment: {str(e)}")
    except Exception as e:
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync workflows to Sandgarden")
    parser.add_argument("branch", help="Branch name for tagging")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    args = parser.parse_args()
    
    print("🔄 Syncing to Sandgarden")
    try:
        synced = sync_to_sandgarden(args.branch, args.dry_run)
        
        # Build success message
        message = "\n# ✅ Sync Complete\n"
        if len(synced["workflows"]) + len(synced["steps"]) + len(synced["prompts"]) > 0:
            message += "Successfully synced the following resources to Sandgarden:\n\n"
        
        for resource_type, resources in synced.items():
            if resources:
                message += f"## {resource_type.title()}\n"
                for resource in resources:
                    message += f"- {resource}\n"
                message += "\n"
                            
        # Post success comment
        post_pr_comment(message)
        print('\n'.join(re.sub(r'^#+\s+', '', line) for line in message.split('\n')))
    except Exception as e:
        error_msg = "# ❌ Sandgarden Sync Failed\n\n"
        error_msg += f"Failed to sync to Sandgarden with the following error:\n\n"
        error_msg += f"```\n{str(e)}\n```"
        print(error_msg.replace("# ", ""), file=sys.stderr)
        # Post error comment
        post_pr_comment(error_msg)
        sys.exit(1) 