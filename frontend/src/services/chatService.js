import { apiRequest, getSessionId } from './api';

export const chatService = {
  async listConversations() {
    const res = await apiRequest('/conversations');
    return res.conversations || [];
  },

  async createConversation(title = 'New Conversation') {
    return apiRequest('/conversations', {
      method: 'POST',
      body: JSON.stringify({ title })
    });
  },

  async getMessages(conversationId) {
    const res = await apiRequest(`/conversations/${conversationId}/messages`);
    return res.messages || [];
  },

  async updateConversation(conversationId, title) {
    return apiRequest(`/conversations/${conversationId}`, {
      method: 'PATCH',
      body: JSON.stringify({ title })
    });
  },

  async deleteConversation(conversationId) {
    return apiRequest(`/conversations/${conversationId}`, {
      method: 'DELETE'
    });
  },

  async clearMessages(conversationId) {
    return apiRequest(`/conversations/${conversationId}/messages`, {
      method: 'DELETE'
    });
  },

  async sendMessageSync(message, conversationId = null) {
    return apiRequest('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        stream: false
      })
    });
  },

  sendMessageStream(message, conversationId, { onInit, onChunk, onDone, onError }) {
    const controller = new AbortController();
    const url = `/api/chat`;

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Id': getSessionId()
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        stream: true
      }),
      signal: controller.signal
    })
      .then(async (response) => {
        if (!response.ok) {
          const text = await response.text();
          throw new Error(`Chat error (${response.status}): ${text}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop(); // keep last incomplete chunk

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('data: ')) {
              try {
                const event = JSON.parse(trimmed.substring(6));
                if (event.type === 'init' && onInit) {
                  onInit(event.conversation_id);
                } else if (event.type === 'chunk' && onChunk) {
                  onChunk(event.content);
                } else if (event.type === 'done' && onDone) {
                  onDone(event);
                }
              } catch (e) {
                console.error('Failed to parse SSE payload:', e);
              }
            }
          }
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError' && onError) {
          onError(err);
        }
      });

    return () => controller.abort();
  }
};
