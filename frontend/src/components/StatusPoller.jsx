import { useEffect, useState } from 'react';
import './StatusPoller.css';

const STEPS = [
  { key: 'PENDING', label: 'Queued', icon: '📋' },
  { key: 'ANALYZING', label: 'Analyzing repository...', icon: '🔍' },
  { key: 'COMPLETED', label: 'Report ready!', icon: '✅' },
];

/**
 * Animated status display while analysis runs.
 * @param {{ status: string, repoName: string }} props
 */
export default function StatusPoller({ status, repoName }) {
  const [dots, setDots] = useState('');

  useEffect(() => {
    if (status === 'COMPLETED' || status === 'FAILED') return;
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);
    return () => clearInterval(interval);
  }, [status]);

  const currentStepIdx = STEPS.findIndex((s) => s.key === status);

  return (
    <div className="status-poller">
      <div className="status-poller-header">
        <div className="status-poller-pulse" />
        <h3 className="status-poller-title">
          {status === 'FAILED' ? 'Analysis Failed' : `Analyzing ${repoName}`}
        </h3>
      </div>

      {status === 'FAILED' ? (
        <p className="status-poller-error">
          Something went wrong during analysis. Please try again.
        </p>
      ) : (
        <div className="status-steps">
          {STEPS.map((step, idx) => {
            const isActive = idx === currentStepIdx;
            const isDone = idx < currentStepIdx;
            return (
              <div
                key={step.key}
                className={`status-step ${isDone ? 'step-done' : ''} ${isActive ? 'step-active' : ''}`}
              >
                <span className="step-icon">{step.icon}</span>
                <span className="step-label">
                  {step.label}
                  {isActive && status !== 'COMPLETED' && dots}
                </span>
                {isDone && <span className="step-check">✓</span>}
              </div>
            );
          })}
        </div>
      )}

      {status !== 'COMPLETED' && status !== 'FAILED' && (
        <div className="status-shimmer-bar">
          <div className="status-shimmer-fill" />
        </div>
      )}
    </div>
  );
}
