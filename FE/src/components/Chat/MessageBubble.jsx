import React from "react";
import ReactMarkdown from "react-markdown";
// Common classes for a clean chat bubble design are assumed
export const MessageBubble = ({ message }) => {
  // Check if the message is from the 'user'
  const isUser = message.role === "user";

  // Define CSS classes dynamically based on the sender (user or assistant)
const bubbleClasses = `
              rounded-xl p-3 max-w-xs break-words shadow-md

          ${
            isUser
              ? "bg-indigo-600 text-white rounded-br-md"
              : "bg-slate-100 text-slate-800 rounded-bl-md"
          }
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
      <div className="flex items-end gap-2">
  {!isUser && (
    <div className="w-8 h-8 rounded-full bg-indigo-500 text-white flex items-center justify-center text-sm font-semibold">
      AI
    </div>
  )}
  <div className={bubbleClasses}>
        <ReactMarkdown>{message.content.replace(/\\n/g, "\n")}</ReactMarkdown>
      </div>
</div>
      
    </div>
  );
};
