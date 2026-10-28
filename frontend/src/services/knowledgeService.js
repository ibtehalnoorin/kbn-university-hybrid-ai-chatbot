import { apiRequest } from './api';

export const knowledgeService = {
  async listSources() {
    const res = await apiRequest('/knowledge/sources');
    return res.sources || [];
  },

  async addSource(url, name = null, description = null) {
    return apiRequest('/knowledge/sources', {
      method: 'POST',
      body: JSON.stringify({ url, name, description })
    });
  },

  async refreshSource(sourceId) {
    return apiRequest(`/knowledge/sources/${sourceId}/refresh`, {
      method: 'POST'
    });
  },

  async deleteSource(sourceId) {
    return apiRequest(`/knowledge/sources/${sourceId}`, {
      method: 'DELETE'
    });
  },

  async listJobs() {
    const res = await apiRequest('/knowledge/jobs');
    return res.jobs || [];
  },

  async getJob(jobId) {
    return apiRequest(`/knowledge/jobs/${jobId}`);
  }
};
