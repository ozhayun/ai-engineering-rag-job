import { useState, useRef, useEffect } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import ErrorBoundary from './components/ErrorBoundary';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  isLoading?: boolean;
}

// Generate unique IDs using crypto
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      type: 'assistant',
      content: "# Welcome to AI Jobs Intelligence\n\nAnalyze real job postings to understand what the market demands.\n\n**Ask questions like:**\n- What skills do AI engineers need?\n- What tools are most in demand?\n- How do senior roles differ from entry-level?\n\nGet insights grounded in real data, not generic advice."
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (question: string) => {
    const userMessage: Message = {
      id: generateId(),
      type: 'user',
      content: question
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    const loadingMessage: Message = {
      id: generateId(),
      type: 'assistant',
      content: 'Analyzing job postings...',
      isLoading: true
    };

    setMessages(prev => [...prev, loadingMessage]);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          id: generateId(),
          type: 'assistant',
          content: data.answer
        }
      ]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          id: generateId(),
          type: 'assistant',
          content: '⚠️ Error: Check that the backend is running and GROQ_API_KEY is set.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ErrorBoundary>
      <div className="h-screen flex flex-col relative" style={{ background: 'var(--color-bg-darker)' }}>
        {/* Header */}
        <header className="relative z-10 border-b px-6 py-8" style={{
          borderColor: 'rgba(0, 217, 255, 0.1)',
          background: 'linear-gradient(180deg, rgba(15, 22, 51, 0.8) 0%, rgba(10, 14, 39, 0.4) 100%)'
        }}>
          <div className="max-w-5xl mx-auto">
            <div className="mb-3 flex items-center gap-3">
              <div className="w-3 h-3 rounded-full animate-glow-pulse" style={{ background: 'var(--color-accent)' }}></div>
              <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--color-accent)' }}>
                Job Intelligence
              </span>
            </div>
            <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "'Space Mono', monospace", letterSpacing: '-0.02em' }}>
              AI Jobs<br />Intelligence
            </h1>
            <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary)' }}>
              Real job postings. Real insights. Data-driven answers.
            </p>
          </div>
        </header>

        {/* Messages Container */}
        <main className="flex-1 overflow-y-auto relative z-10">
          <div className="max-w-5xl mx-auto w-full">
            <div className="space-y-4 p-6 md:p-8">
              {messages.map((message, idx) => (
                <div key={message.id} style={{ animationDelay: `${idx * 0.1}s` }} className="animate-fade-in-up">
                  <ChatMessage
                    message={message.type}
                    content={message.content}
                    isLoading={message.isLoading}
                  />
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </main>

        {/* Input Area */}
        <footer className="relative z-10 border-t px-6 py-6" style={{
          borderColor: 'rgba(0, 217, 255, 0.1)',
          background: 'linear-gradient(180deg, rgba(10, 14, 39, 0.4) 0%, rgba(5, 8, 16, 0.8) 100%)'
        }}>
          <div className="max-w-5xl mx-auto">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
