import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Music, Film, ArrowLeft, Mic, MicOff} from 'lucide-react';

function ChatPage({ onBack }) {
  const url = "http://127.0.0.1:8000"
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'ai',
      content: " Hey there! I'm MuseBot, your AI music and entertainment companion. I can help you discover new music, recommend movies and much more! What are you in the mood for today?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const streamRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleVoiceInput = async () => {
    if (isRecording) {
      // --- SECOND PRESS: STOP AND SEND ---
      if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
        mediaRecorder.current.stop(); // This triggers mediaRecorder.current.onstop
      }
      
      // Stop the mic hardware immediately
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      
      setIsRecording(false);
    } else {
      // --- FIRST PRESS: START RECORDING ---
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream; // Save to ref for later
        
        mediaRecorder.current = new MediaRecorder(stream);
        audioChunks.current = [];

        mediaRecorder.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.current.push(event.data);
          }
        };

        mediaRecorder.current.onstop = async () => {
          // This runs automatically after mediaRecorder.current.stop() is called
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
          if (audioBlob.size > 0) {
            await handleSendVoice(audioBlob);
          }
        };

        mediaRecorder.current.start();
        setIsRecording(true);
      } catch (err) {
        console.error("Microphone access denied:", err);
        alert("Please allow microphone access to use voice input.");
      }
    }
  };

  const handleSendVoice = async (blob) => {
    setIsTyping(true);
    const audioUrl = URL.createObjectURL(blob);
    
    // Add a placeholder message for the user
    const userMessage = {
      id: Date.now().toString(),
      type: "user",
      content: "Audio Message",
      audioUrl: audioUrl,
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, userMessage]);

    const formData = new FormData();
    // 'audio' matches the parameter name in your FastAPI: voice_chat(audio: UploadFile)
    formData.append("audio", blob, "recording.webm");

    try {
      const response = await fetch(`${url}/voice-chat`, {
        method: "POST",
        body: formData, // Do NOT set Content-Type header; fetch does it automatically for FormData
      });

      const data = await response.json();

      const aiResponse = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: data.reply,
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error("Voice Upload Error:", error);
    }
    setIsTyping(false);
  };

  const handleSendMessage = async () => {
		if (!inputValue.trim()) return;

		const userMessage = {
			id: Date.now().toString(),
			type: "user",
			content: inputValue,
			timestamp: new Date()
		};

		setMessages((prev) => [...prev, userMessage]);
		setInputValue("");
		setIsTyping(true);

		try {
			const response = await fetch(`${url}/chat`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					message: inputValue
				})
			});

			const data = await response.json();

			const aiResponse = {
				id: (Date.now() + 1).toString(),
				type: "ai",
				content: data.reply,
				timestamp: new Date()
			};

			setMessages((prev) => [...prev, aiResponse]);
		} catch (error) {
			setMessages((prev) => [
				...prev,
				{
					id: (Date.now() + 1).toString(),
					type: "ai",
					content: "Connection Error",
					timestamp: new Date()
				}
			]);
		}
		setIsTyping(false);
	};

  return (
    <div className="flex flex-col h-screen bg-black text-white">
      {/* Header */}
      <header className="p-4 border-b border-gray-800 flex items-center justify-between bg-black">
        <button onClick={onBack} className="text-gray-400 hover:text-white flex items-center gap-1">
          <ArrowLeft size={18} /> Back
        </button>
        <div className="flex items-center gap-2">
          <Sparkles className="text-purple-500" />
          <h2 className="font-bold">MuseBot</h2>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-6 py-4 ${
              message.type === 'user' ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 'bg-gray-900 border border-gray-800'
            }`}>
              {message.audioUrl ? (
                <div className="flex flex-col gap-2">
                  <span className="text-xs text-white/70 font-semibold uppercase tracking-wider">🎤 Voice Note</span>
                  <audio 
                    controls 
                    src={message.audioUrl} 
                    className="max-w-[200px] h-10 rounded-lg outline-none" 
                  />
                </div>
              ) : (
                <p className="whitespace-pre-line">{message.content}</p>
              )}
            </div>
          </div>
        ))}
        {isTyping && <div className="text-purple-400 text-sm animate-pulse">MuseBot is thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-900/50 border-t border-gray-800">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type a message..."
            className="flex-1 bg-gray-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
           <button
            onClick={toggleVoiceInput}
            className={`px-6 py-4 rounded-xl transition-all flex items-center gap-2 ${
              isRecording
                ? 'bg-red-600 hover:bg-red-700 animate-pulse ring-2 ring-red-400'
                : 'bg-gray-800 hover:bg-gray-700 border border-gray-700'
            } text-white`}
          >
            {isRecording ? (
              <>
                <Send className="w-5 h-5" />
                <span className="text-xs font-bold uppercase tracking-wider">Stop & Send</span>
              </>
            ) : (
              <Mic className="w-5 h-5" />
            )}
          </button>
          <button onClick={handleSendMessage} className="px-4 py-3 bg-purple-600 rounded-xl hover:bg-purple-700 text-white">
            <Send className= "w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatPage;