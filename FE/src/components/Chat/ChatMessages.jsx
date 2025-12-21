import React, { useRef, useEffect } from "react";
import { MessageBubble } from "./MessageBubble";

export const ChatMessages = ({ messages, isTyping }) => {
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isNearBottom()) {
      scrollToBottom();
    }
  }, [messages]);

  const isNearBottom = () => {
    const container = messagesContainerRef.current;
    if (!container) return false;

    return (
      container.scrollHeight - container.scrollTop - container.clientHeight <
      100
    );
  };

  return (
    <div
      ref={messagesContainerRef}
      className="chat-messages-container h-full overflow-y-auto p-4 flex flex-col"
    >
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} message={msg} />
      ))}

   

      <div ref={messagesEndRef} />
    </div>
  );
};
