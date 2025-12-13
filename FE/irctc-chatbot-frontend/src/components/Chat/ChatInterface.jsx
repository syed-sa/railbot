import React, { useEffect, useState } from 'react';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';
import { WELCOME_MESSAGE } from '../../utils/constants';

export const ChatInterface = () => {
  // Generates a unique, stable conversation ID for the duration of this component's life
  const [conversationId] = useState(
    () => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );
  
  // Use the chat hook to manage state and actions
  const { messages, isTyping, sendMessage, setMessages } = useChat(conversationId);

  // Initialize the conversation with a welcome message only once on mount
  useEffect(() => {
    // Note: The useChat hook might already initialize messages. 
    // This is safe if the hook doesn't set an initial state.
    setMessages([{ role: 'assistant', content: WELCOME_MESSAGE }]);
  }, [setMessages]);

  return (
    // 1. Main container for the entire chat interface
    <div className="chat-interface-container flex flex-col h-full bg-white shadow-xl rounded-lg">
      
      {/* 2. Header component */}
      <ChatHeader />
      
      {/* 3. Messages display area (takes up most of the space) */}
      <div className="messages-area flex-grow overflow-hidden">
        <ChatMessages messages={messages} isTyping={isTyping} />
      </div>

      {/* 4. Input component (sends the message via the hook) */}
      <ChatInput sendMessage={sendMessage} />
      
    </div>
  );
};