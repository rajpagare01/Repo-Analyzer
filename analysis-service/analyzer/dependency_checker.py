import os
import re

def check_dependencies(repo_dir: str) -> dict:
    dependency_count = 0
    package_manager = "Unknown"
    
    # Simple regex to count lines with dependencies
    maven_dep_pattern = re.compile(r'<dependency>')
    npm_dep_pattern = re.compile(r'"[^"]+"\s*:\s*"[^"]+"')
    req_dep_pattern = re.compile(r'^[\w\-]+([=><~]+.*)?$')
    go_dep_pattern = re.compile(r'^\s*[\w\.\-/]+\s+v[\d\.]+')
    
    for root, dirs, files in os.walk(repo_dir):
        if '.git' in root or 'node_modules' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            if file == 'pom.xml':
                if package_manager == "Unknown": package_manager = "Maven"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        dependency_count += len(maven_dep_pattern.findall(f.read()))
                except: pass
                
            elif file == 'package.json':
                if package_manager == "Unknown": package_manager = "NPM"
                try:
                    import json
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        deps = data.get('dependencies', {})
                        dev_deps = data.get('devDependencies', {})
                        dependency_count += len(deps) + len(dev_deps)
                except: pass
                
            elif file == 'requirements.txt':
                if package_manager == "Unknown": package_manager = "Pip"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                        dependency_count += len(lines)
                except: pass
                
            elif file == 'build.gradle':
                if package_manager == "Unknown": package_manager = "Gradle"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # rough estimation for gradle
                        dependency_count += f.read().count('implementation ') + f.read().count('testImplementation ')
                except: pass
                
            elif file == 'go.mod':
                if package_manager == "Unknown": package_manager = "Go Modules"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        dependency_count += len(go_dep_pattern.findall(f.read()))
                except: pass
                
            elif file == 'Cargo.toml':
                if package_manager == "Unknown": package_manager = "Cargo"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        in_deps = False
                        for line in f:
                            line = line.strip()
                            if line.startswith('[dependencies]'):
                                in_deps = True
                            elif line.startswith('[') and in_deps:
                                in_deps = False
                            elif in_deps and '=' in line:
                                dependency_count += 1
                except: pass

    return {
        "dependencyCount": dependency_count,
        "packageManager": package_manager
    }
