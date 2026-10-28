import React, { useState } from 'react';
import { Globe, Plus } from 'lucide-react';
import Button from '../common/Button';

export default function WebsiteForm({ onAddSource, isSubmitting }) {
  const [url, setUrl] = useState('https://www.kbn.university/');
  const [name, setName] = useState('KBN University Portal');
  const [description, setDescription] = useState('Official university website');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    onAddSource({ url: url.trim(), name: name.trim(), description: description.trim() });
  };

  return (
    <form onSubmit={handleSubmit} className="p-5 rounded-xl bg-surface border border-borderCol mb-6 shadow-sm">
      <div className="flex items-center space-x-2 mb-4">
        <Globe className="w-5 h-5 text-electric" />
        <h3 className="text-base font-semibold text-primaryText">Register Knowledge Source</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs font-medium text-secondaryText mb-1.5">
            Website Starting URL *
          </label>
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.kbn.university/"
            className="w-full px-3.5 py-2 rounded-lg bg-mainBg border border-borderCol text-sm text-primaryText placeholder-secondaryText/50 focus:outline-none focus:border-electric"
          />
          <p className="mt-1 text-[11px] text-secondaryText/70">
            Enforces domain restriction to <code>kbn.university</code> with SSRF validation.
          </p>
        </div>

        <div>
          <label className="block text-xs font-medium text-secondaryText mb-1.5">
            Source Display Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. KBN Admissions & Faculties"
            className="w-full px-3.5 py-2 rounded-lg bg-mainBg border border-borderCol text-sm text-primaryText placeholder-secondaryText/50 focus:outline-none focus:border-electric"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting || !url.trim()}
          icon={Plus}
        >
          {isSubmitting ? 'Starting Crawl...' : 'Index Website'}
        </Button>
      </div>
    </form>
  );
}
