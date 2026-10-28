import React, { useState } from 'react';
import { Menu } from 'lucide-react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import WelcomeScreen from './WelcomeScreen';
import ErrorMessage from '../common/ErrorMessage';
import Sidebar from '../layout/Sidebar';
import { useChat } from '../../hooks/useChat';

export default function ChatWindow() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { messages, sendMessage, stopGeneration, isGenerating, error } = useChat();

  return (
    <div className="flex-1 flex overflow-hidden relative">
      {/* Sidebar for desktop & mobile drawer */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main chat column */}
      <div className="flex-1 flex flex-col h-full overflow-hidden bg-mainBg">
        {/* Mobile Header Bar */}
        <div className="lg:hidden flex items-center justify-between px-4 py-2 bg-amethyst-dark border-b border-borderCol">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-1.5 rounded-lg text-secondaryText hover:text-primaryText hover:bg-surface"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="text-xs font-semibold text-lavender-soft">Conversations</span>
          <div className="w-5" />
        </div>

        {/* Global Chat Error Banner */}
        {error && (
          <div className="px-4 pt-4 max-w-4xl mx-auto w-full">
            <ErrorMessage message={error} />
          </div>
        )}

        {/* Chat Canvas */}
        {messages.length === 0 ? (
          <WelcomeScreen onSelectStarter={(q) => sendMessage(q)} />
        ) : (
          <MessageList messages={messages} isGenerating={isGenerating} />
        )}

        {/* Input Bar */}
        <MessageInput
          onSend={(text) => sendMessage(text)}
          onStop={stopGeneration}
          isGenerating={isGenerating}
        />
      </div>
    </div>
  );
}
