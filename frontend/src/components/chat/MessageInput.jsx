import React, { useState, useRef, useEffect } from 'react';
import { Send, Square } from 'lucide-react';
import Button from '../common/Button';

export default function MessageInput({ onSend, onStop, isGenerating, disabled }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!input.trim() || isGenerating || disabled) return;
    onSend(input);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  return (
    <div className="p-4 bg-amethyst-dark border-t border-borderCol">
      <div className="max-w-4xl mx-auto flex items-end space-x-2">
        <div className="flex-1 relative rounded-xl bg-surface border border-borderCol focus-within:border-electric transition-colors shadow-inner">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Ask about KBN University programs, admissions, faculties, or contact..."
            className="w-full bg-transparent px-4 py-3 text-sm text-primaryText placeholder-secondaryText/60 focus:outline-none resize-none max-h-40 min-h-[44px]"
          />
        </div>

        {isGenerating ? (
          <Button
            onClick={onStop}
            variant="danger"
            className="h-[44px] px-3.5"
            title="Stop generation"
            icon={Square}
          >
            <span className="hidden sm:inline">Stop</span>
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            variant="primary"
            className="h-[44px] px-4 shadow-md"
            title="Send message (Enter)"
            icon={Send}
          >
            <span className="hidden sm:inline">Send</span>
          </Button>
        )}
      </div>
      <div className="max-w-4xl mx-auto mt-2 text-[11px] text-center text-secondaryText/60 flex items-center justify-center space-x-1">
        <span>Enter sends • Shift+Enter for newline • AI responses grounded in official university publications</span>
      </div>
    </div>
  );
}
