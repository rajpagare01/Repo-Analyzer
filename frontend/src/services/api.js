const API_BASE_URL = 'http://localhost:8080/api';

/**
 * Submit a GitHub repository for analysis.
 * @param {string} repoUrl
 * @returns {Promise<{id, repoName, owner, status, message}>}
 */
export async function submitRepository(repoUrl) {
  const response = await fetch(`${API_BASE_URL}/repositories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repoUrl }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get the analysis status of a repository.
 * @param {number} id
 * @returns {Promise<{id, repoName, status}>}
 */
export async function getStatus(id) {
  const response = await fetch(`${API_BASE_URL}/repositories/${id}/status`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get the full analysis report for a completed repository.
 * @param {number} id
 * @returns {Promise<ReportResponse>}
 */
export async function getReport(id) {
  const response = await fetch(`${API_BASE_URL}/repositories/${id}/report`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get all submitted repositories.
 * @returns {Promise<Array<{id, repoName, owner, status}>>}
 */
export async function getAllRepositories() {
  const response = await fetch(`${API_BASE_URL}/repositories`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}
