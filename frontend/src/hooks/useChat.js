import { useState, useEffect, useRef } from 'react';
import { chatService } from '../services/chatService';
import { useChatContext } from '../context/ChatContext';

export function useChat() {
  const { activeConversationId, setActiveConversationId, fetchConversations } = useChatContext();
  const [messages, setMessages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  const stopStreamRef = useRef(null);

  useEffect(() => {
    if (!activeConversationId) {
      setMessages([]);
      return;
    }

    let isMounted = true;
    chatService.getMessages(activeConversationId)
      .then((msgs) => {
        if (isMounted) setMessages(msgs);
      })
      .catch((err) => {
        if (isMounted) setError(err.message);
      });

    return () => {
      isMounted = false;
      if (stopStreamRef.current) {
        stopStreamRef.current();
      }
    };
  }, [activeConversationId]);

  const sendMessage = async (text) => {
    if (!text || !text.trim() || isGenerating) return;

    setError(null);
    const userMessageText = text.trim();

    // Optimistic user bubble
    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: userMessageText,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsGenerating(true);

    // Placeholder assistant message for streaming
    const tempAsstId = Date.now() + 1;
    const tempAsstMsg = {
      id: tempAsstId,
      role: 'assistant',
      content: '',
      response_type: 'llm',
      citations: [],
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempAsstMsg]);

    try {
      const stopFn = chatService.sendMessageStream(
        userMessageText,
        activeConversationId,
        {
          onInit: (newConvId) => {
            if (!activeConversationId && newConvId) {
              setActiveConversationId(newConvId);
              fetchConversations();
            }
          },
          onChunk: (chunk) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === tempAsstId
                  ? { ...msg, content: msg.content + chunk }
                  : msg
              )
            );
          },
          onDone: (doneEvent) => {
            setIsGenerating(false);
            stopStreamRef.current = null;
            if (doneEvent.message) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === tempAsstId
                    ? {
                        ...doneEvent.message,
                        citations: doneEvent.citations || []
                      }
                    : msg
                )
              );
            }
          },
          onError: (err) => {
            setIsGenerating(false);
            setError(err.message);
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === tempAsstId
                  ? {
                      ...msg,
                      content:
                        msg.content ||
                        'An error occurred while generating the response. Please try again.',
                      response_type: 'error'
                    }
                  : msg
              )
            );
          }
        }
      );
      stopStreamRef.current = stopFn;
    } catch (err) {
      setIsGenerating(false);
      setError(err.message);
    }
  };

  const stopGeneration = () => {
    if (stopStreamRef.current) {
      stopStreamRef.current();
      stopStreamRef.current = null;
      setIsGenerating(false);
    }
  };

  return {
    messages,
    sendMessage,
    stopGeneration,
    isGenerating,
    error
  };
}
