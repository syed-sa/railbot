import { API_BASE_URL, ENDPOINTS } from '../utils/constants';
import { storage } from '../utils/storage';

export const chatAPI = {
  async sendMessage(conversationId, message, onToken) {
    const token = storage.getAccessToken();
    const url = `${API_BASE_URL}${ENDPOINTS.CHAT}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const token = line.slice(6);
          if (token && onToken) {
            onToken(token);
          }
        }
      }
    }
  },
};