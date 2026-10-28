import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import { Copy, Check, GraduationCap, User, Sparkles, CheckCircle2, AlertTriangle } from 'lucide-react';
import SourceCitations from './SourceCitations';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (message.content) {
      navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getBadge = () => {
    if (isUser) return null;
    const type = message.response_type;
    if (type === 'rule') {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-800/60">
          <CheckCircle2 className="w-3 h-3" />
          <span>Verified FAQ</span>
        </span>
      );
    }
    if (type === 'rag') {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-electric/20 text-lavender-soft border border-electric/40">
          <Sparkles className="w-3 h-3 text-electric" />
          <span>RAG Grounded</span>
        </span>
      );
    }
    if (type === 'error') {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-red-950/60 text-red-300 border border-red-800/60">
          <AlertTriangle className="w-3 h-3" />
          <span>System Notice</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amethyst-deep text-secondaryText border border-borderCol">
        <span>AI Generated</span>
      </span>
    );
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} group mb-4`}>
      <div className={`flex max-w-[88%] md:max-w-[78%] space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-1 ${
            isUser
              ? 'bg-electric text-white'
              : 'bg-amethyst-deep border border-borderCol text-lavender-soft'
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <GraduationCap className="w-4 h-4 text-electric" />}
        </div>

        {/* Message Content Bubble */}
        <div
          className={`relative rounded-2xl p-4 shadow-md ${
            isUser
              ? 'bg-amethyst-deep text-primaryText border border-electric/40 rounded-tr-sm'
              : 'bg-surface text-primaryText border border-borderCol rounded-tl-sm'
          }`}
        >
          {/* Header Row */}
          <div className="flex items-center justify-between space-x-3 mb-1.5">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-secondaryText">
                {isUser ? 'You' : 'KBN University Assistant'}
              </span>
              {getBadge()}
            </div>

            {!isUser && message.content && (
              <button
                onClick={handleCopy}
                title="Copy response"
                className="opacity-0 group-hover:opacity-100 text-secondaryText hover:text-primaryText p-1 rounded transition-opacity"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>

          {/* Text Body */}
          <div className="text-sm prose-amethyst break-words">
            <ReactMarkdown rehypePlugins={[rehypeSanitize]}>
              {message.content}
            </ReactMarkdown>
          </div>

          {/* Source Citations */}
          {!isUser && message.citations && message.citations.length > 0 && (
            <SourceCitations citations={message.citations} />
          )}

          {/* Timestamp */}
          {message.created_at && (
            <div className="mt-2 text-[10px] text-right text-secondaryText/60">
              {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
