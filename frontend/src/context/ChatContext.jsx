import React, { createContext, useContext, useState, useEffect } from 'react';
import { chatService } from '../services/chatService';

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const list = await chatService.listConversations();
      setConversations(list);
      if (list.length > 0 && !activeConversationId) {
        setActiveConversationId(list[0].id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  const createNewConversation = async (title = 'New Conversation') => {
    try {
      const conv = await chatService.createConversation(title);
      setConversations((prev) => [conv, ...prev]);
      setActiveConversationId(conv.id);
      return conv;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  const deleteConversation = async (id) => {
    try {
      await chatService.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        const remaining = conversations.filter((c) => c.id !== id);
        setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const renameConversation = async (id, newTitle) => {
    try {
      const updated = await chatService.updateConversation(id, newTitle);
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title: updated.title } : c))
      );
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversationId,
        setActiveConversationId,
        fetchConversations,
        createNewConversation,
        deleteConversation,
        renameConversation,
        loading,
        error
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  return useContext(ChatContext);
}
