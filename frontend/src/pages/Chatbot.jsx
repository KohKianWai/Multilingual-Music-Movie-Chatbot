import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

const BG = "#8A4493";
const url = "http://127.0.0.1:8000";

function BotAvatar() {
  return (
    <div
      className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-bold text-white mt-1"
      style={{ background: "#8B25CB" }}
    >
      M
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-start gap-2">
      <BotAvatar />
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-gray-100">
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-gray-400 block"
              style={{
                animation: "typing-dot 1.2s ease-in-out infinite",
                animationDelay: `${i * 0.2}s`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "bot",
      content: "Hi! Would you like music or movie recommendations today?",
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const messagesEndRef = useRef(null);

  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const streamRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const toggleVoiceInput = async () => {
    if (isRecording) {
      if (mediaRecorder.current && mediaRecorder.current.state !== "inactive") {
        mediaRecorder.current.stop();
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }

      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

        streamRef.current = stream;
        mediaRecorder.current = new MediaRecorder(stream);
        audioChunks.current = [];

        mediaRecorder.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.current.push(event.data);
          }
        };

        mediaRecorder.current.onstop = async () => {
          const audioBlob = new Blob(audioChunks.current, {
            type: "audio/webm",
          });

          if (audioBlob.size > 0) {
            await handleSendVoice(audioBlob);
          }
        };

        mediaRecorder.current.start();
        setIsRecording(true);
      } catch (error) {
        console.error("Microphone access denied:", error);
        alert("Please allow microphone access to use voice input.");
      }
    }
  };

  const handleSendVoice = async (blob) => {
    setIsTyping(true);

    const voiceMessageId = Date.now().toString();

    const userMessage = {
      id: voiceMessageId,
      role: "user",
      content: "Transcribing voice...",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const formData = new FormData();
    formData.append("audio", blob, "recording.webm");

    try {
      const response = await fetch(`${url}/voice-chat`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      setMessages((prev) =>
        prev.map((m) =>
          m.id === voiceMessageId
            ? {
                ...m,
                content:
                  data.transcript || "Could not transcribe voice.",
              }
            : m
        )
      );

      const aiResponse = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: data.reply || "No response from bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error(error);

      setMessages((prev) =>
        prev.map((m) =>
          m.id === voiceMessageId
            ? {
                ...m,
                content: "Voice message failed to transcribe.",
              }
            : m
        )
      );
    }

    setIsTyping(false);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const currentInput = input;

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: currentInput,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch(`${url}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: currentInput }),
      });

      const data = await response.json();

      const aiResponse = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: data.reply || "No response from bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "bot",
          content: "Connection Error",
          timestamp: new Date(),
        },
      ]);
    }

    setIsTyping(false);
  };

  return (
    <div
      className="flex-1 flex flex-col overflow-hidden"
      style={{
        background: "#ffffff",
        borderRadius: "18px",
        border: "1.5px solid rgba(200,180,220,0.4)",
        boxShadow: "0 8px 40px rgba(0,0,0,0.18)",
      }}
    >
      {/* Top Button */}
      <div className="flex justify-center pt-5 pb-2 px-5">
        <button
          className="px-6 py-2 rounded-full text-base font-semibold text-white hover:opacity-90"
          style={{
            background:
              "linear-gradient(135deg, #6D28D9, #8A4493, #C026D3)",
          }}
        >
          Start your chat with MuseBot here!
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-0 overflow-y-auto no-scrollbar px-5 py-3 space-y-4">
        {messages.map((message) => {
          const isBot = message.role === "bot";

          return (
            <div
              key={message.id}
              className={`flex ${
                isBot ? "justify-start" : "justify-end"
              }`}
            >
              {isBot ? (
                <div className="flex items-start gap-2">
                  <BotAvatar />
                  <div className="max-w-[95%] w-fit px-4 py-3 rounded-2xl rounded-tl-sm bg-gray-100 text-base text-gray-700 whitespace-pre-line">
                    {message.content}
                  </div>
                </div>
              ) : (
                <div
                  className="max-w-[95%] w-fit px-4 py-3 rounded-2xl text-base text-white whitespace-pre-line"
                  style={{
                    background:
                      "linear-gradient(135deg, #8A4493, #B044E8)",
                  }}
                >
                  {message.content}
                </div>
              )}
            </div>
          );
        })}

        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-4 border-t border-gray-100">
        <div
          className="flex items-center gap-2 rounded-full px-4 py-2.5 border border-gray-200"
          style={{ background: "#F0EBF8" }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type your query here..."
            className="flex-1 bg-transparent text-base text-gray-700 outline-none"
          />

          {/* Voice Button */}
          <button
            onClick={toggleVoiceInput}
            className={`w-9 h-9 rounded-full flex items-center justify-center transition-all ${
              isRecording ? "animate-pulse" : ""
            }`}
            style={{
              background: isRecording
                ? "rgba(220, 38, 38, 0.35)"
                : "transparent",
              border: isRecording
                ? "1.5px solid rgba(220, 38, 38, 0.5)"
                : "none",
            }}
            aria-label="Voice"
          >
            <span className="text-base">🎤</span>
          </button>

          {/* Send Button */}
          <button
            onClick={sendMessage}
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background: BG }}
          >
            <Send size={14} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}