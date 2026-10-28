import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Modal({ isOpen, onClose, title, children, maxWidth = 'max-w-md' }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className={`w-full ${maxWidth} bg-surface border border-borderCol rounded-xl shadow-2xl overflow-hidden`}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-borderCol bg-amethyst-dark">
          <h3 className="text-base font-semibold text-primaryText">{title}</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-secondaryText hover:text-primaryText hover:bg-amethyst-deep transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}
