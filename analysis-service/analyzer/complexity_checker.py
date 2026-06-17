import os
import radon.complexity as cc
from radon.metrics import mi_visit
from radon.visitors import ComplexityVisitor
import lizard

def check_complexity(repo_dir: str) -> dict:
    """
    Computes average cyclomatic complexity, count of high complexity functions,
    and a maintainability index for the repository.
    """
    total_complexity = 0
    function_count = 0
    high_complexity_functions = 0
    
    total_mi = 0
    python_file_count = 0
    
    for root, dirs, files in os.walk(repo_dir):
        # Skip .git and generated dirs
        if '.git' in root or 'node_modules' in root or 'venv' in root or 'target' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            try:
                # Use Lizard for multi-language complexity
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                analysis = lizard.analyze_file(file_path)
                
                for func in analysis.function_list:
                    function_count += 1
                    total_complexity += func.cyclomatic_complexity
                    if func.cyclomatic_complexity > 15:
                        high_complexity_functions += 1
                        
                # Use Radon for Maintainability Index (only Python)
                if file.endswith('.py'):
                    try:
                        mi = mi_visit(content, multi=True)
                        total_mi += mi
                        python_file_count += 1
                    except Exception:
                        pass
                        
            except Exception:
                pass # Skip binaries or unreadable files

    average_complexity = round(total_complexity / function_count, 1) if function_count > 0 else 1.0
    
    # Calculate Complexity Score
    if average_complexity <= 5:
        complexity_score = 100
    elif average_complexity <= 10:
        complexity_score = 80
    elif average_complexity <= 15:
        complexity_score = 60
    elif average_complexity <= 20:
        complexity_score = 40
    else:
        complexity_score = 20

    # Calculate Maintainability Score
    if python_file_count > 0:
        maintainability_index = round(total_mi / python_file_count, 1)
    else:
        # Fallback if no Python files - derive a rough MI from complexity
        maintainability_index = max(0.0, min(100.0, 100.0 - (average_complexity * 2)))

    maintainability_score = int(maintainability_index)

    return {
        "averageComplexity": average_complexity,
        "highComplexityFunctions": high_complexity_functions,
        "complexityScore": complexity_score,
        "maintainabilityIndex": maintainability_index,
        "maintainabilityScore": maintainability_score
    }
