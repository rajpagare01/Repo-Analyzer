import ScoreGauge from './ScoreGauge';
import './ReportCard.css';

/**
 * Full analysis report card with scores, metrics, and GitHub metadata.
 * @param {{ report: ReportResponse, onReset: () => void }} props
 */
export default function ReportCard({ report, onReset }) {
  const {
    repoName, owner, readmeScore, testingScore, structureScore,
    overallScore, totalFiles, totalLines, languages,
    stars, forks, openIssues, defaultBranch, lastCommitDate, description,
    averageComplexity, highComplexityFunctions, complexityScore,
    maintainabilityIndex, maintainabilityScore,
    dependencyCount, packageManager,
    longMethods, largeClasses, deepNesting,
    qualityScore,
    securityScore, hardcodedPasswords, apiKeys, awsKeys, jwtSecrets,
    databaseCredentials, dangerousConfigs, sensitiveVariables, privateKeys,
    riskLevel, securityFindings, vulnerableDependencies
  } = report;

  const getGrade = (score) => {
    if (score >= 90) return { letter: 'A+', color: 'var(--score-high)' };
    if (score >= 80) return { letter: 'A', color: 'var(--score-high)' };
    if (score >= 70) return { letter: 'B', color: 'var(--score-medium)' };
    if (score >= 60) return { letter: 'C', color: 'var(--score-medium)' };
    if (score >= 50) return { letter: 'D', color: 'var(--score-low)' };
    return { letter: 'F', color: 'var(--score-low)' };
  };

  const grade = getGrade(qualityScore || overallScore);

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return '#10b981'; // Green
      case 'MEDIUM': return '#f59e0b'; // Yellow
      case 'HIGH': return '#f97316'; // Orange
      case 'CRITICAL': return '#ef4444'; // Red
      default: return 'var(--text-muted)';
    }
  };

  let parsedFindings = [];
  if (securityFindings) {
    try {
      const parsed = JSON.parse(securityFindings);
      parsedFindings = parsed.securityIssues || [];
    } catch (e) {
      console.error("Failed to parse securityFindings");
    }
  }

  const topLanguages = languages
    ? Object.entries(languages).slice(0, 6)
    : [];

  const totalLangFiles = topLanguages.reduce((sum, [, count]) => sum + count, 0);

  const formatNumber = (n) => {
    if (n == null) return '—';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
    return n.toString();
  };

  return (
    <div className="report-card animate-fade-in-up">
      {/* Header */}
      <div className="report-header">
        <div className="report-header-info">
          <div className="report-repo-badge">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
            </svg>
            <span>{owner} / <strong>{repoName}</strong></span>
          </div>
          {description && <p className="report-description">{description}</p>}
        </div>
        <div className="report-grade" style={{ borderColor: grade.color }}>
          <span className="report-grade-letter" style={{ color: grade.color }}>{grade.letter}</span>
          <span className="report-grade-label">Grade</span>
        </div>
      </div>

      {/* GitHub Metadata */}
      {(stars != null || forks != null) && (
        <div className="report-meta-strip">
          <div className="meta-item">
            <span className="meta-icon">⭐</span>
            <span className="meta-value">{formatNumber(stars)}</span>
            <span className="meta-label">Stars</span>
          </div>
          <div className="meta-item">
            <span className="meta-icon">🍴</span>
            <span className="meta-value">{formatNumber(forks)}</span>
            <span className="meta-label">Forks</span>
          </div>
          <div className="meta-item">
            <span className="meta-icon">🐛</span>
            <span className="meta-value">{formatNumber(openIssues)}</span>
            <span className="meta-label">Issues</span>
          </div>
          <div className="meta-item">
            <span className="meta-icon">🌿</span>
            <span className="meta-value">{defaultBranch || 'main'}</span>
            <span className="meta-label">Branch</span>
          </div>
          {lastCommitDate && (
            <div className="meta-item">
              <span className="meta-icon">📅</span>
              <span className="meta-value">{new Date(lastCommitDate).toLocaleDateString()}</span>
              <span className="meta-label">Last Commit</span>
            </div>
          )}
        </div>
      )}

      {/* Score Gauges */}
      <div className="report-scores">
        <div className="report-overall">
          <ScoreGauge score={qualityScore || overallScore} label="Health Score" size={150} />
        </div>
        <div className="report-individual-scores">
          <ScoreGauge score={complexityScore || 0} label="Complexity" size={100} />
          <ScoreGauge score={maintainabilityScore || 0} label="Maintainability" size={100} />
          <ScoreGauge score={structureScore || 0} label="Structure" size={100} />
          <ScoreGauge score={readmeScore || 0} label="README" size={100} />
          <ScoreGauge score={testingScore || 0} label="Testing" size={100} />
        </div>
      </div>

      {/* Code Smells & Dependencies Sections */}
      <div className="report-details-grid">
        <div className="details-section">
          <h4 className="report-section-title">Code Smells</h4>
          <div className="details-card-group">
            <div className="metric-card smell-card">
              <span className="metric-value">{longMethods || 0}</span>
              <span className="metric-label">Long Methods</span>
            </div>
            <div className="metric-card smell-card">
              <span className="metric-value">{largeClasses || 0}</span>
              <span className="metric-label">Large Classes</span>
            </div>
            <div className="metric-card smell-card">
              <span className="metric-value">{deepNesting || 0}</span>
              <span className="metric-label">Deep Nesting</span>
            </div>
            <div className="metric-card smell-card">
              <span className="metric-value">{highComplexityFunctions || 0}</span>
              <span className="metric-label">Complex Functions</span>
            </div>
          </div>
        </div>
        
        <div className="details-section">
          <h4 className="report-section-title">Repository Details</h4>
          <div className="details-card-group">
            <div className="metric-card">
              <span className="metric-value">{averageComplexity != null ? averageComplexity.toFixed(1) : '—'}</span>
              <span className="metric-label">Avg Complexity</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{maintainabilityIndex != null ? maintainabilityIndex.toFixed(1) : '—'}</span>
              <span className="metric-label">Maintainability Index</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{formatNumber(dependencyCount)}</span>
              <span className="metric-label">Dependencies</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{packageManager || 'None'}</span>
              <span className="metric-label">Package Mgr</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Analytics Section */}
      {securityScore !== undefined && (
        <div className="report-security-section">
          <div className="security-header">
            <h3 className="security-title">Security Analytics</h3>
          </div>
          
          <div className="security-grid">
            <div className="security-overview">
              <div className="security-score-container">
                <ScoreGauge score={securityScore} label="Security Score" size={120} />
              </div>
              <div className="risk-level-container" style={{ borderColor: getRiskColor(riskLevel) }}>
                <span className="risk-label">Risk Level</span>
                <span className="risk-value" style={{ color: getRiskColor(riskLevel) }}>{riskLevel}</span>
              </div>
            </div>

            <div className="security-issues">
              <h4 className="report-section-title">Detected Issues</h4>
              <ul className="issues-list">
                <li className={awsKeys > 0 ? "issue-item danger" : "issue-item safe"}>
                  <span className="issue-icon">{awsKeys > 0 ? '⚠' : '✓'}</span>
                  {awsKeys > 0 ? `${awsKeys} AWS Keys` : 'No AWS Keys'}
                </li>
                <li className={apiKeys > 0 ? "issue-item danger" : "issue-item safe"}>
                  <span className="issue-icon">{apiKeys > 0 ? '⚠' : '✓'}</span>
                  {apiKeys > 0 ? `${apiKeys} API Keys` : 'No API Keys'}
                </li>
                <li className={jwtSecrets > 0 ? "issue-item danger" : "issue-item safe"}>
                  <span className="issue-icon">{jwtSecrets > 0 ? '⚠' : '✓'}</span>
                  {jwtSecrets > 0 ? `${jwtSecrets} JWT Secrets` : 'No JWT Secrets'}
                </li>
                <li className={databaseCredentials > 0 ? "issue-item danger" : "issue-item safe"}>
                  <span className="issue-icon">{databaseCredentials > 0 ? '⚠' : '✓'}</span>
                  {databaseCredentials > 0 ? `${databaseCredentials} DB Credentials` : 'No Database Credentials'}
                </li>
                <li className={privateKeys > 0 ? "issue-item danger" : "issue-item safe"}>
                  <span className="issue-icon">{privateKeys > 0 ? '⚠' : '✓'}</span>
                  {privateKeys > 0 ? `${privateKeys} Private Keys` : 'No Private Keys'}
                </li>
                <li className={hardcodedPasswords > 0 ? "issue-item danger" : "issue-item safe"}>
                  <span className="issue-icon">{hardcodedPasswords > 0 ? '⚠' : '✓'}</span>
                  {hardcodedPasswords > 0 ? `${hardcodedPasswords} Hardcoded Passwords` : 'No Hardcoded Passwords'}
                </li>
                <li className={dangerousConfigs > 0 ? "issue-item warning" : "issue-item safe"}>
                  <span className="issue-icon">{dangerousConfigs > 0 ? '⚠' : '✓'}</span>
                  {dangerousConfigs > 0 ? `${dangerousConfigs} Dangerous Configs` : 'No Dangerous Configs'}
                </li>
                <li className={sensitiveVariables > 0 ? "issue-item warning" : "issue-item safe"}>
                  <span className="issue-icon">{sensitiveVariables > 0 ? '⚠' : '✓'}</span>
                  {sensitiveVariables > 0 ? `${sensitiveVariables} Sensitive Env Vars` : 'No Sensitive Env Vars'}
                </li>
                {vulnerableDependencies !== null && vulnerableDependencies !== undefined && (
                  <li className={vulnerableDependencies > 0 ? "issue-item danger" : "issue-item safe"}>
                    <span className="issue-icon">{vulnerableDependencies > 0 ? '⚠' : '✓'}</span>
                    {vulnerableDependencies > 0 ? `${vulnerableDependencies} Vulnerable Dependencies` : 'No Vulnerable Dependencies'}
                  </li>
                )}
              </ul>
            </div>
            
            {parsedFindings.length > 0 && (
              <div className="security-findings">
                <h4 className="report-section-title">Findings Details</h4>
                <div className="findings-table-container">
                  <table className="findings-table">
                    <thead>
                      <tr>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>File</th>
                      </tr>
                    </thead>
                    <tbody>
                      {parsedFindings.map((finding, idx) => (
                        <tr key={idx}>
                          <td>
                            <span className={`severity-badge ${finding.severity.toLowerCase()}`}>
                              {finding.severity}
                            </span>
                          </td>
                          <td>{finding.type}</td>
                          <td className="finding-file">{finding.file}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Basic Metrics */}
      <div className="report-metrics">
        <div className="metric-card">
          <span className="metric-value">{formatNumber(totalFiles)}</span>
          <span className="metric-label">Total Files</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{formatNumber(totalLines)}</span>
          <span className="metric-label">Lines of Code</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{topLanguages.length}</span>
          <span className="metric-label">Languages</span>
        </div>
      </div>

      {/* Languages */}
      {topLanguages.length > 0 && (
        <div className="report-languages">
          <h4 className="report-section-title">Languages</h4>
          <div className="language-bar">
            {topLanguages.map(([lang, count]) => {
              const pct = ((count / totalLangFiles) * 100).toFixed(1);
              return (
                <div
                  key={lang}
                  className="language-segment"
                  style={{ width: `${pct}%` }}
                  title={`${lang}: ${count} files (${pct}%)`}
                />
              );
            })}
          </div>
          <div className="language-legend">
            {topLanguages.map(([lang, count]) => (
              <div key={lang} className="language-item">
                <span className="language-dot" />
                <span className="language-name">{lang}</span>
                <span className="language-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="report-actions">
        <button id="analyze-another-btn" className="btn-secondary" onClick={onReset}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          Analyze Another
        </button>
      </div>
    </div>
  );
}
