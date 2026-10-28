import { apiRequest } from './api';

export const memoryService = {
  async getMemories() {
    return apiRequest('/memories');
  },

  async addMemory(key, value, category = 'preference') {
    return apiRequest('/memories', {
      method: 'POST',
      body: JSON.stringify({ key, value, category })
    });
  },

  async updateMemory(memoryId, { key, value, category }) {
    return apiRequest(`/memories/${memoryId}`, {
      method: 'PATCH',
      body: JSON.stringify({ key, value, category })
    });
  },

  async deleteMemory(memoryId) {
    return apiRequest(`/memories/${memoryId}`, {
      method: 'DELETE'
    });
  },

  async clearAll() {
    return apiRequest('/memories', {
      method: 'DELETE'
    });
  },

  async getSettings() {
    return apiRequest('/memories/settings');
  },

  async toggleMemory(enabled) {
    return apiRequest('/memories/settings', {
      method: 'POST',
      body: JSON.stringify({ enabled })
    });
  }
};
