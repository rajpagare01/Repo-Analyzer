"""
Repository Analyzer — orchestrates all analysis checks on a cloned repository using single-pass parallel processing.
"""

import os
from concurrent.futures import ThreadPoolExecutor

from utils.git_utils import clone_repo, cleanup_repo
from analyzer.readme_checker import check_readme
from analyzer.test_checker import check_tests
from analyzer.structure_checker import check_structure
from analyzer.file_analyzer import analyze_single_file


class RepoAnalyzer:
    """Orchestrates repository analysis by cloning, running checks, and aggregating results."""
    
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.repo_dir = None
    
    def analyze(self) -> dict:
        try:
            # Step 1: Clone (shallow clone is used inside)
            self.repo_dir = clone_repo(self.repo_url)
            
            # Step 2: Global checks
            readme_result = check_readme(self.repo_dir)
            test_result = check_tests(self.repo_dir)
            structure_result = check_structure(self.repo_dir)
            
            # Step 3: Single-Pass File Collection
            all_files = []
            for root, dirs, files in os.walk(self.repo_dir):
                # Skip hidden directories and large generated dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'target', 'build', 'dist', 'venv']]
                for f in files:
                    if not f.startswith('.'):
                        all_files.append(os.path.join(root, f))
            
            total_files = len(all_files)
            
            # Step 4: Parallel Processing
            total_lines = 0
            dependency_count = 0
            package_managers = set()
            
            total_complexity = 0
            function_count = 0
            high_complexity_functions = 0
            
            long_methods = 0
            large_classes = 0
            deep_nesting = 0
            
            total_mi = 0.0
            python_file_count = 0
            
            language_counts = {}
            
            # Security
            hardcoded_passwords = 0
            api_keys = 0
            aws_keys = 0
            jwt_secrets = 0
            database_credentials = 0
            dangerous_configs = 0
            sensitive_variables = 0
            private_keys = 0
            security_findings = []
            
            # Use ThreadPoolExecutor for fast I/O and process parallelization
            workers = min(32, os.cpu_count() + 4 if os.cpu_count() else 8)
            with ThreadPoolExecutor(max_workers=workers) as executor:
                for metrics in executor.map(analyze_single_file, all_files):
                    total_lines += metrics['lines']
                    dependency_count += metrics['dependency_count']
                    if metrics['package_manager']:
                        package_managers.add(metrics['package_manager'])
                        
                    total_complexity += metrics['complexity']
                    function_count += metrics['function_count']
                    high_complexity_functions += metrics['high_complexity_functions']
                    
                    long_methods += metrics['long_methods']
                    large_classes += metrics['large_classes']
                    deep_nesting += metrics['deep_nesting']
                    
                    if metrics['is_python'] and metrics['mi'] > 0:
                        total_mi += metrics['mi']
                        python_file_count += 1
                        
                    if metrics['language']:
                        lang = metrics['language']
                        language_counts[lang] = language_counts.get(lang, 0) + 1
                        
                    # Aggregate security
                    hardcoded_passwords += metrics['hardcodedPasswords']
                    api_keys += metrics['apiKeys']
                    aws_keys += metrics['awsKeys']
                    jwt_secrets += metrics['jwtSecrets']
                    database_credentials += metrics['databaseCredentials']
                    dangerous_configs += metrics['dangerousConfigs']
                    sensitive_variables += metrics['sensitiveVariables']
                    private_keys += metrics['privateKeys']
                    if metrics['findings']:
                        security_findings.extend(metrics['findings'])

            # Format languages
            languages = dict(sorted(language_counts.items(), key=lambda x: x[1], reverse=True))
            
            # Step 5: Compute Scores
            readme_score = readme_result['score']
            testing_score = test_result['score']
            structure_score = structure_result['score']
            overall_score = round((readme_score + testing_score + structure_score) / 3, 2)
            
            # Complexity score
            average_complexity = round(total_complexity / function_count, 1) if function_count > 0 else 1.0
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
                
            # Maintainability score
            if python_file_count > 0:
                maintainability_index = round(total_mi / python_file_count, 1)
            else:
                maintainability_index = max(0.0, min(100.0, 100.0 - (average_complexity * 2)))
            maintainability_score = int(maintainability_index)
            
            # Quality Score Formula: (Complexity * 0.4) + (Maintainability * 0.4) + (Structure * 0.2)
            quality_score = int(round((complexity_score * 0.4) + (maintainability_score * 0.4) + (structure_score * 0.2)))
            
            # Security Score
            security_score = 100
            security_score -= (hardcoded_passwords * 10)
            security_score -= (api_keys * 15)
            security_score -= (aws_keys * 20)
            security_score -= (jwt_secrets * 10)
            security_score -= (database_credentials * 10)
            security_score -= (dangerous_configs * 5)
            security_score -= (sensitive_variables * 2)
            security_score -= (private_keys * 25)
            
            security_score = max(0, security_score)
            
            if security_score >= 90:
                risk_level = "LOW"
            elif security_score >= 70:
                risk_level = "MEDIUM"
            elif security_score >= 50:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"
            
            import json
            
            # Step 6: Build response
            result = {
                'readmeScore': readme_score,
                'testingScore': testing_score,
                'structureScore': structure_score,
                'overallScore': overall_score,
                'totalFiles': total_files,
                'totalLines': total_lines,
                'languages': languages,
                
                'averageComplexity': average_complexity,
                'highComplexityFunctions': high_complexity_functions,
                'complexityScore': complexity_score,
                
                'maintainabilityIndex': maintainability_index,
                'maintainabilityScore': maintainability_score,
                
                'dependencyCount': dependency_count,
                'packageManager': ", ".join(package_managers) if package_managers else "Unknown",
                
                'longMethods': long_methods,
                'largeClasses': large_classes,
                'deepNesting': deep_nesting,
                
                'qualityScore': quality_score,
                
                'securityScore': security_score,
                'hardcodedPasswords': hardcoded_passwords,
                'apiKeys': api_keys,
                'awsKeys': aws_keys,
                'jwtSecrets': jwt_secrets,
                'databaseCredentials': database_credentials,
                'dangerousConfigs': dangerous_configs,
                'sensitiveVariables': sensitive_variables,
                'privateKeys': private_keys,
                'riskLevel': risk_level,
                'securityFindings': json.dumps({"securityIssues": security_findings}) if security_findings else None,
                'vulnerableDependencies': None, # Placeholder
                
                'details': {
                    'readme': readme_result,
                    'testing': test_result,
                    'structure': structure_result,
                },
            }
            
            return result
            
        finally:
            if self.repo_dir:
                cleanup_repo(self.repo_dir)
