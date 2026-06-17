"""
CodePulse AI — Analysis Service

Flask application that provides repository analysis endpoints.
Clones GitHub repositories and computes quality metrics.
"""

import logging
import re
from flask import Flask, request, jsonify, send_file
from analyzer.repo_analyzer import RepoAnalyzer
from ai_review.review_engine import generate_ai_review
from ai_review.report_generator import generate_pdf_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('codepulse-analysis')

app = Flask(__name__)

# GitHub URL validation pattern
GITHUB_URL_PATTERN = re.compile(
    r'^https?://github\.com/[\w.\-]+/[\w.\-]+(?:\.git)?/?$'
)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'UP',
        'service': 'codepulse-analysis-service',
    }), 200


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze a GitHub repository.
    
    Request Body:
        { "repoUrl": "https://github.com/owner/repo" }
    
    Response:
        {
            "readmeScore": 100,
            "testingScore": 80,
            "structureScore": 90,
            "overallScore": 90.0,
            "totalFiles": 150,
            "totalLines": 12000,
            "languages": {"Python": 80, "JavaScript": 30},
            "details": { ... }
        }
    """
    # Validate request
    if not request.is_json:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Content-Type must be application/json',
        }), 400
    
    data = request.get_json()
    repo_url = data.get('repoUrl', '').strip()
    
    if not repo_url:
        return jsonify({
            'error': 'Bad Request',
            'message': 'repoUrl is required',
        }), 400
    
    if not GITHUB_URL_PATTERN.match(repo_url):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid GitHub repository URL format. Expected: https://github.com/owner/repo',
        }), 400
    
    # Ensure the URL ends with .git for cloning
    clone_url = repo_url.rstrip('/')
    if not clone_url.endswith('.git'):
        clone_url += '.git'
    
    logger.info(f"Starting analysis for: {repo_url}")
    
    try:
        analyzer = RepoAnalyzer(clone_url)
        result = analyzer.analyze()
        
        logger.info(
            f"Analysis complete for {repo_url} — "
            f"Overall: {result['overallScore']}, "
            f"Files: {result['totalFiles']}, "
            f"Lines: {result['totalLines']}"
        )
        
        return jsonify(result), 200
        
    except RuntimeError as e:
        logger.error(f"Analysis failed for {repo_url}: {str(e)}")
        return jsonify({
            'error': 'Analysis Failed',
            'message': str(e),
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error analyzing {repo_url}: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred during analysis.',
        }), 500

@app.route('/api/v1/ai-review', methods=['POST'])
def ai_review():
    """
    Generate an AI review based on static analysis metrics.
    """
    if not request.is_json:
        return jsonify({'error': 'Bad Request'}), 400
        
    metrics = request.get_json()
    logger.info("Generating AI review...")
    
    try:
        review_data = generate_ai_review(metrics)
        return jsonify(review_data), 200
    except Exception as e:
        logger.error(f"AI review generation failed: {str(e)}")
        return jsonify({'error': 'AI Review Failed', 'message': str(e)}), 500

@app.route('/api/v1/pdf-report', methods=['POST'])
def pdf_report():
    """
    Generate a PDF report from metrics and AI review.
    """
    if not request.is_json:
        return jsonify({'error': 'Bad Request'}), 400
        
    data = request.get_json()
    metrics = data.get('metrics', {})
    review = data.get('review', {})
    
    logger.info("Generating PDF report...")
    
    try:
        pdf_path = generate_pdf_report(metrics, review)
        return send_file(pdf_path, as_attachment=True, download_name='CodePulse_Report.pdf', mimetype='application/pdf')
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        return jsonify({'error': 'PDF Generation Failed', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
