"""
Structure checker — evaluates repository organization using 6 criteria.

Scoring (100 points total):
    1. Has README          → 17 points
    2. Has LICENSE          → 17 points
    3. Has .gitignore       → 17 points
    4. Has tests            → 17 points
    5. Has CI/CD config     → 16 points
    6. Has dependency file  → 16 points
"""

import os
from pathlib import Path


# LICENSE file patterns (case-insensitive)
LICENSE_PATTERNS = {
    'license', 'licence', 'license.md', 'licence.md',
    'license.txt', 'licence.txt', 'copying', 'copying.md',
    'copying.txt', 'license.rst', 'licence.rst',
    'license-mit', 'license-apache',
}

# CI/CD configuration files and directories
CI_CD_PATTERNS = {
    'dirs': ['.github/workflows', '.gitlab', '.circleci'],
    'files': [
        '.gitlab-ci.yml', 'Jenkinsfile', '.travis.yml',
        'azure-pipelines.yml', 'bitbucket-pipelines.yml',
        '.drone.yml', 'cloudbuild.yaml', 'cloudbuild.yml',
        'appveyor.yml', '.appveyor.yml',
        'Taskfile.yml', 'Taskfile.yaml',
    ],
}

# Dependency / build files
DEPENDENCY_FILES = {
    # Python
    'requirements.txt', 'setup.py', 'setup.cfg', 'pyproject.toml', 'Pipfile',
    'poetry.lock', 'conda.yaml', 'environment.yml',
    # JavaScript / TypeScript
    'package.json', 'yarn.lock', 'pnpm-lock.yaml',
    # Java / Kotlin / Scala
    'pom.xml', 'build.gradle', 'build.gradle.kts', 'build.sbt',
    # Go
    'go.mod', 'go.sum',
    # Rust
    'Cargo.toml', 'Cargo.lock',
    # Ruby
    'Gemfile', 'Gemfile.lock',
    # PHP
    'composer.json', 'composer.lock',
    # C# / .NET
    '.csproj', '.sln', 'packages.config', 'Directory.Build.props',
    # C / C++
    'CMakeLists.txt', 'Makefile', 'makefile', 'meson.build', 'conanfile.txt',
    # Dart / Flutter
    'pubspec.yaml',
    # Elixir
    'mix.exs',
    # Swift
    'Package.swift',
    # Haskell
    'stack.yaml', 'cabal.project',
}

# Test directory names
TEST_DIRECTORIES = {
    'test', 'tests', '__tests__', 'spec', 'specs',
    'test_suite', 'testing', 'unittest', 'unittests',
    'integration_tests', 'e2e', 'cypress',
}

# Test file patterns
TEST_FILE_PATTERNS = [
    '_test.py', '_test.go', '_test.rb', '_test.rs',
    'test_',
    'Test.java', 'Tests.java',
    '.test.js', '.test.ts', '.test.jsx', '.test.tsx',
    '.spec.js', '.spec.ts', '.spec.jsx', '.spec.tsx',
]


def check_structure(repo_dir: str) -> dict:
    """
    Evaluate repository structure using 6 criteria.
    
    Returns:
        dict with 'score' (0-100), 'breakdown' (dict of criteria -> points), 
        and 'details' (dict of criteria -> found items)
    """
    breakdown = {}
    details = {}
    
    root_files = os.listdir(repo_dir)
    root_files_lower = {f.lower(): f for f in root_files}
    
    # 1. Has README (17 points)
    has_readme = any(
        f.startswith('readme') for f in root_files_lower
    )
    breakdown['hasReadme'] = 17 if has_readme else 0
    details['readme'] = has_readme
    
    # 2. Has LICENSE (17 points)
    has_license = any(
        f in LICENSE_PATTERNS for f in root_files_lower
    )
    breakdown['hasLicense'] = 17 if has_license else 0
    details['license'] = has_license
    
    # 3. Has .gitignore (17 points)
    has_gitignore = '.gitignore' in root_files
    breakdown['hasGitignore'] = 17 if has_gitignore else 0
    details['gitignore'] = has_gitignore
    
    # 4. Has tests (17 points)
    has_tests = _check_has_tests(repo_dir)
    breakdown['hasTests'] = 17 if has_tests else 0
    details['tests'] = has_tests
    
    # 5. Has CI/CD (16 points)
    ci_cd_found = _check_ci_cd(repo_dir, root_files)
    has_ci_cd = len(ci_cd_found) > 0
    breakdown['hasCiCd'] = 16 if has_ci_cd else 0
    details['ciCd'] = ci_cd_found if ci_cd_found else False
    
    # 6. Has dependency file (16 points)
    dep_files_found = _check_dependency_files(repo_dir)
    has_deps = len(dep_files_found) > 0
    breakdown['hasDependencyFile'] = 16 if has_deps else 0
    details['dependencyFiles'] = dep_files_found if dep_files_found else False
    
    total_score = sum(breakdown.values())
    
    return {
        'score': total_score,
        'breakdown': breakdown,
        'details': details,
    }


def _check_has_tests(repo_dir: str) -> bool:
    """Check for test directories or test files."""
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for d in dirs:
            if d.lower() in TEST_DIRECTORIES:
                return True
        
        for f in files:
            for pattern in TEST_FILE_PATTERNS:
                if f.endswith(pattern) or f.startswith(pattern):
                    return True
    return False


def _check_ci_cd(repo_dir: str, root_files: list) -> list:
    """Check for CI/CD configuration files and directories."""
    found = []
    
    # Check directories
    for ci_dir in CI_CD_PATTERNS['dirs']:
        full_path = os.path.join(repo_dir, ci_dir)
        if os.path.isdir(full_path):
            found.append(ci_dir)
    
    # Check files
    for ci_file in CI_CD_PATTERNS['files']:
        if ci_file in root_files:
            found.append(ci_file)
    
    return found


def _check_dependency_files(repo_dir: str) -> list:
    """Check for dependency/build files in repo root and first-level dirs."""
    found = []
    root_files = set(os.listdir(repo_dir))
    
    for dep_file in DEPENDENCY_FILES:
        if dep_file in root_files:
            found.append(dep_file)
    
    # Also check for .csproj / .sln files that might have varying names
    for f in root_files:
        f_lower = f.lower()
        if f_lower.endswith('.csproj') or f_lower.endswith('.sln'):
            if f not in found:
                found.append(f)
    
    return found
