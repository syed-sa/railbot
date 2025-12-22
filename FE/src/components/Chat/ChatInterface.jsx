import React, { useState } from "react";
import { ChatHeader } from "./ChatHeader";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { useChat } from "../../hooks/useChat";

const QUICK_OPTIONS = [
  "PNR Status",
  "Live Train Status",
  "Seat Availability",
  "Fare Information",
  "Trains Between Stations",
];

export const ChatInterface = () => {
  const [conversationId] = useState(
    () => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );

  const { messages, isTyping, sendMessage } = useChat(conversationId);
  const [selectedOption, setSelectedOption] = useState(null);

  const handleQuickOptionClick = (option) => {
    setSelectedOption(option);
    sendMessage(option);
  };

  return (
    <div className="chat-interface-container flex flex-col h-screen bg-white shadow-xl rounded-lg">
      <ChatHeader />

      {/* Messages Area */}
      <div className="flex-grow overflow-y-auto px-4 py-3 space-y-3">
        
        {/* Bot Greeting */}
        {messages.length === 0 && (
          <div className="max-w-[75%] bg-gray-100 text-gray-800 px-4 py-2.5 rounded-2xl">
            How can I help you today?
          </div>
        )}

        {/* Quick Options (Image-style placement) */}
        {messages.length === 0 && (
          <div className="flex flex-wrap gap-3 max-w-[85%]">
            {QUICK_OPTIONS.map((option) => {
              const isSelected = selectedOption === option;

              return (
                <button
                  key={option}
                  onClick={() => handleQuickOptionClick(option)}
                  className={`
                    px-5 py-2.5 rounded-full text-sm font-medium
                    transition-all duration-200
                    ${
                      isSelected
                        ? "bg-gradient-to-r from-purple-500 to-indigo-500 text-white shadow-md"
                        : "border border-purple-400 text-purple-600 hover:bg-purple-50"
                    }
                  `}
                >
                  {option}
                </button>
              );
            })}
          </div>
        )}

        {/* Actual Chat Messages */}
        <ChatMessages messages={messages} isTyping={isTyping} />
      </div>

      {/* Input */}
      <ChatInput onSendMessage={sendMessage} />
    </div>
  );
};
