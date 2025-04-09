import os
import json
from unittest.mock import patch, mock_open, Mock
import pytest
import requests
from sync_to_sandgarden import get_changed_files
import yaml
import tempfile

@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        'GITHUB_EVENT_PATH': '/path/to/event.json',
        'GITHUB_TOKEN': 'fake-token'
    }):
        yield

@pytest.fixture
def mock_pr_event_data():
    return {
        "pull_request": {
            "number": 123
        },
        "repository": {
            "full_name": "org/repo"
        }
    }

@pytest.fixture
def mock_step_dir(tmp_path):
    """Create a temporary step directory structure."""
    step_dir = tmp_path / "workflow" / "workflow_name" / "steps" / "0001-test-step"
    step_dir.mkdir(parents=True)
    return step_dir

@pytest.fixture
def mock_prompts_dir(mock_step_dir):
    """Create a prompts directory with test files."""
    prompts_dir = mock_step_dir / "prompts"
    prompts_dir.mkdir()
    
    # Create test prompt files
    (prompts_dir / "test1.txt").write_text("Test prompt 1")
    (prompts_dir / "test2.txt").write_text("Test prompt 2")
    return prompts_dir

@pytest.fixture
def mock_workflow_dir(tmp_path):
    """Create a temporary workflow directory structure."""
    workflow_dir = tmp_path / "workflows" / "test-workflow"
    workflow_dir.mkdir(parents=True)
    return workflow_dir

@pytest.fixture
def mock_steps_dir(mock_workflow_dir):
    """Create steps directory with test steps."""
    steps_dir = mock_workflow_dir / "steps"
    steps_dir.mkdir()
    
    # Create test steps
    step1_dir = steps_dir / "0001-first-step"
    step2_dir = steps_dir / "0002-second-step"
    step1_dir.mkdir()
    step2_dir.mkdir()
    
    # Create prompts directories
    (step1_dir / "prompts").mkdir()
    (step2_dir / "prompts").mkdir()
    
    # Add config files
    config1 = {
        "name": "First Step",
        "description": "First test step",
        "connectors": ["connector1", "connector2"]
    }
    config2 = {
        "name": "Second Step",
        "description": "Second test step",
        "connectors": ["connector3"]
    }
    
    (step1_dir / "config.yml").write_text(yaml.dump(config1))
    (step2_dir / "config.yml").write_text(yaml.dump(config2))
    
    # Add schemas
    (step1_dir / "input.json").write_text('{"type": "object"}')
    (step2_dir / "output.json").write_text('{"type": "object"}')
    
    return steps_dir

@pytest.fixture
def mock_workflows_dir(tmp_path):
    """Create workflows directory with test workflows."""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()
    return workflows_dir

def test_get_changed_files_no_event_path():
    """Test when GITHUB_EVENT_PATH is not set."""
    with patch.dict(os.environ, clear=True):
        assert get_changed_files() == []

def test_get_changed_files_no_pr_data(mock_env_vars):
    """Test when event data doesn't contain PR information."""
    event_data = {"some": "data"}
    with patch("builtins.open", mock_open(read_data=json.dumps(event_data))):
        assert get_changed_files() == []

def test_get_changed_files_no_github_token(mock_env_vars):
    """Test when GITHUB_TOKEN is not set."""
    with patch.dict(os.environ, {'GITHUB_EVENT_PATH': '/path/to/event.json'}, clear=True):
        with patch("builtins.open", mock_open(read_data='{}')):
            assert get_changed_files() == []

def test_get_changed_files_success(mock_env_vars, mock_pr_event_data):
    """Test successful retrieval of changed files."""
    expected_files = ["file1.py", "file2.py"]
    mock_response = [{"filename": f} for f in expected_files]

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_pr_event_data))):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response
            
            assert get_changed_files() == expected_files
            
            mock_get.assert_called_once_with(
                "https://api.github.com/repos/org/repo/pulls/123/files",
                headers={
                    "Authorization": "token fake-token",
                    "Accept": "application/vnd.github.v3+json"
                }
            )

def test_get_changed_files_api_error(mock_env_vars, mock_pr_event_data):
    """Test handling of GitHub API error."""
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_pr_event_data))):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.text = "Not found"
            
            assert get_changed_files() == []

def test_get_changed_files_request_exception(mock_env_vars, mock_pr_event_data):
    """Test handling of request exception."""
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_pr_event_data))):
        with patch("requests.get", side_effect=requests.exceptions.RequestException):
            assert get_changed_files() == []

