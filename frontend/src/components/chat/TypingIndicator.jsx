import React from 'react';

export default function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1.5 px-3 py-2 bg-surface border border-borderCol rounded-xl w-fit">
      <div className="w-2 h-2 rounded-full bg-electric animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 rounded-full bg-electric-bright animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-2 h-2 rounded-full bg-lavender-soft animate-bounce" style={{ animationDelay: '300ms' }} />
      <span className="text-xs text-secondaryText ml-1.5 font-medium">Consulting knowledge base...</span>
    </div>
  );
}
