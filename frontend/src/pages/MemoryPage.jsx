import React, { useState, useEffect } from 'react';
import { Brain, RefreshCw, Plus } from 'lucide-react';
import MemoryList from '../components/memory/MemoryList';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { memoryService } from '../services/memoryService';

export default function MemoryPage() {
  const [memories, setMemories] = useState([]);
  const [isEnabled, setIsEnabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Add memory modal state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');
  const [category, setCategory] = useState('preference');

  const fetchData = async () => {
    try {
      setError(null);
      const res = await memoryService.getMemories();
      setMemories(res.memories || []);
      setIsEnabled(res.enabled !== false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggle = async (enabled) => {
    try {
      setError(null);
      await memoryService.toggleMemory(enabled);
      setIsEnabled(enabled);
      if (!enabled) {
        setMemories([]);
      } else {
        await fetchData();
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (memoryId) => {
    try {
      setError(null);
      await memoryService.deleteMemory(memoryId);
      setMemories((prev) => prev.filter((m) => m.id !== memoryId));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleClearAll = async () => {
    if (window.confirm('Purge all stored conversational memory for your session?')) {
      try {
        setError(null);
        await memoryService.clearAll();
        setMemories([]);
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleSaveNewMemory = async (e) => {
    e.preventDefault();
    if (!key.trim() || !value.trim()) return;

    try {
      setError(null);
      await memoryService.addMemory(key.trim(), value.trim(), category);
      setIsAddModalOpen(false);
      setKey('');
      setValue('');
      await fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 max-w-4xl mx-auto w-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-primaryText flex items-center space-x-2">
            <Brain className="w-5 h-5 text-electric" />
            <span>Conversational Memory</span>
          </h2>
          <p className="text-xs text-secondaryText mt-1">
            Inspect, customize, or disable long-term student preferences and conversation summaries.
          </p>
        </div>

        <Button size="sm" variant="secondary" onClick={fetchData} icon={RefreshCw}>
          Refresh
        </Button>
      </div>

      <ErrorMessage message={error} onRetry={fetchData} className="mb-6" />

      {loading ? (
        <div className="p-12 text-center">
          <LoadingSpinner size="lg" />
          <p className="text-xs text-secondaryText mt-2">Loading memory preferences...</p>
        </div>
      ) : (
        <MemoryList
          memories={memories}
          isEnabled={isEnabled}
          onToggleMemory={handleToggle}
          onDeleteMemory={handleDelete}
          onClearAll={handleClearAll}
          onOpenAddModal={() => setIsAddModalOpen(true)}
        />
      )}

      {/* Add Memory Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Custom Memory Preference"
      >
        <form onSubmit={handleSaveNewMemory} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-secondaryText mb-1">
              Memory Key / Topic *
            </label>
            <input
              type="text"
              required
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="e.g. intended_major, campus_interest"
              className="w-full px-3 py-2 rounded-lg bg-mainBg border border-borderCol text-sm text-primaryText focus:outline-none focus:border-electric"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-secondaryText mb-1">
              Memory Content / Fact *
            </label>
            <textarea
              required
              rows={3}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="e.g. Interested in B.Tech Computer Science and engineering hostel facilities"
              className="w-full px-3 py-2 rounded-lg bg-mainBg border border-borderCol text-sm text-primaryText focus:outline-none focus:border-electric resize-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-secondaryText mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-mainBg border border-borderCol text-sm text-primaryText focus:outline-none focus:border-electric"
            >
              <option value="preference">Preference</option>
              <option value="profile">Student Profile</option>
              <option value="fact">Context Fact</option>
            </select>
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <Button variant="ghost" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" icon={Plus}>
              Save Preference
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
