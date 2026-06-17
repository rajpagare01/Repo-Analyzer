"""
Repository Analyzer — orchestrates all analysis checks on a cloned repository.
"""

from utils.git_utils import clone_repo, cleanup_repo, count_files, count_lines, detect_languages
from analyzer.readme_checker import check_readme
from analyzer.test_checker import check_tests
from analyzer.structure_checker import check_structure


class RepoAnalyzer:
    """Orchestrates repository analysis by cloning, running checks, and aggregating results."""
    
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.repo_dir = None
    
    def analyze(self) -> dict:
        """
        Full analysis pipeline:
        1. Clone the repository (shallow)
        2. Run all checkers
        3. Compute overall score
        4. Cleanup cloned files
        5. Return aggregated results
        """
        try:
            # Step 1: Clone
            self.repo_dir = clone_repo(self.repo_url)
            
            # Step 2: Run checkers
            readme_result = check_readme(self.repo_dir)
            test_result = check_tests(self.repo_dir)
            structure_result = check_structure(self.repo_dir)
            
            # Step 3: Collect metrics
            total_files = count_files(self.repo_dir)
            total_lines = count_lines(self.repo_dir)
            languages = detect_languages(self.repo_dir)
            
            # Step 4: Compute overall score
            readme_score = readme_result['score']
            testing_score = test_result['score']
            structure_score = structure_result['score']
            overall_score = round((readme_score + testing_score + structure_score) / 3, 2)
            
            # Step 5: Build response
            result = {
                'readmeScore': readme_score,
                'testingScore': testing_score,
                'structureScore': structure_score,
                'overallScore': overall_score,
                'totalFiles': total_files,
                'totalLines': total_lines,
                'languages': languages,
                'details': {
                    'readme': readme_result,
                    'testing': test_result,
                    'structure': structure_result,
                },
            }
            
            return result
            
        finally:
            # Always cleanup cloned repo
            if self.repo_dir:
                cleanup_repo(self.repo_dir)
