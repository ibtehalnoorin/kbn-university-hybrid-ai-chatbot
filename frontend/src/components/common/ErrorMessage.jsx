import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import Button from './Button';

export default function ErrorMessage({ message, onRetry, className = '' }) {
  if (!message) return null;

  return (
    <div className={`p-4 rounded-lg bg-red-950/40 border border-red-800/60 flex items-start space-x-3 text-red-200 ${className}`}>
      <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
      <div className="flex-1 text-sm leading-relaxed">
        <p className="font-semibold text-red-300">Something went wrong</p>
        <p className="mt-1 text-red-200/90">{message}</p>
        {onRetry && (
          <div className="mt-3">
            <Button size="sm" variant="secondary" onClick={onRetry} icon={RefreshCw}>
              Retry Action
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
