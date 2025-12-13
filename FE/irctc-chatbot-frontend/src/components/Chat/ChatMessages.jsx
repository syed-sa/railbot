import React, { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';

export const ChatMessages = ({ messages, isTyping }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    // Optional chaining ensures we only call scrollIntoView if messagesEndRef.current exists
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // Scrolls to the bottom whenever the 'messages' array changes
    scrollToBottom();
  }, [messages]);

  return (
    // 1. Root container for the messages list
    <div className="chat-messages-container overflow-y-auto p-4 flex flex-col">
      {/* 2. Map through messages and render a MessageBubble for each */}
      {messages.map((msg, idx) => (
        <MessageBubble 
          key={idx} // Using index as key is acceptable here if messages are not reordered/deleted
          message={msg}
        />
      ))}
      
      {/* 3. Typing indicator logic (conditionally renders a 'typing...' bubble) */}
      {isTyping && (
        <div className="flex justify-start mb-4">
          <div className="message-bubble assistant-message bg-gray-200 text-gray-800 rounded-xl p-3 max-w-xs shadow-md">
            {/* Simple three-dot typing animation can be implemented here */}
            <span>Typing...</span>
          </div>
        </div>
      )}
      
      {/* 4. The empty div that the auto-scroller targets */}
      <div ref={messagesEndRef} />
    </div>
  );
};