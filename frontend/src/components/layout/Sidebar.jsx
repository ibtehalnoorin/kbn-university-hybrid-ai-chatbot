import React, { useState } from 'react';
import { Plus, MessageSquare, Edit2, Trash2, Check, X } from 'lucide-react';
import { useChatContext } from '../../context/ChatContext';
import Button from '../common/Button';

export default function Sidebar({ isOpen, onClose }) {
  const {
    conversations,
    activeConversationId,
    setActiveConversationId,
    createNewConversation,
    deleteConversation,
    renameConversation
  } = useChatContext();

  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleStartRename = (conv, e) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const handleSaveRename = (convId, e) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      renameConversation(convId, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelRename = (e) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const handleDelete = (convId, e) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation? All messages will be permanently removed.')) {
      deleteConversation(convId);
    }
  };

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 w-72 bg-amethyst-dark border-r border-borderCol flex flex-col transition-transform duration-200 lg:static lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div className="p-4 border-b border-borderCol">
        <Button
          onClick={() => createNewConversation()}
          variant="primary"
          className="w-full justify-center shadow-lg"
          icon={Plus}
        >
          New Conversation
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        <p className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-secondaryText/70">
          Recent Discussions
        </p>

        {conversations.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-secondaryText">
            No conversations yet. Start a new chat!
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            const isEditing = conv.id === editingId;

            return (
              <div
                key={conv.id}
                onClick={() => {
                  setActiveConversationId(conv.id);
                  if (onClose) onClose();
                }}
                className={`group relative flex items-center justify-between px-3 py-2.5 rounded-lg text-sm cursor-pointer transition-colors ${
                  isActive
                    ? 'bg-amethyst-deep text-primaryText font-medium border border-electric/40'
                    : 'text-secondaryText hover:text-primaryText hover:bg-surface'
                }`}
              >
                <div className="flex items-center space-x-2.5 truncate flex-1 min-w-0 pr-2">
                  <MessageSquare
                    className={`w-4 h-4 flex-shrink-0 ${
                      isActive ? 'text-electric' : 'text-secondaryText'
                    }`}
                  />
                  {isEditing ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      className="bg-mainBg border border-electric rounded px-1.5 py-0.5 text-xs text-primaryText focus:outline-none w-full"
                      autoFocus
                    />
                  ) : (
                    <span className="truncate">{conv.title}</span>
                  )}
                </div>

                <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {isEditing ? (
                    <>
                      <button
                        onClick={(e) => handleSaveRename(conv.id, e)}
                        className="p-1 text-green-400 hover:text-green-300"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={handleCancelRename}
                        className="p-1 text-red-400 hover:text-red-300"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={(e) => handleStartRename(conv, e)}
                        title="Rename conversation"
                        className="p-1 text-secondaryText hover:text-lavender-soft"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(conv.id, e)}
                        title="Delete conversation"
                        className="p-1 text-secondaryText hover:text-red-400"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="p-3 border-t border-borderCol text-[11px] text-center text-secondaryText/70 bg-mainBg">
        Khaja Bandanawaz University • Assistant
      </div>
    </aside>
  );
}
