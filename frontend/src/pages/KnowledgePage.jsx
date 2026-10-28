import React, { useState, useEffect } from 'react';
import { Database, RefreshCw } from 'lucide-react';
import WebsiteForm from '../components/knowledge/WebsiteForm';
import SourceCard from '../components/knowledge/SourceCard';
import IngestionStatus from '../components/knowledge/IngestionStatus';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Button from '../components/common/Button';
import { knowledgeService } from '../services/knowledgeService';

export default function KnowledgePage() {
  const [sources, setSources] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setError(null);
      const [srcList, jobList] = await Promise.all([
        knowledgeService.listSources(),
        knowledgeService.listJobs()
      ]);
      setSources(srcList);
      setJobs(jobList);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll ingestion jobs periodically if any job is running
    const interval = setInterval(() => {
      knowledgeService.listJobs().then(setJobs).catch(() => {});
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAddSource = async ({ url, name, description }) => {
    try {
      setSubmitting(true);
      setError(null);
      await knowledgeService.addSource(url, name, description);
      await fetchData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRefresh = async (sourceId) => {
    try {
      setError(null);
      await knowledgeService.refreshSource(sourceId);
      await fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (sourceId) => {
    if (window.confirm('Delete this knowledge source and all its associated document vectors?')) {
      try {
        setError(null);
        await knowledgeService.deleteSource(sourceId);
        await fetchData();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 max-w-5xl mx-auto w-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-primaryText flex items-center space-x-2">
            <Database className="w-5 h-5 text-electric" />
            <span>Knowledge Base Management</span>
          </h2>
          <p className="text-xs text-secondaryText mt-1">
            Manage official university website crawlers, documents, and vector embeddings.
          </p>
        </div>

        <Button
          size="sm"
          variant="secondary"
          onClick={fetchData}
          icon={RefreshCw}
        >
          Refresh
        </Button>
      </div>

      <ErrorMessage message={error} onRetry={fetchData} className="mb-6" />

      {/* Register Form */}
      <WebsiteForm onAddSource={handleAddSource} isSubmitting={submitting} />

      {/* Sources List */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-lavender-soft uppercase tracking-wider">
          Active University Sources ({sources.length})
        </h3>

        {loading ? (
          <div className="p-12 text-center">
            <LoadingSpinner size="lg" />
            <p className="text-xs text-secondaryText mt-2">Loading knowledge sources...</p>
          </div>
        ) : sources.length === 0 ? (
          <div className="p-8 text-center rounded-xl bg-surface border border-dashed border-borderCol text-xs text-secondaryText">
            No knowledge sources indexed yet. Add https://www.kbn.university/ to begin.
          </div>
        ) : (
          <div className="space-y-3">
            {sources.map((src) => (
              <SourceCard
                key={src.id}
                source={src}
                onRefresh={handleRefresh}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>

      {/* Recent Jobs */}
      <IngestionStatus jobs={jobs} />
    </div>
  );
}
