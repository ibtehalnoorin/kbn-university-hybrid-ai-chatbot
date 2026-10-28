import React from 'react';
import { Tag, Trash2 } from 'lucide-react';
import Button from '../common/Button';

export default function MemoryCard({ memory, onDelete }) {
  return (
    <div className="p-3.5 rounded-lg bg-surface border border-borderCol hover:border-electric/40 transition-colors flex items-center justify-between text-xs">
      <div className="space-y-1">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-lavender-soft">{memory.key}</span>
          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-amethyst-deep text-secondaryText border border-borderCol">
            <Tag className="w-2.5 h-2.5" />
            <span>{memory.category}</span>
          </span>
        </div>
        <p className="text-secondaryText text-xs leading-relaxed">{memory.value}</p>
      </div>

      <Button
        size="sm"
        variant="ghost"
        onClick={() => onDelete(memory.id)}
        className="text-red-400 hover:text-red-300 hover:bg-red-950/30 ml-3"
        title="Delete memory"
        icon={Trash2}
      />
    </div>
  );
}
