import os
import lizard

def check_smells(repo_dir: str) -> dict:
    long_methods = 0
    large_classes = 0
    deep_nesting = 0
    
    for root, dirs, files in os.walk(repo_dir):
        if '.git' in root or 'node_modules' in root or 'venv' in root or 'target' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            try:
                # Use Lizard for Long Methods
                analysis = lizard.analyze_file(file_path)
                
                for func in analysis.function_list:
                    # length = end_line - start_line
                    if func.end_line - func.start_line > 50:
                        long_methods += 1
                        
                # Use heuristics for Large Classes and Deep Nesting
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Large Classes: Very rough heuristic. Just checking if file is > 500 lines for now
                # Or count 'class ' blocks
                if len(lines) > 500:
                    large_classes += 1
                
                # Deep Nesting heuristic: count max leading spaces or braces
                is_python = file.endswith('.py')
                current_nesting = 0
                max_nesting_in_file = 0
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith(('//', '#', '/*')):
                        continue
                        
                    if is_python:
                        # Python: count leading spaces / 4
                        indent = len(line) - len(line.lstrip())
                        nesting = indent // 4
                        if nesting > max_nesting_in_file:
                            max_nesting_in_file = nesting
                    else:
                        # C/Java/JS: count { and }
                        current_nesting += line.count('{')
                        current_nesting -= line.count('}')
                        if current_nesting > max_nesting_in_file:
                            max_nesting_in_file = current_nesting
                            
                if max_nesting_in_file > 4:
                    deep_nesting += 1

            except Exception:
                pass

    return {
        "longMethods": long_methods,
        "largeClasses": large_classes,
        "deepNesting": deep_nesting
    }
