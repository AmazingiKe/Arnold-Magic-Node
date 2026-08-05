"""Small filesystem helpers shared by runtime persistence code."""

import json
import os
import tempfile
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


def load_json(file_path):
    """Load a UTF-8 JSON file."""
    with Path(file_path).open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def save_json(file_path, data):
    """Atomically save JSON data without hiding unsupported values."""
    path = ensure_parent_directory(file_path)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(path.parent),
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(
                data,
                temporary_file,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(str(temporary_path), str(path))
    except Exception:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except OSError:
                pass
        raise

    return path
