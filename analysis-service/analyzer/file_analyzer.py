import os
import re
from pathlib import Path
import lizard
from radon.metrics import mi_visit
from utils.git_utils import BINARY_EXTENSIONS, LANGUAGE_EXTENSIONS
from analyzer.security_checker import scan_for_secrets

# Dependency regex patterns
MAVEN_DEP_PATTERN = re.compile(r'<dependency>')
GO_DEP_PATTERN = re.compile(r'^\s*[\w\.\-/]+\s+v[\d\.]+')

def analyze_single_file(file_path: str) -> dict:
    """
    Performs a single-pass analysis on a file.
    Returns a dictionary of metrics for this specific file.
    """
    metrics = {
        'lines': 0,
        'language': None,
        'dependency_count': 0,
        'package_manager': None,
        'complexity': 0,
        'function_count': 0,
        'high_complexity_functions': 0,
        'mi': 0.0,
        'is_python': False,
        'long_methods': 0,
        'large_classes': 0,
        'deep_nesting': 0,
        'is_source_code': False,
        
        # Security metrics
        'hardcodedPasswords': 0,
        'apiKeys': 0,
        'awsKeys': 0,
        'jwtSecrets': 0,
        'databaseCredentials': 0,
        'dangerousConfigs': 0,
        'sensitiveVariables': 0,
        'privateKeys': 0,
        'findings': []
    }
    
    file_name = os.path.basename(file_path)
    ext = Path(file_path).suffix.lower()
    
    if ext in BINARY_EXTENSIONS:
        return metrics

    if ext in LANGUAGE_EXTENSIONS:
        metrics['language'] = LANGUAGE_EXTENSIONS[ext]
        metrics['is_source_code'] = True
        if metrics['language'] == 'Python':
            metrics['is_python'] = True

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return metrics

    # Scan for secrets (Security Analytics)
    security_results = scan_for_secrets(file_name, content)
    for key in ['hardcodedPasswords', 'apiKeys', 'awsKeys', 'jwtSecrets', 
                'databaseCredentials', 'dangerousConfigs', 'sensitiveVariables', 'privateKeys']:
        metrics[key] = security_results[key]
    metrics['findings'] = security_results['findings']

    # Count lines
    lines = content.splitlines()
    metrics['lines'] = len(lines)

    # Dependency Checking
    if file_name == 'pom.xml':
        metrics['package_manager'] = "Maven"
        metrics['dependency_count'] = len(MAVEN_DEP_PATTERN.findall(content))
    elif file_name == 'package.json':
        metrics['package_manager'] = "NPM"
        try:
            import json
            data = json.loads(content)
            deps = data.get('dependencies', {})
            dev_deps = data.get('devDependencies', {})
            metrics['dependency_count'] = len(deps) + len(dev_deps)
        except Exception:
            pass
    elif file_name == 'requirements.txt':
        metrics['package_manager'] = "Pip"
        metrics['dependency_count'] = len([line for line in lines if line.strip() and not line.startswith('#')])
    elif file_name == 'build.gradle':
        metrics['package_manager'] = "Gradle"
        metrics['dependency_count'] = content.count('implementation ') + content.count('testImplementation ')
    elif file_name == 'go.mod':
        metrics['package_manager'] = "Go Modules"
        metrics['dependency_count'] = len(GO_DEP_PATTERN.findall(content))
    elif file_name == 'Cargo.toml':
        metrics['package_manager'] = "Cargo"
        in_deps = False
        for line in lines:
            line = line.strip()
            if line.startswith('[dependencies]'):
                in_deps = True
            elif line.startswith('[') and in_deps:
                in_deps = False
            elif in_deps and '=' in line:
                metrics['dependency_count'] += 1

    # Source Code Analysis (Complexity & Smells)
    if metrics['is_source_code']:
        try:
            # Lizard single pass
            analysis = lizard.analyze_file.analyze_source_code(file_name, content)
            
            for func in analysis.function_list:
                metrics['function_count'] += 1
                metrics['complexity'] += func.cyclomatic_complexity
                if func.cyclomatic_complexity > 15:
                    metrics['high_complexity_functions'] += 1
                if func.end_line - func.start_line > 50:
                    metrics['long_methods'] += 1
        except Exception:
            pass

        # Large Classes Heuristic (files > 500 lines)
        if metrics['lines'] > 500:
            metrics['large_classes'] = 1

        # Deep Nesting Heuristic
        current_nesting = 0
        max_nesting = 0
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith(('//', '#', '/*')):
                continue
                
            if metrics['is_python']:
                indent = len(line) - len(line.lstrip())
                nesting = indent // 4
                if nesting > max_nesting:
                    max_nesting = nesting
            else:
                current_nesting += line.count('{')
                current_nesting -= line.count('}')
                if current_nesting > max_nesting:
                    max_nesting = current_nesting
                    
        if max_nesting > 4:
            metrics['deep_nesting'] = 1

        # Maintainability Index (Radon)
        if metrics['is_python']:
            try:
                metrics['mi'] = mi_visit(content, multi=True)
            except Exception:
                pass

    return metrics
