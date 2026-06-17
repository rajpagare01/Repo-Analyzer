from fpdf import FPDF
import json
import os

def generate_pdf_report(metrics: dict, review: dict) -> str:
    """
    Generates a PDF report summarizing the repository static metrics and the AI review.
    Returns the absolute file path to the generated PDF.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, "CodePulse AI - Engineering Review Report", ln=True, align='C')
    pdf.ln(5)
    
    # Executive Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Executive Summary", ln=True)
    pdf.set_font("Arial", '', 11)
    
    exec_summary = review.get("executiveSummary", "No summary available.")
    pdf.multi_cell(0, 8, exec_summary)
    pdf.ln(5)
    
    # Grades & Confidence
    pdf.set_font("Arial", 'B', 12)
    grade = review.get("repositoryGrade", "N/A")
    conf = review.get("confidenceScore", 0)
    pdf.cell(0, 10, f"Repository Grade: {grade} (AI Confidence: {conf}%)", ln=True)
    pdf.ln(5)
    
    # Key Metrics
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Static Analysis Metrics", ln=True)
    pdf.set_font("Arial", '', 11)
    for k, v in metrics.items():
        if isinstance(v, (int, float, str)):
            pdf.cell(0, 8, f"{k}: {v}", ln=True)
    pdf.ln(5)
    
    # Strengths
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Strengths", ln=True)
    pdf.set_font("Arial", '', 11)
    for strength in review.get("strengths", []):
        pdf.cell(0, 8, f"- {strength}", ln=True)
    pdf.ln(5)
    
    # Security Risks
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Security Risks", ln=True)
    pdf.set_font("Arial", '', 11)
    sec_risks = review.get("securityRisks", [])
    if not sec_risks:
        pdf.cell(0, 8, "No security risks detected by AI.", ln=True)
    else:
        for risk in sec_risks:
            sev = risk.get('severity', 'UNKNOWN')
            iss = risk.get('issue', '')
            pdf.multi_cell(0, 8, f"[{sev}] {iss}")
    pdf.ln(5)
    
    # Recommendations
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Actionable Recommendations", ln=True)
    pdf.set_font("Arial", '', 11)
    recs = review.get("recommendations", [])
    if not recs:
        pdf.cell(0, 8, "No recommendations.", ln=True)
    else:
        for rec in recs:
            pri = rec.get('priority', 'INFO')
            text = rec.get('recommendation', '')
            pdf.multi_cell(0, 8, f"[{pri}] {text}")
            
    # Save PDF
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "CodePulse_Report.pdf")
    pdf.output(file_path)
    
    return file_path
