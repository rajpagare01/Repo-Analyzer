"""
README checker — detects the presence and quality of README files.
"""

import os
from pathlib import Path


# Common README filenames (case-insensitive matching)
README_PATTERNS = [
    'readme.md',
    'readme.rst',
    'readme.txt',
    'readme',
    'readme.adoc',
    'readme.rdoc',
    'readme.org',
]


def check_readme(repo_dir: str) -> dict:
    """
    Check if a README file exists in the repository root.
    
    Returns:
        dict with 'score' (0 or 100), 'exists' (bool), and 'filename' (str or None)
    """
    root_files = os.listdir(repo_dir)
    root_files_lower = {f.lower(): f for f in root_files}
    
    for pattern in README_PATTERNS:
        if pattern in root_files_lower:
            actual_filename = root_files_lower[pattern]
            filepath = os.path.join(repo_dir, actual_filename)
            
            # Check file size — a nearly empty README is barely useful
            file_size = os.path.getsize(filepath) if os.path.isfile(filepath) else 0
            
            return {
                'score': 100,
                'exists': True,
                'filename': actual_filename,
                'fileSize': file_size,
            }
    
    return {
        'score': 0,
        'exists': False,
        'filename': None,
        'fileSize': 0,
    }
