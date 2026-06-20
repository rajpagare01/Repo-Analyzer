import React, { useState, useEffect, useRef } from 'react';
import './AIReviewCard.css';

export default function AIReviewCard({ reportId, initialStatus, initialFailureReason, initialTime }) {
  const [aiReview, setAiReview] = useState(null);
  const [status, setStatus] = useState(initialStatus || 'NOT_STARTED');
  const [failureReason, setFailureReason] = useState(initialFailureReason);
  const [generationTime, setGenerationTime] = useState(initialTime);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const pollingRef = useRef(null);

  useEffect(() => {
    if (status === 'GENERATING') {
      startPolling();
    } else if (status === 'COMPLETED' && !aiReview) {
      fetchCompletedReview();
    } else if (status === 'FAILED' && failureReason) {
      setError(`Generation failed: ${failureReason}`);
    }

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [status]); // Only run when status changes or on mount

  const startAiReview = async () => {
    setStatus('GENERATING');
    setError(null);
    setFailureReason(null);
    
    try {
      const response = await fetch(`http://localhost:8080/api/repositories/${reportId}/ai-review`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to start AI review generation');
      startPolling();
    } catch (err) {
      setError(err.message);
      setStatus('FAILED');
    }
  };

  const startPolling = () => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    
    pollingRef.current = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8080/api/repositories/${reportId}/ai-review/status`);
        if (!response.ok) throw new Error('Failed to fetch status');
        const data = await response.json();
        
        if (data.status === 'COMPLETED') {
          clearInterval(pollingRef.current);
          setStatus('COMPLETED');
          setGenerationTime(data.generationTimeSeconds);
          fetchCompletedReview();
        } else if (data.status === 'FAILED') {
          clearInterval(pollingRef.current);
          setStatus('FAILED');
          setFailureReason(data.failureReason);
          setError(`Generation failed: ${data.failureReason || 'Unknown error'}`);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 5000);
  };

  const fetchCompletedReview = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/repositories/${reportId}/ai-review`);
      if (!response.ok) throw new Error('Failed to fetch completed AI review');
      const data = await response.json();
      setAiReview(data);
    } catch (err) {
      setError(err.message);
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

  if ((status === 'NOT_STARTED' || status === 'FAILED') && !aiReview) {
    return (
      <div className="ai-review-card animate-fade-in-up">
        <div className="ai-cta-container">
          <h3>🤖 AI Engineering Review</h3>
          <p>Generate a professional architecture and security review using our local AI Engine.</p>
          <button className="btn-primary" onClick={startAiReview}>
            Generate AI Review
          </button>
          {error && <p className="ai-error" style={{marginTop: '1rem', color: 'var(--score-low)'}}>{error}</p>}
        </div>
      </div>
    );
  }

  if (status === 'GENERATING' || (status === 'COMPLETED' && !aiReview)) {
    return (
      <div className="ai-review-card animate-fade-in-up ai-loading">
        <div className="loader"></div>
        <div className="loading-ux">
          <h3 style={{marginBottom: '1rem'}}>Generating AI Review...</h3>
          <ul style={{listStyle: 'none', padding: 0, textAlign: 'left', display: 'inline-block', marginBottom: '1.5rem'}}>
            <li style={{color: 'var(--score-high)', marginBottom: '0.5rem'}}>✓ Repository metrics collected</li>
            <li style={{color: 'var(--score-high)', marginBottom: '0.5rem'}}>✓ Security analysis completed</li>
            <li style={{color: 'var(--primary-color)'}}>⏳ AI reviewing repository</li>
          </ul>
          <p className="loader-subtext" style={{opacity: 0.8}}>This may take several minutes for local models.</p>
          <p className="loader-subtext" style={{fontWeight: 'bold'}}>You can safely leave this page.</p>
        </div>
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
          {generationTime && (
            <div className="ai-confidence" style={{backgroundColor: 'var(--surface-color)', color: 'var(--text-muted)'}}>
              Generated in {generationTime} seconds
            </div>
          )}
        </div>
        <button className="btn-secondary" onClick={downloadPdf} disabled={downloading}>
          {downloading ? 'Generating PDF...' : '📥 Download PDF Report'}
        </button>
      </div>

      {aiReview.provider === 'ollama_fallback' && (
        <div className="ai-fallback-warning" style={{ backgroundColor: 'rgba(211, 47, 47, 0.1)', color: '#d32f2f', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', fontWeight: '500', border: '1px solid rgba(211, 47, 47, 0.3)' }}>
          ⚠️ Gemini API failed to respond. This review was generated using the local Ollama fallback.
        </div>
      )}

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
