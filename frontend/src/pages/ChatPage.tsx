import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import { chatApi } from '../services/api';
import { ArrowLeft, Send, Bot, User } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  routedTo?: string;
  sources?: any[];
}

const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { company, addActivity } = useApp();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !company || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        company_id: company.id,
        message: userMessage,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.response || response.message || 'No response',
          routedTo: response.routed_to,
          sources: response.sources,
        },
      ]);

      addActivity({
        id: Date.now().toString(),
        title: 'AI Chat',
        description: userMessage.substring(0, 50) + (userMessage.length > 50 ? '...' : ''),
        timestamp: new Date().toISOString(),
        type: 'chat',
        content: `Question: ${userMessage}\n\nAnswer: ${response.response || response.message || 'No response'}`,
        toolUsed: response.routed_to ? `${response.routed_to} Agent` : 'AI Chat',
      });
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err.response?.data?.detail || err.message || 'Failed to get response'}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedPrompts = [
    "Generate a competitive analysis",
    "What's my patentability score?",
    "Create an Instagram post for my product",
    "What roles should I hire first?",
    "Generate a privacy policy",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-fuchsia-50 flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-purple-100 px-8 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-purple-100 rounded-lg transition-colors text-purple-600"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold gradient-text">AI Assistant</h1>
              <p className="text-slate-500 text-sm">Ask anything about your startup</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-100 rounded-full text-sm text-purple-700">
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
            {company?.company_name}
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center">
                <Bot size={40} className="text-purple-500" />
              </div>
              <h2 className="text-2xl font-semibold text-slate-800 mb-2">How can I help you today?</h2>
              <p className="text-slate-500 mb-8">
                Ask me anything about pitch decks, competitors, patents, marketing, or team building.
              </p>
              
              {/* Suggested Prompts */}
              <div className="flex flex-wrap justify-center gap-2 max-w-2xl mx-auto">
                {suggestedPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(prompt)}
                    className="px-4 py-2 bg-white border border-purple-200 rounded-full text-sm text-purple-700 hover:bg-purple-50 hover:border-purple-300 transition-all"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                  <Bot size={18} className="text-white" />
                </div>
              )}
              
              <div
                className={`max-w-[75%] rounded-2xl p-4 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white'
                    : 'bg-white border border-purple-100 text-slate-700 shadow-sm'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {message.routedTo && (
                  <div className="mt-2 pt-2 border-t border-purple-200/50 text-xs text-purple-400">
                    Handled by: {message.routedTo} agent
                  </div>
                )}
                
                {message.sources && message.sources.length > 0 && (
                  <details className="mt-3 pt-2 border-t border-purple-100">
                    <summary className="text-xs text-purple-500 cursor-pointer hover:text-purple-700">
                      View sources ({message.sources.length})
                    </summary>
                    <div className="mt-2 space-y-1">
                      {message.sources.slice(0, 3).map((source: any, i: number) => (
                        <div key={i} className="text-xs text-slate-500">
                          • {source.title || source.source}
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>

              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center flex-shrink-0">
                  <User size={18} className="text-white" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                <Bot size={18} className="text-white" />
              </div>
              <div className="bg-white border border-purple-100 rounded-2xl p-4 shadow-sm">
                <div className="flex items-center gap-2">
                  <div className="spinner"></div>
                  <span className="text-purple-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white/80 backdrop-blur-sm border-t border-purple-100 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask me anything about your startup..."
                className="w-full p-4 pr-12 border-2 border-purple-200 rounded-2xl resize-none focus:outline-none focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all"
                rows={1}
                style={{ minHeight: '56px', maxHeight: '150px' }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center hover:shadow-lg hover:shadow-purple-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
          <p className="text-center text-xs text-slate-400 mt-3">
            AI responses are generated based on your company data and RAG knowledge base
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
