import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { Loader } from 'lucide-react';
import { isRTL } from '../utils/rtl';

interface ChatMessageProps {
  message: 'user' | 'assistant';
  content: string;
  isLoading?: boolean;
}

export default function ChatMessage({
  message,
  content,
  isLoading
}: ChatMessageProps) {
  const isUser = message === 'user';
  const hasRTL = isRTL(content);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-3`}>
      {isUser ? (
        /* User Message */
        <div className="max-w-2xl">
          <div
            className="rounded-2xl rounded-tr-none px-5 py-3 text-sm leading-relaxed break-words"
            style={{
              background: 'linear-gradient(135deg, var(--color-accent), var(--color-primary-dark))',
              color: 'var(--color-bg-darker)',
              fontWeight: 500,
              direction: hasRTL ? 'rtl' : 'ltr',
              textAlign: hasRTL ? 'right' : 'left',
              unicodeBidi: 'plaintext'
            }}
            dir={hasRTL ? 'rtl' : 'ltr'}
          >
            {content}
          </div>
        </div>
      ) : (
        /* Assistant Message */
        <div className="max-w-2xl flex-1">
          {isLoading ? (
            <div
              className="rounded-2xl rounded-tl-none px-5 py-3 flex items-center gap-3 text-sm"
              style={{
                background: 'var(--color-surface-light)',
                color: 'var(--color-text-secondary)',
                direction: hasRTL ? 'rtl' : 'ltr'
              }}
              dir={hasRTL ? 'rtl' : 'ltr'}
            >
              <Loader className="animate-spin flex-shrink-0" size={16} style={{ color: 'var(--color-accent)' }} />
              <span>{content}</span>
            </div>
          ) : (
            <div
              className="rounded-2xl rounded-tl-none px-5 py-4 text-sm"
              style={{
                background: 'var(--color-surface)',
                border: '1px solid rgba(0, 217, 255, 0.1)',
                color: 'var(--color-text-primary)',
                direction: hasRTL ? 'rtl' : 'ltr'
              }}
              dir={hasRTL ? 'rtl' : 'ltr'}
            >
              <div className="prose prose-invert max-w-none text-sm leading-relaxed">
                <style>{`
                  .prose {
                    --tw-prose-headings: var(--color-accent);
                    --tw-prose-bold: var(--color-text-primary);
                    --tw-prose-links: var(--color-accent);
                  }
                  .prose h1,
                  .prose h2,
                  .prose h3 {
                    font-weight: 600;
                    margin-top: 0.75rem;
                    margin-bottom: 0.5rem;
                    letter-spacing: -0.01em;
                  }
                  .prose h1 {
                    font-size: 1.5rem;
                  }
                  .prose h2 {
                    font-size: 1.25rem;
                  }
                  .prose h3 {
                    font-size: 1.1rem;
                  }
                  .prose p {
                    margin: 0.75rem 0;
                  }
                  .prose ul,
                  .prose ol {
                    margin: 0.75rem 0;
                    padding-right: 1.25rem;
                    padding-left: 0;
                  }
                  [dir="rtl"] .prose ul,
                  [dir="rtl"] .prose ol {
                    padding-right: 1.25rem;
                    padding-left: 0;
                  }
                  .prose li {
                    margin: 0.25rem 0;
                  }
                  .prose strong {
                    color: var(--color-accent);
                    font-weight: 600;
                  }
                  .prose a {
                    text-decoration: none;
                    transition: all 0.2s ease;
                  }
                  .prose a:hover {
                    text-decoration: underline;
                  }
                  .prose code {
                    background: rgba(0, 217, 255, 0.1);
                    color: var(--color-accent);
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-family: 'Space Mono', monospace;
                    font-size: 0.9em;
                  }
                `}</style>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeSanitize]}
                >
                  {content}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
