'use client';

import React, { useState, useEffect } from 'react';
import { fetchAnalysisHistory, AnalysisRecord } from '@/lib/api';
import ResultsView from '@/components/ResultsView';

function FormattedDate({ dateString }: { dateString: string }) {
  const [formatted, setFormatted] = useState<string>('');
  useEffect(() => {
    try {
      setFormatted(
        new Date(dateString).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      );
    } catch {
      setFormatted(dateString);
    }
  }, [dateString]);
  return <span suppressHydrationWarning>{formatted || dateString.substring(0, 10)}</span>;
}

function HistoryThumbnail({ url, alt }: { url: string; alt: string }) {
  const [error, setError] = useState(false);

  const resolveImageUrl = (src?: string) => {
    if (!src) return '';
    if (src.startsWith('/uploads')) {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      return `${baseUrl}${src}`;
    }
    return src;
  };

  const finalSrc = resolveImageUrl(url);

  if (error || !finalSrc) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-400 text-[9px] text-center p-0.5 font-semibold">
        Crop image unavailable
      </div>
    );
  }

  return (
    <img
      src={finalSrc}
      alt={alt}
      onError={() => setError(true)}
      className="w-full h-full object-cover"
    />
  );
}

export default function HistoryPage() {
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<AnalysisRecord | null>(null);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const records = await fetchAnalysisHistory();
      setHistory(records);
    } catch (err: any) {
      setError(err.message || 'Failed to load assessment history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  if (selectedRecord) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => setSelectedRecord(null)}
          className="text-xs font-semibold text-emerald-800 hover:underline flex items-center space-x-1"
        >
          ← Back to History List
        </button>

        <ResultsView
          analysis={selectedRecord}
          onReanalyzeClick={() => setSelectedRecord(null)}
          onViewHistoryClick={() => setSelectedRecord(null)}
          onReset={() => setSelectedRecord(null)}
        />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Previous Assessments</h1>
          <p className="text-xs text-slate-500">Stored diagnostic history retrieved from Supabase / DB</p>
        </div>

        <button
          onClick={loadHistory}
          disabled={loading}
          className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded transition-colors"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error ? (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded text-xs text-amber-900">
          {error}
        </div>
      ) : loading ? (
        <p className="text-xs text-slate-400 py-8 text-center">Loading stored assessments...</p>
      ) : history.length === 0 ? (
        <div className="bg-white p-8 rounded border border-slate-200 text-center text-xs text-slate-500 space-y-2">
          <p>No previous assessment records found.</p>
          <a href="/" className="inline-block text-emerald-800 font-semibold underline">
            Run an assessment
          </a>
        </div>
      ) : (
        /* Table of Previous Assessments */
        <div className="bg-white rounded border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-4">Thumbnail</th>
                  <th className="py-2.5 px-4">Date</th>
                  <th className="py-2.5 px-4">Crop</th>
                  <th className="py-2.5 px-4">Assessment</th>
                  <th className="py-2.5 px-4">Confidence</th>
                  <th className="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((record) => (
                  <tr
                    key={record.analysis_id}
                    onClick={() => setSelectedRecord(record)}
                    className="hover:bg-emerald-50/40 cursor-pointer transition-colors"
                  >
                    <td className="py-2 px-4">
                      <div className="w-10 h-10 rounded overflow-hidden bg-slate-100 border border-slate-200">
                        <HistoryThumbnail url={record.image_url} alt="Thumbnail" />
                      </div>
                    </td>
                    <td className="py-2 px-4 text-slate-600 font-medium whitespace-nowrap">
                      <FormattedDate dateString={record.created_at} />
                    </td>
                    <td className="py-2 px-4 text-slate-800 font-medium">{record.crop}</td>
                    <td className="py-2 px-4 text-slate-900 font-bold">{record.final_assessment}</td>
                    <td className="py-2 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                          record.confidence === 'High'
                            ? 'bg-emerald-100 text-emerald-800'
                            : record.is_uncertain
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-slate-100 text-slate-800'
                        }`}
                      >
                        {record.confidence}
                      </span>
                    </td>
                    <td className="py-2 px-4 text-right">
                      <span className="text-emerald-800 font-semibold hover:underline">
                        View
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
