import React, { useState, useEffect } from 'react';
import { Settings, Server, Cpu, Database, RefreshCw, CheckCircle, AlertCircle, Terminal } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Button from '../components/common/Button';
import { settingsService } from '../services/settingsService';

export default function SettingsPage() {
  const [health, setHealth] = useState(null);
  const [llmStatus, setLlmStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const [h, l] = await Promise.all([
        settingsService.getHealth(),
        settingsService.getLlmStatus()
      ]);
      setHealth(h);
      setLlmStatus(l);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 max-w-4xl mx-auto w-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-primaryText flex items-center space-x-2">
            <Settings className="w-5 h-5 text-electric" />
            <span>System Status & Configuration</span>
          </h2>
          <p className="text-xs text-secondaryText mt-1">
            Real-time diagnostics for local LLM (Ollama), PostgreSQL / pgvector database, and API services.
          </p>
        </div>

        <Button size="sm" variant="secondary" onClick={fetchStatus} icon={RefreshCw}>
          Check Again
        </Button>
      </div>

      <ErrorMessage message={error} onRetry={fetchStatus} className="mb-6" />

      {loading ? (
        <div className="p-12 text-center">
          <LoadingSpinner size="lg" />
          <p className="text-xs text-secondaryText mt-2">Checking system services...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Service Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Database Card */}
            <div className="p-5 rounded-xl bg-surface border border-borderCol shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Database className="w-5 h-5 text-electric" />
                  <h3 className="text-sm font-semibold text-primaryText">Database & Vectors</h3>
                </div>
                <span
                  className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                    health?.database?.status === 'connected'
                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'
                      : 'bg-red-950/60 text-red-300 border border-red-800/60'
                  }`}
                >
                  {health?.database?.status === 'connected' ? (
                    <>
                      <CheckCircle className="w-3 h-3" />
                      <span>Connected</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-3 h-3" />
                      <span>Disconnected</span>
                    </>
                  )}
                </span>
              </div>

              <div className="space-y-2 text-xs text-secondaryText">
                <div className="flex justify-between py-1 border-b border-borderCol/40">
                  <span>Engine:</span>
                  <strong className="text-primaryText uppercase">{health?.database?.engine}</strong>
                </div>
                <div className="flex justify-between py-1 border-b border-borderCol/40">
                  <span>Indexed Sources:</span>
                  <strong className="text-primaryText">{health?.database?.indexed_sources}</strong>
                </div>
                <div className="flex justify-between py-1 border-b border-borderCol/40">
                  <span>Stored Webpages:</span>
                  <strong className="text-primaryText">{health?.database?.indexed_documents}</strong>
                </div>
                <div className="flex justify-between py-1">
                  <span>Vector Chunks:</span>
                  <strong className="text-primaryText">{health?.database?.indexed_chunks}</strong>
                </div>
              </div>
            </div>

            {/* Ollama LLM Card */}
            <div className="p-5 rounded-xl bg-surface border border-borderCol shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-5 h-5 text-electric" />
                  <h3 className="text-sm font-semibold text-primaryText">Ollama & Qwen LLM</h3>
                </div>
                <span
                  className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                    llmStatus?.is_reachable
                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'
                      : 'bg-amber-950/60 text-amber-300 border border-amber-800/60'
                  }`}
                >
                  {llmStatus?.is_reachable ? (
                    <>
                      <CheckCircle className="w-3 h-3" />
                      <span>Online</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-3 h-3" />
                      <span>Offline</span>
                    </>
                  )}
                </span>
              </div>

              <div className="space-y-2 text-xs text-secondaryText">
                <div className="flex justify-between py-1 border-b border-borderCol/40">
                  <span>Base URL:</span>
                  <code className="text-primaryText text-[11px]">{llmStatus?.base_url}</code>
                </div>
                <div className="flex justify-between py-1 border-b border-borderCol/40">
                  <span>Target Model:</span>
                  <strong className="text-lavender-soft">{llmStatus?.configured_model}</strong>
                </div>
                <div className="flex justify-between py-1 border-b border-borderCol/40">
                  <span>Model Ready:</span>
                  <strong className={llmStatus?.model_available ? 'text-emerald-400' : 'text-amber-400'}>
                    {llmStatus?.model_available ? 'Ready' : 'Not Pulled'}
                  </strong>
                </div>
                <div className="flex justify-between py-1">
                  <span>Vector Dimension:</span>
                  <strong className="text-primaryText">{llmStatus?.vector_dimension}D</strong>
                </div>
              </div>
            </div>
          </div>

          {/* Setup / Instructions Banner when Ollama is offline */}
          {!llmStatus?.is_reachable && (
            <div className="p-5 rounded-xl bg-amethyst-dark border border-amber-800/60 text-xs">
              <div className="flex items-center space-x-2 text-amber-300 font-semibold mb-2">
                <Terminal className="w-4 h-4" />
                <span>Ollama Setup Instructions</span>
              </div>
              <p className="text-secondaryText mb-3 leading-relaxed">
                The local Ollama server is currently offline. Rule-based answers and verified KBN University FAQs are fully active.
                To activate local natural-language generation with Qwen, start Ollama and pull the models:
              </p>
              <div className="bg-mainBg p-3 rounded-lg border border-borderCol font-mono text-[11px] text-lavender-soft space-y-1">
                <div># Start the Ollama background daemon</div>
                <div className="text-primaryText">ollama serve</div>
                <div className="pt-1.5"># Pull the configured Qwen model</div>
                <div className="text-primaryText">ollama pull {llmStatus?.configured_model || 'qwen2.5:7b'}</div>
                <div className="pt-1.5"># Pull the nomic embedding model</div>
                <div className="text-primaryText">ollama pull {llmStatus?.configured_embedding_model || 'nomic-embed-text'}</div>
              </div>
            </div>
          )}

          {/* Installed Models */}
          <div className="p-5 rounded-xl bg-surface border border-borderCol shadow-sm">
            <h3 className="text-sm font-semibold text-lavender-soft uppercase tracking-wider mb-2">
              Installed Models on Host ({llmStatus?.installed_models?.length || 0})
            </h3>
            {llmStatus?.installed_models?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {llmStatus.installed_models.map((mod, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 rounded bg-amethyst-deep text-primaryText border border-borderCol text-xs"
                  >
                    {mod}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-secondaryText">No models detected in Ollama registry.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
