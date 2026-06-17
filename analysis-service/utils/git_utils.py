"""
Git utility functions for cloning repositories and extracting metrics.
"""

import os
import tempfile
import shutil
from pathlib import Path
from git import Repo, GitCommandError


# File extensions mapped to language names
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.java': 'Java',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.jsx': 'JavaScript',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.c': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.h': 'C',
    '.hpp': 'C++',
    '.cs': 'C#',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.r': 'R',
    '.R': 'R',
    '.m': 'Objective-C',
    '.dart': 'Dart',
    '.lua': 'Lua',
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.pl': 'Perl',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'SASS',
    '.less': 'LESS',
    '.sql': 'SQL',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.json': 'JSON',
    '.xml': 'XML',
    '.md': 'Markdown',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    '.erl': 'Erlang',
    '.hs': 'Haskell',
    '.clj': 'Clojure',
}

# Binary file extensions to skip when counting lines
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
    '.zip', '.tar', '.gz', '.bz2', '.rar', '.7z',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.exe', '.dll', '.so', '.dylib', '.o', '.a',
    '.class', '.jar', '.war', '.ear',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.pyc', '.pyo', '.obj', '.bin',
    '.db', '.sqlite', '.sqlite3',
    '.lock',
}


def clone_repo(repo_url: str) -> str:
    """
    Clone a repository to a temporary directory using shallow clone (depth=1).
    Returns the path to the cloned repo directory.
    """
    temp_dir = tempfile.mkdtemp(prefix='codepulse_')
    try:
        Repo.clone_from(
            repo_url,
            temp_dir,
            depth=1,
            single_branch=True
        )
        return temp_dir
    except GitCommandError as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to clone repository: {str(e)}")
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Unexpected error cloning repository: {str(e)}")


def cleanup_repo(repo_dir: str) -> None:
    """Remove the cloned repository directory."""
    if repo_dir and os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, ignore_errors=True)


def _is_hidden(path: str) -> bool:
    """Check if any component of the path is a hidden directory/file."""
    parts = Path(path).parts
    return any(part.startswith('.') for part in parts)


def count_files(repo_dir: str) -> int:
    """Count all non-hidden, non-binary files in the repository."""
    count = 0
    for root, dirs, files in os.walk(repo_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if not f.startswith('.'):
                count += 1
    return count


def count_lines(repo_dir: str) -> int:
    """Count total lines of code, skipping binary files."""
    total_lines = 0
    for root, dirs, files in os.walk(repo_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.startswith('.'):
                continue
            filepath = os.path.join(root, f)
            ext = Path(f).suffix.lower()
            if ext in BINARY_EXTENSIONS:
                continue
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                    total_lines += sum(1 for _ in fh)
            except (OSError, IOError):
                continue
    return total_lines


def detect_languages(repo_dir: str) -> dict:
    """
    Detect programming languages by file extension.
    Returns a dict of language -> file count.
    """
    language_counts = {}
    for root, dirs, files in os.walk(repo_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in LANGUAGE_EXTENSIONS:
                lang = LANGUAGE_EXTENSIONS[ext]
                language_counts[lang] = language_counts.get(lang, 0) + 1
    
    # Sort by count descending
    sorted_langs = dict(
        sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    )
    return sorted_langs
