import json
from .llm_factory import LLMFactory

PROMPT_TEMPLATE = """
You are a Principal Software Architect and Staff Security Engineer conducting a repository engineering review.

You have received the following static analysis metrics for a repository:
{metrics_json}

Your task is to generate a professional, objective, and deeply technical AI engineering review.
You must output ONLY valid JSON using the exact schema below. Do not include markdown code blocks around the JSON.

SCHEMA REQUIREMENTS:
{{
  "repositoryGrade": "A+ | A | B | C | D | F", 
  "confidenceScore": 0-100, // Based on available data quality
  "executiveSummary": "150 words max. Professional tone. Highlight key strengths and critical risks.",
  "strengths": ["list of strings"],
  "weaknesses": ["list of strings"],
  "securityRisks": [
    {{ "severity": "LOW|MEDIUM|HIGH|CRITICAL", "issue": "string description" }}
  ],
  "codeQualityRisks": [
    {{ "severity": "LOW|MEDIUM|HIGH|CRITICAL", "issue": "string description" }}
  ],
  "architectureRecommendations": ["list of structural/architectural recommendations"],
  "recommendations": [
    {{ "priority": "LOW|MEDIUM|HIGH|CRITICAL", "recommendation": "string actionable advice" }}
  ]
}}

Grading Rules:
- 95+ average -> A+
- 90+ average -> A
- 80+ average -> B
- 70+ average -> C
- 60+ average -> D
- Below 60 -> F
(Penalize grade heavily if critical security risks exist)

Ensure your response is highly actionable and reflects Senior Staff Engineer level insight.
"""

def generate_ai_review(metrics: dict) -> dict:
    """
    Takes a dictionary of static analysis metrics, formats the prompt,
    calls the active LLM provider, and parses the JSON result.
    """
    provider = LLMFactory.get_provider()
    
    prompt = PROMPT_TEMPLATE.format(metrics_json=json.dumps(metrics, indent=2))
    
    print(f"[AI Review Engine] Calling LLM via {provider.__class__.__name__}...")
    raw_response = provider.generate_review(prompt)
    
    try:
        # Some LLMs might wrap output in markdown blocks despite instructions
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        review_data = json.loads(clean_json)
        return review_data
    except json.JSONDecodeError as e:
        print(f"[AI Review Engine] Failed to parse JSON: {str(e)}\nRaw Response: {raw_response}")
        return {
            "repositoryGrade": "N/A",
            "confidenceScore": 0,
            "executiveSummary": "Failed to generate AI review due to LLM parsing error.",
            "strengths": [],
            "weaknesses": [],
            "securityRisks": [],
            "codeQualityRisks": [],
            "architectureRecommendations": [],
            "recommendations": []
        }
