import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText } from 'lucide-react';

interface MessageContentProps {
  content: string;
  role: 'user' | 'assistant';
}

// Custom Citation Component
const CitationBadge = ({ text }: { text: string }) => (
  <span className="inline-flex items-center gap-1 px-2 py-0.5 mx-1 rounded-md bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 text-[10px] font-bold border border-blue-200 dark:border-blue-800/50 cursor-pointer hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors">
    <FileText size={10} />
    {text}
  </span>
);

export const MessageContent: React.FC<MessageContentProps> = ({ content, role }) => {
  if (role === 'user') {
    return <p className="text-[15px] leading-relaxed font-medium whitespace-pre-wrap">{content}</p>;
  }

  // 1. Extract Unique Citations for the Footer
  const citationRegex = /\[(.*?)\]/g;
  const matches = [...content.matchAll(citationRegex)].map(m => m[1]);
  const uniqueSources = Array.from(new Set(matches)).filter(s => s.length < 100 && !s.includes('http')); // Basic filter

  // 2. Split content for inline rendering
  const parts = content.split(/(\[[^\]]+\])/g);

  return (
    <div className="space-y-4">
        {/* Main Text Content */}
        <div className="text-[15px] leading-relaxed font-medium">
            {parts.map((part, idx) => {
                const isCitation = part.startsWith('[') && part.endsWith(']') && part.length < 100;
                if (isCitation) {
                    const text = part.slice(1, -1);
                    return <CitationBadge key={idx} text={text} />;
                }
                return (
                    <span key={idx}>
                        <ReactMarkdown 
                            remarkPlugins={[remarkGfm]}
                            components={{
                                p: ({node, ...props}) => <span {...props} />,
                                strong: ({node, ...props}) => <span className="font-bold text-slate-900 dark:text-white" {...props} />,
                                ul: ({node, ...props}) => <ul className="list-disc list-inside my-2 space-y-1 block" {...props} />,
                                ol: ({node, ...props}) => <ol className="list-decimal list-inside my-2 space-y-1 block" {...props} />,
                                li: ({node, ...props}) => <li className="ml-2" {...props} />,
                                code: ({node, ...props}) => <code className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-sm font-mono text-pink-600" {...props} />,
                            }}
                        >
                            {part}
                        </ReactMarkdown>
                    </span>
                );
            })}
        </div>

        {/* Footer: Verified Sources List */}
        {uniqueSources.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 mb-2 opacity-70">
                    <FileText size={12} className="text-blue-600" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Verified Sources</span>
                </div>
                <div className="space-y-1.5">
                    {uniqueSources.map((source, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/50 p-2 rounded-lg border border-slate-100 dark:border-slate-800">
                            <span className="font-mono text-blue-500 text-[10px] pt-0.5">[{idx + 1}]</span>
                            <span>{source}</span>
                        </div>
                    ))}
                </div>
            </div>
        )}
    </div>
  );
};
