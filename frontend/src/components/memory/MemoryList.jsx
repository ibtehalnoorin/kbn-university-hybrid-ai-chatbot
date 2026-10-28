import React from 'react';
import { Brain, Shield, Info } from 'lucide-react';
import MemoryCard from './MemoryCard';
import Button from '../common/Button';

export default function MemoryList({
  memories,
  isEnabled,
  onToggleMemory,
  onDeleteMemory,
  onClearAll,
  onOpenAddModal
}) {
  return (
    <div className="space-y-6">
      {/* Control Card */}
      <div className="p-5 rounded-xl bg-surface border border-borderCol flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-start space-x-3">
          <div className="w-10 h-10 rounded-xl bg-electric/20 border border-electric/40 flex items-center justify-center text-electric mt-0.5">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-primaryText">Long-Term Memory Persistence</h3>
            <p className="text-xs text-secondaryText mt-0.5 max-w-md">
              When enabled, the assistant retains your academic preferences (e.g. intended major, campus interests)
              across sessions while strictly rejecting sensitive credentials.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={isEnabled}
              onChange={(e) => onToggleMemory(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-amethyst-deep border border-borderCol rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-electric"></div>
            <span className="ml-2.5 text-xs font-semibold text-primaryText">
              {isEnabled ? 'Enabled' : 'Disabled'}
            </span>
          </label>
        </div>
      </div>

      {/* Information Banner */}
      <div className="p-3.5 rounded-lg bg-amethyst-deep/60 border border-borderCol flex items-start space-x-2.5 text-xs text-secondaryText">
        <Info className="w-4 h-4 text-electric mt-0.5 flex-shrink-0" />
        <span>
          Memory items are private to your current session. All stored items can be inspected, edited, or purged at any time.
        </span>
      </div>

      {/* Memories Collection */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-semibold text-lavender-soft uppercase tracking-wider">
            Saved Preferences ({memories.length})
          </h4>
          <div className="flex items-center space-x-2">
            <Button size="sm" variant="secondary" onClick={onOpenAddModal}>
              + Add Preference
            </Button>
            {memories.length > 0 && (
              <Button size="sm" variant="ghost" className="text-red-400 hover:text-red-300" onClick={onClearAll}>
                Clear All
              </Button>
            )}
          </div>
        </div>

        {memories.length === 0 ? (
          <div className="p-8 text-center rounded-xl bg-surface/50 border border-dashed border-borderCol text-xs text-secondaryText">
            No memories currently saved for this session.
          </div>
        ) : (
          <div className="space-y-2">
            {memories.map((mem) => (
              <MemoryCard key={mem.id} memory={mem} onDelete={onDeleteMemory} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
