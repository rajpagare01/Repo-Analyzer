import { useState } from 'react';
import './RepoForm.css';

/**
 * Repository submission form with URL validation.
 * @param {{ onSubmit: (url: string) => void, loading: boolean }} props
 */
export default function RepoForm({ onSubmit, loading }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const githubPattern = /^https?:\/\/github\.com\/[\w.\-]+\/[\w.\-]+\/?$/;

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = url.trim();

    if (!trimmed) {
      setError('Please enter a repository URL');
      return;
    }

    if (!githubPattern.test(trimmed)) {
      setError('Please enter a valid GitHub URL (e.g., https://github.com/owner/repo)');
      return;
    }

    setError('');
    onSubmit(trimmed);
  };

  return (
    <form className="repo-form" onSubmit={handleSubmit}>
      <div className="repo-form-header">
        <h2 className="repo-form-title">Analyze a Repository</h2>
        <p className="repo-form-description">
          Enter a public GitHub repository URL to get a comprehensive quality report
        </p>
      </div>

      <div className="repo-form-input-group">
        <div className="repo-form-input-wrapper">
          <svg className="repo-form-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
          </svg>
          <input
            id="repo-url-input"
            type="text"
            className={`repo-form-input ${error ? 'input-error' : ''}`}
            placeholder="https://github.com/owner/repository"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setError(''); }}
            disabled={loading}
            autoComplete="off"
          />
        </div>
        {error && <p className="repo-form-error">{error}</p>}
      </div>

      <button
        id="submit-repo-btn"
        type="submit"
        className="repo-form-button"
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="button-spinner" />
            Submitting...
          </>
        ) : (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            Analyze Repository
          </>
        )}
      </button>
    </form>
  );
}
