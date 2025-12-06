import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

 const sendMessage = async () => {
  if (!input.trim()) return;

  const userMessage: Message = { role: "user", content: input };
  setMessages((prev) => [...prev, userMessage]);

  // Clear input immediately
  const currentInput = input;
  setInput("");

  try {
    const response = await fetch(
      "http://localhost:8000/api/v1/chat/stream?timeout=30",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify({
          conversation_id: Date.now().toString(), // Use unique ID
          message: currentInput,
        }),
      }
    );

    // Check if response is OK
    if (!response.ok) {
      console.error("Fetch error:", response.status, response.statusText);
      return;
    }

    // Check if response body exists
    if (!response.body) {
      console.error("No response body");
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let assistantMessage = { role: "assistant", content: "" };

    // Add initial assistant message
    setMessages((prev) => [...prev, assistantMessage]);

    while (true) {
      const { value, done } = await reader.read();
      
      if (done) {
        console.log("Stream complete");
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      
      // Process complete SSE events (delimited by \n\n)
      const lines = buffer.split("\n");
      buffer = "";
      
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.substring(6); // Remove "data: "
          
          if (data === "[DONE]") {
            continue;
          }
          
          try {
            // If your backend sends JSON, parse it
            const parsed = JSON.parse(data);
            const token = parsed.choices?.[0]?.delta?.content || 
                          parsed.content || 
                          parsed.token?.text || 
                          parsed;
            
            if (token && typeof token === "string") {
              assistantMessage.content += token;
              
              // Update the assistant message in state
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                
                if (lastMessage?.role === "assistant") {
                  lastMessage.content = assistantMessage.content;
                }
                
                return newMessages;
              });
            }
          } catch (e) {
            // If not JSON, treat as plain text
            if (data && data !== "[DONE]") {
              assistantMessage.content += data;
              
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                
                if (lastMessage?.role === "assistant") {
                  lastMessage.content = assistantMessage.content;
                }
                
                return newMessages;
              });
            }
          }
        }
      }
    }
  } catch (error) {
    console.error("Error sending message:", error);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "Error: Failed to get response" },
    ]);
  }
};

  return (
    <div style={{ padding: 20 }}>
      <h2>💬 Streaming Chat</h2>

      <div
        style={{
          border: "1px solid #ccc",
          height: "300px",
          overflowY: "auto",
          padding: 10,
          marginBottom: 10,
        }}
      >
        {messages.map((m, idx) => (
          <div
            key={idx}
            style={{
              textAlign: m.role === "user" ? "right" : "left",
              marginBottom: 8,
            }}
          >
            <strong>{m.role === "user" ? "🧑 You" : "🤖 Bot"}:</strong>{" "}
            {m.content}
          </div>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Say something..."
        style={{ width: "70%", padding: 8 }}
      />
      <button onClick={sendMessage} style={{ padding: 8, marginLeft: 10 }}>
        Send
      </button>
    </div>
  );
}
