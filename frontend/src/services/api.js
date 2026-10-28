const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export function getSessionId() {
  let sessionId = localStorage.getItem('kbn_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
    localStorage.setItem('kbn_session_id', sessionId);
  }
  return sessionId;
}

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    'X-Session-Id': getSessionId(),
    ...(options.headers || {})
  };

  const response = await fetch(url, {
    ...options,
    headers
  });

  const returnedSession = response.headers.get('X-Session-Id');
  if (returnedSession) {
    localStorage.setItem('kbn_session_id', returnedSession);
  }

  if (!response.ok) {
    let errMessage = `HTTP error ${response.status}`;
    try {
      const errData = await response.json();
      if (errData && errData.error) {
        errMessage = errData.error;
      }
    } catch (_) {}
    throw new Error(errMessage);
  }

  return response.json();
}