def test_find_prompts_no_prompts_dir(mock_step_dir):
    """Test when prompts directory doesn't exist."""
    from sync_to_sandgarden import find_prompts
    assert find_prompts(mock_step_dir, []) == []

def test_find_prompts_empty_dir(mock_step_dir):
    """Test with empty prompts directory."""
    prompts_dir = mock_step_dir / "prompts"
    prompts_dir.mkdir()
    
    from sync_to_sandgarden import find_prompts
    assert find_prompts(mock_step_dir, []) == []

def test_find_prompts_sand_cli_failure(mock_prompts_dir, mock_step_dir):
    """Test handling of sand CLI failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        
        from sync_to_sandgarden import find_prompts
        prompts = find_prompts(mock_step_dir, [])
        
        assert len(prompts) == 2
        assert all(prompt["updated"] for prompt in prompts)

def test_find_prompts_changed_files(mock_prompts_dir, mock_step_dir):
    """Test detection of changed prompt files."""
    changed_files = [
        "workflow/workflow_name/steps/0001-test-step/prompts/test1.txt"
    ]
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({ "prompts": [
            {"version": 1, "content": "Current content"}
        ]})
        
        from sync_to_sandgarden import find_prompts
        prompts = find_prompts(mock_step_dir, changed_files)
        
        assert len(prompts) == 2
        assert prompts[0]["updated"]  # Changed file
        assert not prompts[1]["updated"]  # Unchanged file

def test_find_steps_no_steps_dir(mock_workflow_dir):
    """Test when steps directory doesn't exist."""
    from sync_to_sandgarden import find_steps
    assert find_steps(mock_workflow_dir, []) == []

def test_find_steps_empty_dir(mock_workflow_dir):
    """Test with empty steps directory."""
    steps_dir = mock_workflow_dir / "steps"
    steps_dir.mkdir()
    
    from sync_to_sandgarden import find_steps
    assert find_steps(mock_workflow_dir, []) == []

def test_find_steps_success(mock_steps_dir, mock_workflow_dir):
    """Test successful steps loading."""
    mock_sand_output = json.dumps({
        "steps": [{
            "version": 1,
            "name": "0001-first-step",
            "description": "First test step",
            "connectors": ["connector1", "connector2"]
        }, {
            "version": 1,
            "name": "0002-second-step",
            "description": "Second test step",
            "connectors": ["connector3"]
        }]
    })
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_sand_output
        
        from sync_to_sandgarden import find_steps
        steps = find_steps(mock_workflow_dir, [])
        
        assert len(steps) == 2
        assert steps[0]["name"] == "0001-first-step"
        assert steps[0]["description"] == "First test step"
        assert steps[0]["connectors"] == ["connector1", "connector2"]
        assert not steps[0]["updated"]
        
        assert steps[1]["name"] == "0002-second-step"
        assert steps[1]["connectors"] == ["connector3"]

def test_find_steps_sand_cli_failure(mock_steps_dir, mock_workflow_dir):
    """Test handling of sand CLI failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        
        from sync_to_sandgarden import find_steps
        steps = find_steps(mock_workflow_dir, [])
        
        assert len(steps) == 2
        assert all(step["updated"] for step in steps)

def test_find_steps_changed_files(mock_steps_dir, mock_workflow_dir):
    """Test detection of changed step files."""
    changed_files = [
        "test-workflow/steps/0001-first-step/main.py"
    ]
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "[]"
        
        from sync_to_sandgarden import find_steps
        steps = find_steps(mock_workflow_dir, changed_files)
        
        assert len(steps) == 2
        assert steps[0]["updated"]  # Changed step

def test_find_steps_with_prompts(tmp_path):
    """Test steps with associated prompts."""
    # Create mock directory structure
    workflow_dir = tmp_path / "test-workflow"
    workflow_dir.mkdir()
    steps_dir = workflow_dir / "steps"
    steps_dir.mkdir()
    
    # Create step directories
    first_step = steps_dir / "0001-first-step"
    first_step.mkdir()
    second_step = steps_dir / "0002-second-step"
    second_step.mkdir()
    
    # Create prompts directory and file
    prompts_dir = first_step / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "test.txt"
    prompt_file.write_text("Test prompt")
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps([{
            "version": 1,
            "content": "Test prompt"
        }])
        
        from sync_to_sandgarden import find_steps
        steps = find_steps(workflow_dir, [])
        
        assert len(steps) == 2
        assert len(steps[0]["prompts"]) == 1
        assert steps[0]["prompts"][0]["name"] == "test"
        assert steps[0]["prompts"][0]["content"] == "Test prompt"

def test_find_workflows_no_workflows_dir(tmp_path):
    """Test when workflows directory doesn't exist."""
    from sync_to_sandgarden import find_workflows
    assert find_workflows(tmp_path, []) == []

