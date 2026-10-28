import React from 'react';
import { Activity, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';

export default function IngestionStatus({ jobs }) {
  if (!jobs || jobs.length === 0) return null;

  return (
    <div className="mt-8">
      <div className="flex items-center space-x-2 mb-3">
        <Activity className="w-4 h-4 text-electric" />
        <h3 className="text-sm font-semibold text-primaryText uppercase tracking-wider">
          Recent Ingestion Jobs
        </h3>
      </div>

      <div className="space-y-2">
        {jobs.map((job) => {
          const isRunning = job.status === 'running' || job.status === 'pending';
          const isCompleted = job.status === 'completed';

          return (
            <div
              key={job.id}
              className="p-3.5 rounded-lg bg-surface border border-borderCol flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2"
            >
              <div className="flex items-center space-x-3">
                {isRunning ? (
                  <LoadingSpinner size="sm" />
                ) : isCompleted ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-400" />
                )}
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-primaryText">Job #{job.id}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        isRunning
                          ? 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
                          : isCompleted
                          ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'
                          : 'bg-red-950/60 text-red-300 border border-red-800/60'
                      }`}
                    >
                      {job.status}
                    </span>
                  </div>
                  <p className="text-secondaryText text-[11px] truncate max-w-sm mt-0.5">
                    {job.source_url}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-4 text-secondaryText">
                <div>
                  Discovered: <strong className="text-primaryText">{job.pages_discovered}</strong>
                </div>
                <div>
                  Processed: <strong className="text-primaryText">{job.pages_processed}</strong>
                </div>
                {job.pages_failed > 0 && (
                  <div className="text-red-400">
                    Failed: <strong>{job.pages_failed}</strong>
                  </div>
                )}
                <div className="hidden md:flex items-center space-x-1 text-[11px]">
                  <Clock className="w-3 h-3" />
                  <span>{new Date(job.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
