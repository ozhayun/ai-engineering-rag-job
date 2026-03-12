import { useState, useRef } from 'react';
import { Send, Loader } from 'lucide-react';
import { isRTL } from '../utils/rtl';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');
  const hasRTL = isRTL(input);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      handleSubmit(e as any);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 items-end">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder="Ask about the jobs..."
        disabled={isLoading}
        rows={1}
        className="flex-1 px-4 py-3 rounded-xl resize-none text-sm focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        style={{
          background: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid rgba(0, 217, 255, 0.2)',
          fontFamily: "'Sora', sans-serif",
          direction: hasRTL ? 'rtl' : 'ltr',
          textAlign: hasRTL ? 'right' : 'left',
          unicodeBidi: 'plaintext'
        }}
        dir={hasRTL ? 'rtl' : 'ltr'}
        onFocus={(e) => {
          e.target.style.borderColor = 'rgba(0, 217, 255, 0.5)';
          e.target.style.boxShadow = '0 0 20px rgba(0, 217, 255, 0.1)';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = 'rgba(0, 217, 255, 0.2)';
          e.target.style.boxShadow = 'none';
        }}
      />
      <button
        type="submit"
        disabled={!input.trim() || isLoading}
        className="px-4 py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg"
        style={{
          background: 'linear-gradient(135deg, var(--color-accent), var(--color-primary-dark))',
          color: 'var(--color-bg-darker)',
        }}
      >
        {isLoading ? (
          <Loader size={18} className="animate-spin" />
        ) : (
          <>
            <Send size={18} />
            <span className="hidden sm:inline">Send</span>
          </>
        )}
      </button>
    </form>
  );
}
