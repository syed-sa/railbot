import React, { useState } from 'react';
import { Send } from 'lucide-react';

export const ChatInput = ({ onSendMessage, disabled }) => {
  const [inputMessage, setInputMessage] = useState('');

  const handleSend = () => {
    if (inputMessage.trim() && !disabled) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t px-4 py-3">
      <div className="flex items-center gap-3 max-w-4xl mx-auto">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about trains, PNR status, seat availability..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-full
                     focus:ring-2 focus:ring-indigo-500 outline-none"
          disabled={disabled}
        />

        <button
          onClick={handleSend}
          disabled={disabled}
          className="p-3 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};
