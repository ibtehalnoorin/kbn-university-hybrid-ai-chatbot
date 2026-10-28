import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

export default function MessageList({ messages, isGenerating }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isGenerating]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 max-w-4xl w-full mx-auto">
      {messages.map((msg, index) => (
        <MessageBubble key={msg.id || index} message={msg} />
      ))}

      {isGenerating && (
        <div className="flex justify-start mb-4">
          <TypingIndicator />
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
