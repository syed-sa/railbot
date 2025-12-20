import { useState, useCallback } from 'react';
import { chatAPI } from '../api/chat';

export const useChat = (conversationId) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const addMessage = useCallback((role, content) => {
    setMessages(prev => [...prev, { role, content }]);
  }, []);

  const updateLastMessage = useCallback((content) => {
    setMessages(prev => {
      const newMessages = [...prev];
      if (newMessages.length > 0) {
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          content,
        };
      }
      return newMessages;
    });
  }, []);

  const sendMessage = useCallback(async (message) => {
    if (!message.trim() || isTyping) return;

    addMessage('user', message);
    setIsTyping(true);

    let assistantMessage = '';
    addMessage('assistant', '');

    try {
      await chatAPI.sendMessage(conversationId, message, (token) => {
        assistantMessage += token;
        updateLastMessage(assistantMessage);
      });
    } catch (error) {
      console.error('Error sending message:', error);
      updateLastMessage('❌ Sorry, I encountered an error. Please try again.');
    } finally {
      setIsTyping(false);
    }
  }, [conversationId, isTyping, addMessage, updateLastMessage]);

  return {
    messages,
    isTyping,
    sendMessage,
    setMessages,
  };
};