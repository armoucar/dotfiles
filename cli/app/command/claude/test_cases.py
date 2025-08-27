"""Test cases for Claude Code permission validation."""

from typing import Dict, List, TypedDict


class TestCase(TypedDict):
    """Structure for permission test cases."""

    command: str
    expected: str  # "allow", "ask", "blocked"
    category: str
    description: str


# Comprehensive test cases based on the updated permissions
TEST_CASES: Dict[str, List[TestCase]] = {
    "allow": [
        # File system operations (safe)
        {
            "command": "ls -la",
            "expected": "allow",
            "category": "filesystem",
            "description": "List directory contents",
        },
        {
            "command": "pwd",
            "expected": "allow",
            "category": "filesystem",
            "description": "Print working directory",
        },
        {
            "command": "cat package.json",
            "expected": "allow",
            "category": "filesystem",
            "description": "Read file contents",
        },
        {
            "command": "find . -name '*.py'",
            "expected": "allow",
            "category": "filesystem",
            "description": "Find files",
        },
        {
            "command": "mkdir new-folder",
            "expected": "allow",
            "category": "filesystem",
            "description": "Create directory",
        },
        # Git operations (safe)
        {
            "command": "git status",
            "expected": "allow",
            "category": "git",
            "description": "Check git status",
        },
        {
            "command": "git diff",
            "expected": "allow",
            "category": "git",
            "description": "Show git diff",
        },
        {
            "command": "git log --oneline",
            "expected": "allow",
            "category": "git",
            "description": "Show git log",
        },
        {
            "command": "git branch",
            "expected": "allow",
            "category": "git",
            "description": "List git branches",
        },
        {
            "command": "git show HEAD",
            "expected": "allow",
            "category": "git",
            "description": "Show git commit",
        },
        {
            "command": "git add .",
            "expected": "allow",
            "category": "git",
            "description": "Stage git changes",
        },
        {
            "command": "git commit -m 'test'",
            "expected": "allow",
            "category": "git",
            "description": "Commit git changes",
        },
        {
            "command": "git push origin main",
            "expected": "allow",
            "category": "git",
            "description": "Push to remote repository",
        },
        # Development tools
        {
            "command": "npm run test",
            "expected": "allow",
            "category": "dev-tools",
            "description": "Run npm test",
        },
        {
            "command": "yarn build",
            "expected": "allow",
            "category": "dev-tools",
            "description": "Build with yarn",
        },
        {
            "command": "pytest tests/",
            "expected": "allow",
            "category": "dev-tools",
            "description": "Run python tests",
        },
        {
            "command": "ruff check .",
            "expected": "allow",
            "category": "dev-tools",
            "description": "Lint python code",
        },
        {
            "command": "go test ./...",
            "expected": "allow",
            "category": "dev-tools",
            "description": "Run go tests",
        },
        # Container operations (safe)
        {
            "command": "docker ps",
            "expected": "allow",
            "category": "docker",
            "description": "List running containers",
        },
        {
            "command": "docker images",
            "expected": "allow",
            "category": "docker",
            "description": "List docker images",
        },
        {
            "command": "docker logs container-name",
            "expected": "allow",
            "category": "docker",
            "description": "Show container logs",
        },
        {
            "command": "docker inspect container",
            "expected": "allow",
            "category": "docker",
            "description": "Inspect container",
        },
        # Kubernetes operations (safe)
        {
            "command": "kubectl get pods",
            "expected": "allow",
            "category": "kubernetes",
            "description": "List kubernetes pods",
        },
        {
            "command": "kubectl describe deployment app",
            "expected": "allow",
            "category": "kubernetes",
            "description": "Describe kubernetes resource",
        },
        {
            "command": "kubectl logs pod-name",
            "expected": "allow",
            "category": "kubernetes",
            "description": "Get pod logs",
        },
        {
            "command": "kubectl top pods",
            "expected": "allow",
            "category": "kubernetes",
            "description": "Show resource usage",
        },
        # Cloud CLI (safe)
        {
            "command": "aws sts get-caller-identity",
            "expected": "allow",
            "category": "cloud",
            "description": "Check AWS identity",
        },
        {
            "command": "gcloud auth list",
            "expected": "allow",
            "category": "cloud",
            "description": "List GCP auth",
        },
    ],
    "ask": [
        # File operations (dangerous)
        {
            "command": "rm -rf temp/",
            "expected": "ask",
            "category": "destructive",
            "description": "Remove directory recursively",
        },
        {
            "command": "rmdir old-folder",
            "expected": "ask",
            "category": "destructive",
            "description": "Remove directory",
        },
        {
            "command": "sudo systemctl restart nginx",
            "expected": "ask",
            "category": "system",
            "description": "Restart system service",
        },
        # Git operations (dangerous)
        {
            "command": "git reset --hard HEAD~1",
            "expected": "ask",
            "category": "git",
            "description": "Hard reset git history",
        },
        {
            "command": "git clean -fd",
            "expected": "ask",
            "category": "git",
            "description": "Clean untracked files",
        },
        # Database operations
        {
            "command": "psql -c 'SELECT * FROM users'",
            "expected": "ask",
            "category": "database",
            "description": "Execute SQL query",
        },
        {
            "command": "mysql -e 'SHOW TABLES'",
            "expected": "ask",
            "category": "database",
            "description": "Execute MySQL query",
        },
        # Container operations (dangerous)
        {
            "command": "docker rm container-name",
            "expected": "ask",
            "category": "docker",
            "description": "Remove docker container",
        },
        {
            "command": "docker system prune",
            "expected": "ask",
            "category": "docker",
            "description": "Clean docker system",
        },
        {
            "command": "docker compose up -d",
            "expected": "ask",
            "category": "docker",
            "description": "Start docker compose",
        },
        # Kubernetes operations (dangerous)
        {
            "command": "kubectl delete pod my-pod",
            "expected": "ask",
            "category": "kubernetes",
            "description": "Delete kubernetes pod",
        },
        {
            "command": "kubectl apply -f deployment.yaml",
            "expected": "ask",
            "category": "kubernetes",
            "description": "Apply kubernetes config",
        },
        {
            "command": "kubectl scale deployment app --replicas=3",
            "expected": "ask",
            "category": "kubernetes",
            "description": "Scale kubernetes deployment",
        },
        # Package management
        {
            "command": "npm install",
            "expected": "ask",
            "category": "package-mgmt",
            "description": "Install npm packages",
        },
        {
            "command": "brew install wget",
            "expected": "ask",
            "category": "package-mgmt",
            "description": "Install system package",
        },
        # System operations
        {
            "command": "systemctl restart docker",
            "expected": "ask",
            "category": "system",
            "description": "Restart system service",
        },
        {
            "command": "killall chrome",
            "expected": "ask",
            "category": "system",
            "description": "Kill all processes",
        },
    ],
}


def get_all_test_cases() -> List[TestCase]:
    """Get all test cases as a flat list."""
    all_cases = []
    for category in TEST_CASES.values():
        all_cases.extend(category)
    return all_cases


def get_test_cases_by_category(category: str) -> List[TestCase]:
    """Get test cases for a specific category."""
    return TEST_CASES.get(category, [])


def get_test_categories() -> List[str]:
    """Get list of available test categories."""
    return list(TEST_CASES.keys())
