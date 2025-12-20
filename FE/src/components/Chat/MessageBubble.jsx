import React from 'react';

// Common classes for a clean chat bubble design are assumed
export const MessageBubble = ({ message }) => {
  // Check if the message is from the 'user'
  const isUser = message.role === 'user';

  // Define CSS classes dynamically based on the sender (user or assistant)
  const bubbleClasses = `
    message-bubble 
    ${isUser ? 'user-message bg-blue-500 text-white' : 'assistant-message bg-gray-200 text-gray-800'}
    rounded-xl p-3 max-w-xs break-words shadow-md
  `;

  // Define alignment classes for the containing wrapper
  const wrapperClasses = `
    flex 
    mb-4 
    ${isUser ? 'justify-end' : 'justify-start'}
  `;

  return (
    // 1. Outer div to handle alignment (left for assistant, right for user)
    <div className={wrapperClasses}>
      {/* 2. Inner div for the actual styled message bubble */}
      <div className={bubbleClasses}>
        {/* 3. Render the message content */}
        {message.content}
      </div>
    </div>
  );
};