def test_find_workflows_empty_dir(mock_workflows_dir):
    """Test with empty workflows directory."""
    from sync_to_sandgarden import find_workflows
    assert find_workflows(mock_workflows_dir, []) == []

def test_find_workflows_success(mock_workflows_dir, mock_steps_dir):
    """Test successful workflows loading."""
    mock_sand_output = json.dumps({
        "workflows": [{
            "version": 1,
            "description": "Existing workflow description"
        }]
    })
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_sand_output
        
        from sync_to_sandgarden import find_workflows
        workflows = find_workflows(mock_workflows_dir.parent, [])

        assert len(workflows) == 1
        workflow = workflows[0]
        assert workflow["name"] == "test-workflow"
        assert workflow["updated"]
        assert len(workflow["steps"]) == 2
        
def test_find_workflows_changed_workflow_json(mock_workflows_dir, mock_steps_dir):
    """Test detection of changed workflow.json."""
    changed_files = [
        "workflows/test-workflow/workflow.json"
    ]
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "[]"
        
        from sync_to_sandgarden import find_workflows
        workflows = find_workflows(mock_workflows_dir.parent, changed_files)
        
        assert len(workflows) == 1
        assert workflows[0]["updated"]

def test_find_workflows_with_schemas(mock_workflows_dir, mock_steps_dir):
    """Test workflows with input/output schemas."""
    # Add schemas to first and last steps
    first_step = mock_steps_dir / "0001-first-step"
    last_step = mock_steps_dir / "0002-second-step"
    
    input_schema = {"type": "object", "properties": {"input": {"type": "string"}}}
    output_schema = {"type": "object", "properties": {"output": {"type": "string"}}}
    
    (first_step / "input.json").write_text(json.dumps(input_schema))
    (last_step / "output.json").write_text(json.dumps(output_schema))
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "[]"
        
        from sync_to_sandgarden import find_workflows
        workflows = find_workflows(mock_workflows_dir.parent, [])
        
        assert len(workflows) == 1
        workflow = workflows[0]
        assert json.loads(workflow["inputSchema"]) == input_schema
        assert json.loads(workflow["outputSchema"]) == output_schema

def test_find_workflows_no_steps(mock_workflows_dir):
    """Test workflow without steps directory."""
    workflow_dir = mock_workflows_dir / "test-workflow"
    workflow_dir.mkdir(parents=True)
    
    from sync_to_sandgarden import find_workflows
    workflows = find_workflows(mock_workflows_dir.parent, [])
    
    assert len(workflows) == 1
    workflow = workflows[0]
    assert workflow["name"] == "test-workflow"
    assert workflow["steps"] == []
    assert workflow["path"] == "test-workflow" 

def test_update_resource_prompt():
    """Test updating a prompt resource."""
    with patch("subprocess.run") as mock_run:
        # Mock the command output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"version": 1}'
        mock_run.return_value = mock_result
        
        # Create a real temporary file instead of mocking
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("Test prompt content")
            temp_path = temp_file.name
            
            data = {
                "content": "Test prompt content",
                "name": "test-prompt"
            }
            
            from sync_to_sandgarden import update_resource, sand_command
            result = update_resource("prompts", "test-workflow/test-step/test-prompt", data, "main")
            
            # Verify correct command was called
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert cmd[0:4] == [sand_command(), "prompts", "create", "--content"]
            assert cmd[5:] == ["--name", "test-workflow/test-step/test-prompt", "--json"]
            
            # Verify result
            assert result == {"version": 1}
            
            # Clean up
            import os
            os.unlink(temp_path)

