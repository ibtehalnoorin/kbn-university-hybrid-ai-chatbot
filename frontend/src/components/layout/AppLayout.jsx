import React from 'react';
import Header from './Header';
import MobileNavigation from './MobileNavigation';

export default function AppLayout({ children }) {
  return (
    <div className="flex flex-col h-screen w-screen bg-mainBg overflow-hidden">
      <Header />
      <main className="flex-1 overflow-hidden flex relative pb-12 md:pb-0">
        {children}
      </main>
      <MobileNavigation />
    </div>
  );
}
