"""
Test checker — detects the presence of test directories and test files.
"""

import os
from pathlib import Path


# Common test directory names
TEST_DIRECTORIES = {
    'test', 'tests', '__tests__', 'spec', 'specs',
    'test_suite', 'testing', 'unittest', 'unittests',
    'integration_tests', 'e2e', 'cypress',
}

# Test file patterns (checked as substrings or suffixes)
TEST_FILE_PATTERNS = [
    '_test.py', '_test.go', '_test.rb', '_test.rs',
    'test_.py',
    'Test.java', 'Tests.java', 'Test.kt', 'Test.scala',
    '.test.js', '.test.ts', '.test.jsx', '.test.tsx',
    '.spec.js', '.spec.ts', '.spec.jsx', '.spec.tsx',
    '_spec.rb',
    'Test.cs', 'Tests.cs',
    '_test.dart',
    'test.php', 'Test.php',
]


def check_tests(repo_dir: str) -> dict:
    """
    Check if the repository contains test directories or test files.
    
    Returns:
        dict with 'score' (0 or 100), 'hasTestDir' (bool), 
        'hasTestFiles' (bool), 'testDirs' (list), 'testFileCount' (int)
    """
    found_test_dirs = []
    test_file_count = 0
    
    for root, dirs, files in os.walk(repo_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # Check for test directories
        for d in dirs:
            if d.lower() in TEST_DIRECTORIES:
                rel_path = os.path.relpath(os.path.join(root, d), repo_dir)
                found_test_dirs.append(rel_path)
        
        # Check for test files
        for f in files:
            for pattern in TEST_FILE_PATTERNS:
                if f.endswith(pattern):
                    test_file_count += 1
                    break
    
    has_test_dir = len(found_test_dirs) > 0
    has_test_files = test_file_count > 0
    has_tests = has_test_dir or has_test_files
    
    return {
        'score': 100 if has_tests else 0,
        'hasTestDir': has_test_dir,
        'hasTestFiles': has_test_files,
        'testDirs': found_test_dirs,
        'testFileCount': test_file_count,
    }