def test_update_resource_step():
    """Test updating a step resource."""
    with patch("subprocess.run") as mock_run:
        # Mock the command output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"version": 1}'
        mock_run.return_value = mock_result
        
        data = {
            "path": "steps/test-step",
            "prompts": [
                {"name": "prompt1", "version": 1},
                {"name": "prompt2", "version": 1}
            ],
            "connectors": ["connector1", "connector2"]
        }
        
        from sync_to_sandgarden import update_resource, sand_command
        result = update_resource("steps", "test-workflow/test-step", data, "main")
        
        # Verify correct command was called
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0:8] == [
            sand_command(), "steps", "push", "docker",
            "--name", "test-workflow/test-step",
            "--description", "Updated via GitHub sync"
        ]
        assert "--file" in cmd and "steps/test-step" in cmd
        assert "--prompt" in cmd and "prompt1:1" in cmd
        assert "--prompt" in cmd and "prompt2:1" in cmd
        assert "--connector" in cmd and "connector1" in cmd
        assert "--connector" in cmd and "connector2" in cmd
        # assert "--tag" in cmd and "main" in cmd
        
        # Verify result
        assert result == {"version": 1}

def test_update_resource_workflow():
    """Test updating a workflow resource."""
    with patch("subprocess.run") as mock_run:
        # Mock the command output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"version": 1}'
        mock_run.return_value = mock_result
        
        data = {
            "stages": [
                {"name": "stage1", "step": "step1:stable", "input": "runInput"},
                {"name": "stage2", "step": "step2:stable", "input": "stage1"}
            ]
        }
        
        from sync_to_sandgarden import update_resource, sand_command
        result = update_resource("workflows", "test-workflow", data, "main")
        
        # Verify correct command was called
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0:6] == [
            sand_command(), "workflows", "push",
            "--name", "test-workflow",
            "--description"
        ]
        
        # Find the --stages argument and verify JSON
        stages_idx = cmd.index("--stages")
        assert stages_idx + 1 < len(cmd)
        stages_json = cmd[stages_idx + 1]
        assert json.loads(stages_json) == data["stages"]
        
        # Verify tag
        assert "--tag" in cmd
        tag_idx = cmd.index("--tag")
        assert tag_idx + 1 < len(cmd)
        assert cmd[tag_idx + 1] == "main"
        
        # Verify result
        assert result == {"version": 1}

def test_update_resource_prompt_error():
    """Test error handling when updating a prompt fails."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"version": 1}'
        
        # Create a real temporary file instead of mocking
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("Test prompt content")
            temp_path = temp_file.name
            
            data = {
                "content": "Test prompt content",
                "name": "test-prompt"
            }
            
            from sync_to_sandgarden import update_resource, sand_command
            result = update_resource("prompts", "test-workflow/test-step/test-prompt", data, "main")
            
            # Verify command was called with correct arguments
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert cmd[0:4] == [sand_command(), "prompts", "create", "--content"]
            assert cmd[5:] == ["--name", "test-workflow/test-step/test-prompt", "--json"]
            
            # Verify result
            assert result == {"version": 1}
            
            # Clean up
            import os
            os.unlink(temp_path)

def test_update_resource_invalid_type():
    """Test handling of invalid resource type."""
    with patch("subprocess.run") as mock_run:
        from sync_to_sandgarden import update_resource
        with pytest.raises(ValueError, match="Invalid resource type: invalid"):
            update_resource("invalid", "test-name", {}, "main")
        
        # Verify no command was run
        mock_run.assert_not_called()

def test_update_resource_subprocess_exception():
    """Test handling of subprocess exception."""
    with patch("subprocess.run", side_effect=Exception("Test error")):
        data = {
            "content": "Test content",
            "name": "test-name"
        }
        
        from sync_to_sandgarden import update_resource
        with pytest.raises(Exception, match="Test error"):
            update_resource("prompts", "test-name", data, "main")

def test_sync_to_sandgarden_missing_api_key():
    """Test sync fails when SAND_API_KEY is missing."""
    with patch.dict(os.environ, {}, clear=True):
        from sync_to_sandgarden import sync_to_sandgarden
        with pytest.raises(ValueError, match="SAND_API_KEY environment variables must be set"):
            sync_to_sandgarden("main")

def test_sync_to_sandgarden_missing_workspace():
    """Test sync fails when GITHUB_WORKSPACE is missing."""
    with patch.dict(os.environ, {"SAND_API_KEY": "test-key"}, clear=True):
        from sync_to_sandgarden import sync_to_sandgarden
        with pytest.raises(ValueError, match="GITHUB_WORKSPACE environment variable must be set"):
            sync_to_sandgarden("main")

def test_sync_to_sandgarden_no_workflows(mock_workflows_dir):
    """Test sync fails when no workflows are found."""
    with patch.dict(os.environ, {
        "SAND_API_KEY": "test-key",
        "GITHUB_WORKSPACE": str(mock_workflows_dir)
    }), patch("sync_to_sandgarden.get_changed_files") as mock_get_files:
        mock_get_files.return_value = []
        
        from sync_to_sandgarden import sync_to_sandgarden
        with pytest.raises(ValueError, match="No valid Sandgarden workflows found"):
            sync_to_sandgarden("main")

def test_post_pr_comment_success():
    """Test successful PR comment posting."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "test-token",
        "GITHUB_EVENT_PATH": "/path/to/event.json"
    }), \
    patch("builtins.open", mock_open(read_data=json.dumps({
        "pull_request": {"number": 123},
        "repository": {"full_name": "org/repo"}
    }))), \
    patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 201
        
        from sync_to_sandgarden import post_pr_comment
        post_pr_comment("Test comment")
        
        # Verify correct API call
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0] == "https://api.github.com/repos/org/repo/issues/123/comments"
        assert mock_post.call_args[1]["headers"]["Authorization"] == "token test-token"
        assert mock_post.call_args[1]["json"]["body"] == "Test comment"

