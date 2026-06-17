import { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import RepoForm from './components/RepoForm';
import StatusPoller from './components/StatusPoller';
import ReportCard from './components/ReportCard';
import { submitRepository, getStatus, getReport } from './services/api';
import './App.css';

/**
 * CodePulse AI — Main Application
 * 
 * Flow: idle → submitting → polling → report (or error)
 */
export default function App() {
  const [view, setView] = useState('form'); // form | polling | report | error
  const [loading, setLoading] = useState(false);
  const [repoId, setRepoId] = useState(null);
  const [repoName, setRepoName] = useState('');
  const [status, setStatus] = useState('');
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const pollingRef = useRef(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const handleSubmit = async (url) => {
    setLoading(true);
    setError('');

    try {
      const data = await submitRepository(url);
      setRepoId(data.id);
      setRepoName(data.repoName || url.split('/').pop());
      setStatus('PENDING');
      setView('polling');
      startPolling(data.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startPolling = (id) => {
    // Clear any existing polling
    if (pollingRef.current) clearInterval(pollingRef.current);

    pollingRef.current = setInterval(async () => {
      try {
        const statusData = await getStatus(id);
        setStatus(statusData.status);

        if (statusData.status === 'COMPLETED') {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
          // Fetch the full report
          const reportData = await getReport(id);
          setReport(reportData);
          setView('report');
        } else if (statusData.status === 'FAILED') {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 3000);
  };

  const handleReset = () => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    setView('form');
    setRepoId(null);
    setRepoName('');
    setStatus('');
    setReport(null);
    setError('');
  };

  return (
    <div className="app">
      <Header />
      <main className="app-main">
        <div className="app-container">
          {view === 'form' && (
            <>
              <RepoForm onSubmit={handleSubmit} loading={loading} />
              {error && (
                <div className="app-error animate-fade-in">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                  {error}
                </div>
              )}
            </>
          )}

          {view === 'polling' && (
            <StatusPoller status={status} repoName={repoName} />
          )}

          {view === 'report' && report && (
            <ReportCard report={report} onReset={handleReset} />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>CodePulse AI · Repository Quality Analyzer · Phase 1 MVP</p>
      </footer>
    </div>
  );
}
