"""Configuration loader for ai-reviewer"""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Load configuration from files.
    
    Searches for .ai-reviewer.yaml in current dir and home dir.
    
    Returns:
        Configuration dictionary with defaults merged.
    """
    config = {
        "ignore": [
            "__pycache__", ".git", "node_modules", 
            ".venv", "venv", "dist", "build"
        ],
        "languages": {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".jsx": "javascript", ".tsx": "typescript", ".sql": "sql",
            ".go": "go", ".java": "java", ".rs": "rust",
            ".c": "c", ".cpp": "cpp", ".h": "c", ".hpp": "cpp"
        },
        "max_file_size_mb": 10,
        "threads": 4,
    }
    
    config_paths = [
        Path(".ai-reviewer.yaml"),
        Path(".ai-reviewer.yml"),
        Path.home() / ".ai-reviewer.yaml",
        Path.home() / ".ai-reviewer.yml",
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    if user_config and isinstance(user_config, dict):
                        config.update(user_config)
                break
            except (yaml.YAMLError, OSError, UnicodeDecodeError):
                continue
    
    return config
