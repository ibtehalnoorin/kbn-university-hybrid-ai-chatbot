import React from 'react';
import { Globe, RefreshCw, Trash2, Calendar, FileText } from 'lucide-react';
import Button from '../common/Button';

export default function SourceCard({ source, onRefresh, onDelete, isRefreshing }) {
  return (
    <div className="p-4 rounded-xl bg-surface border border-borderCol hover:border-electric/40 transition-colors shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="w-9 h-9 rounded-lg bg-amethyst-deep border border-borderCol flex items-center justify-center text-electric mt-0.5">
            <Globe className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-primaryText">{source.name}</h4>
            <a
              href={source.base_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-lavender-soft hover:underline flex items-center space-x-1 mt-0.5"
            >
              <span>{source.base_url}</span>
            </a>
            {source.description && (
              <p className="text-xs text-secondaryText mt-1">{source.description}</p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onRefresh(source.id)}
            disabled={isRefreshing}
            title="Reindex pages"
            icon={RefreshCw}
          >
            Reindex
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onDelete(source.id)}
            className="text-red-400 hover:text-red-300 hover:bg-red-950/30"
            title="Delete source and vectors"
            icon={Trash2}
          />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-borderCol/60 flex items-center justify-between text-xs text-secondaryText">
        <div className="flex items-center space-x-1.5">
          <FileText className="w-3.5 h-3.5 text-electric" />
          <span><strong>{source.total_pages}</strong> indexed pages</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <Calendar className="w-3.5 h-3.5 text-secondaryText" />
          <span>
            {source.last_crawled_at
              ? `Last updated: ${new Date(source.last_crawled_at).toLocaleDateString()}`
              : 'Never crawled'}
          </span>
        </div>
      </div>
    </div>
  );
}
