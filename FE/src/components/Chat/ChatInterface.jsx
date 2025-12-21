import React, { useState } from "react";
import { ChatHeader } from "./ChatHeader";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { useChat } from "../../hooks/useChat";

const QUICK_OPTIONS = [
  "PNR Status",
  "Live Train Status",
  "Seat Availability",
  "Fare information",
  "Trains between stations",
];

export const ChatInterface = () => {
  const [conversationId] = useState(
    () => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );

  const { messages, isTyping, sendMessage } = useChat(conversationId);

  const handleQuickOptionClick = (option) => {
    sendMessage(option);
  };

  return (
    <div className="chat-interface-container flex flex-col h-screen bg-white shadow-xl rounded-lg">
      <ChatHeader />

      {/* Messages */}
      <div className="messages-area flex-grow overflow-hidden">
        <ChatMessages messages={messages} isTyping={isTyping} />
      </div>

      {/* Quick buttons */}
      {messages.length === 0 && (
        <div className="quick-options flex flex-wrap gap-2 p-3 border-t bg-gray-50">
          {QUICK_OPTIONS.map((option) => (
            <button
              key={option}
              onClick={() => handleQuickOptionClick(option)}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
            >
              {option}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <ChatInput onSendMessage={sendMessage} />
    </div>
  );
};
