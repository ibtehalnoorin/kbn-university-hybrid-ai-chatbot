import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ChatProvider } from './context/ChatContext';
import AppLayout from './components/layout/AppLayout';
import ChatPage from './pages/ChatPage';
import KnowledgePage from './pages/KnowledgePage';
import MemoryPage from './pages/MemoryPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <BrowserRouter>
      <ChatProvider>
        <AppLayout>
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/memory" element={<MemoryPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </ChatProvider>
    </BrowserRouter>
  );
}
