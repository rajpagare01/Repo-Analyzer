import React, { useState } from 'react';
import './AIReviewCard.css';

export default function AIReviewCard({ reportId }) {
  const [aiReview, setAiReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const fetchAiReview = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8080/api/repositories/${reportId}/ai-review`);
      if (!response.ok) throw new Error('Failed to fetch AI review');
      const data = await response.json();
      setAiReview(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async () => {
    setDownloading(true);
    try {
      const response = await fetch(`http://localhost:8080/api/repositories/${reportId}/pdf-report`);
      if (!response.ok) throw new Error('Failed to generate PDF');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CodePulse_Report_${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      console.error('PDF Download Error:', err);
      alert('Failed to download PDF report');
    } finally {
      setDownloading(false);
    }
  };

  if (!aiReview && !loading) {
    return (
      <div className="ai-review-card animate-fade-in-up">
        <div className="ai-cta-container">
          <h3>🤖 AI Engineering Review</h3>
          <p>Generate a professional architecture and security review using our local AI Engine.</p>
          <button className="btn-primary" onClick={fetchAiReview}>
            Generate AI Review
          </button>
          {error && <p className="ai-error">{error}</p>}
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="ai-review-card animate-fade-in-up ai-loading">
        <div className="loader"></div>
        <p>Analyzing architecture, metrics, and security posture...</p>
        <p className="loader-subtext">This may take up to 60 seconds.</p>
      </div>
    );
  }

  return (
    <div className="ai-review-card animate-fade-in-up">
      <div className="ai-header">
        <div className="ai-title-group">
          <h3>🤖 AI Engineering Review</h3>
          <div className="ai-grade-badge">
            Grade: <strong>{aiReview.repositoryGrade}</strong>
          </div>
          {aiReview.confidenceScore && (
             <div className="ai-confidence">
               Confidence: {aiReview.confidenceScore}%
             </div>
          )}
        </div>
        <button className="btn-secondary" onClick={downloadPdf} disabled={downloading}>
          {downloading ? 'Generating PDF...' : '📥 Download PDF Report'}
        </button>
      </div>

      <div className="ai-summary">
        <h4>Executive Summary</h4>
        <p>{aiReview.executiveSummary}</p>
      </div>

      <div className="ai-grid">
        <div className="ai-section strengths">
          <h4>✅ Strengths</h4>
          <ul>
            {aiReview.strengths?.map((item, idx) => <li key={idx}>{item}</li>)}
          </ul>
        </div>
        <div className="ai-section weaknesses">
          <h4>⚠️ Weaknesses</h4>
          <ul>
            {aiReview.weaknesses?.map((item, idx) => <li key={idx}>{item}</li>)}
          </ul>
        </div>
      </div>

      {(aiReview.securityRisks?.length > 0 || aiReview.codeQualityRisks?.length > 0) && (
        <div className="ai-grid">
          {aiReview.securityRisks?.length > 0 && (
            <div className="ai-section risks security">
              <h4>🛡️ Security Risks</h4>
              <ul>
                {aiReview.securityRisks.map((risk, idx) => (
                  <li key={idx}>
                    <span className={`risk-badge ${risk.severity?.toLowerCase()}`}>{risk.severity}</span>
                    {risk.issue}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {aiReview.codeQualityRisks?.length > 0 && (
            <div className="ai-section risks quality">
              <h4>📉 Code Quality Risks</h4>
              <ul>
                {aiReview.codeQualityRisks.map((risk, idx) => (
                  <li key={idx}>
                    <span className={`risk-badge ${risk.severity?.toLowerCase()}`}>{risk.severity}</span>
                    {risk.issue}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {aiReview.architectureRecommendations?.length > 0 && (
        <div className="ai-full-section">
          <h4>🏗️ Architecture Recommendations</h4>
          <ul className="arch-recs-list">
             {aiReview.architectureRecommendations.map((rec, idx) => (
               <li key={idx}>💡 {rec}</li>
             ))}
          </ul>
        </div>
      )}

      <div className="ai-full-section">
        <h4>🎯 Actionable Recommendations</h4>
        <ul className="recs-list">
          {aiReview.recommendations?.map((rec, idx) => (
            <li key={idx} className="rec-item">
              <span className={`rec-priority ${rec.priority?.toLowerCase()}`}>{rec.priority} Priority</span>
              <p>{rec.recommendation}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