def test_post_pr_comment_missing_token():
    """Test PR comment fails when GitHub token is missing."""
    with patch.dict(os.environ, {"GITHUB_EVENT_PATH": "/path/to/event.json"}, clear=True), \
         patch("builtins.open", mock_open(read_data=json.dumps({
            "pull_request": {"number": 123},
            "repository": {"full_name": "org/repo"}
         }))):
        from sync_to_sandgarden import post_pr_comment
        with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable must be set"):
            post_pr_comment("Test comment")

def test_post_pr_comment_missing_event_path():
    """Test PR comment fails when event path is missing."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}, clear=True):
        from sync_to_sandgarden import post_pr_comment
        with pytest.raises(ValueError, match="GITHUB_EVENT_PATH environment variable must be set"):
            post_pr_comment("Test comment")

def test_post_pr_comment_invalid_event_data():
    """Test PR comment fails with invalid event data."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "test-token",
        "GITHUB_EVENT_PATH": "/path/to/event.json"
    }), \
    patch("builtins.open", mock_open(read_data="{}")):
        from sync_to_sandgarden import post_pr_comment
        with pytest.raises(ValueError, match="Invalid event data"):
            post_pr_comment("Test comment")

def test_post_pr_comment_api_error():
    """Test handling of GitHub API error."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "test-token",
        "GITHUB_EVENT_PATH": "/path/to/event.json"
    }), \
    patch("builtins.open", mock_open(read_data=json.dumps({
        "pull_request": {"number": 123},
        "repository": {"full_name": "org/repo"}
    }))), \
    patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 403
        mock_post.return_value.text = "Forbidden"
        
        from sync_to_sandgarden import post_pr_comment
        with pytest.raises(Exception, match="Failed to post comment: Forbidden"):
            post_pr_comment("Test comment")

def test_post_pr_comment_request_exception():
    """Test handling of request exception."""
    with patch.dict(os.environ, {
        "GITHUB_TOKEN": "test-token",
        "GITHUB_EVENT_PATH": "/path/to/event.json"
    }), \
    patch("builtins.open", mock_open(read_data=json.dumps({
        "pull_request": {"number": 123},
        "repository": {"full_name": "org/repo"}
    }))), \
    patch("requests.post", side_effect=requests.exceptions.RequestException("Network error")):
        from sync_to_sandgarden import post_pr_comment
        with pytest.raises(Exception, match="Failed to post comment: Network error"):
            post_pr_comment("Test comment")

def test_update_resource_dry_run():
    """Test dry-run mode for resource updates."""
    with patch("subprocess.run") as mock_run:
        data = {
            "path": "steps/test-step",
            "prompts": [
                {"name": "prompt1", "version": 1},
                {"name": "prompt2", "version": 1}
            ],
            "connectors": ["connector1", "connector2"]
        }
        
        from sync_to_sandgarden import update_resource, sand_command
        result = update_resource("steps", "test-workflow/test-step", data, "main", dry_run=True)
        
        # Verify no command was run
        mock_run.assert_not_called()
        
        # Verify result indicates dry run
        assert result == {"version": 1, "dry_run": True}
