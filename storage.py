"""Small filesystem helpers shared by runtime persistence code."""

from pathlib import Path


def ensure_directory(directory_path):
    """Create a directory and its parents when they do not exist."""
    directory = Path(directory_path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent_directory(file_path):
    """Create the parent directory for a file path and return the path."""
    path = Path(file_path)
    ensure_directory(path.parent)
    return path
