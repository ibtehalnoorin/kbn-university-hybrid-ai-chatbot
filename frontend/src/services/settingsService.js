import { apiRequest } from './api';

export const settingsService = {
  async getHealth() {
    return apiRequest('/health');
  },

  async getLlmStatus() {
    return apiRequest('/llm/status');
  },

  async getModels() {
    return apiRequest('/models');
  }
};
