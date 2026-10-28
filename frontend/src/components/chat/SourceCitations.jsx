import React, { useState } from 'react';
import { ExternalLink, BookOpen } from 'lucide-react';

export default function SourceCitations({ citations }) {
  const [activeTooltip, setActiveTooltip] = useState(null);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-2.5 border-t border-borderCol/60">
      <div className="flex items-center space-x-1.5 text-xs text-secondaryText mb-2">
        <BookOpen className="w-3.5 h-3.5 text-electric" />
        <span className="font-semibold uppercase tracking-wider text-[11px] text-lavender-soft">
          Verified University Sources:
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {citations.map((cite, idx) => (
          <div
            key={idx}
            className="relative"
            onMouseEnter={() => setActiveTooltip(idx)}
            onMouseLeave={() => setActiveTooltip(null)}
          >
            <a
              href={cite.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-amethyst-dark hover:bg-amethyst-deep text-lavender-soft border border-borderCol hover:border-electric/50 transition-colors"
            >
              <span className="truncate max-w-[200px]">{cite.title || 'Official Page'}</span>
              <ExternalLink className="w-3 h-3 text-secondaryText" />
            </a>

            {activeTooltip === idx && cite.snippet && (
              <div className="absolute bottom-full left-0 mb-2 w-72 p-2.5 bg-amethyst-dark text-xs text-primaryText rounded-lg shadow-xl border border-electric/40 z-30 pointer-events-none animate-fadeIn">
                <p className="font-semibold text-lavender-soft mb-1">{cite.title}</p>
                <p className="text-secondaryText text-[11px] leading-relaxed line-clamp-4">{cite.snippet}</p>
                <div className="mt-1.5 text-[10px] text-electric truncate">{cite.url}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
