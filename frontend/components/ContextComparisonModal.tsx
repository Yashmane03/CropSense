'use client';

import React, { useState } from 'react';
import { AnalysisRecord, FieldObservation, LocationInput, reanalyzeCropImage, ReanalyzeSuccessResponse } from '@/lib/api';

interface ContextComparisonModalProps {
  initialAnalysis: AnalysisRecord;
  onClose: () => void;
  onReanalysisComplete: (result: ReanalyzeSuccessResponse) => void;
}

export default function ContextComparisonModal({
  initialAnalysis,
  onClose,
  onReanalysisComplete,
}: ContextComparisonModalProps) {
  const [fieldObs, setFieldObs] = useState<FieldObservation>({
    crop: 'Tomato',
    growth_stage: initialAnalysis.field_observations.growth_stage || 'vegetative',
    soil_condition: initialAnalysis.field_observations.soil_condition === 'wet' ? 'dry' : 'wet',
    irrigation: initialAnalysis.field_observations.irrigation === 'excessive' ? 'none' : 'excessive',
    pests: initialAnalysis.field_observations.pests || 'no',
    recent_rainfall: initialAnalysis.field_observations.recent_rainfall === 'heavy' ? 'low' : 'heavy',
  });

  const [location, setLocation] = useState<LocationInput>({
    city_search: initialAnalysis.weather_data.location_name || 'Pune',
    latitude: initialAnalysis.weather_data.latitude,
    longitude: initialAnalysis.weather_data.longitude,
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [imgError, setImgError] = useState<boolean>(false);

  const resolveImageUrl = (url?: string) => {
    if (!url) return '';
    if (url.startsWith('/uploads')) {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      return `${baseUrl}${url}`;
    }
    return url;
  };

  const finalImgSrc = resolveImageUrl(initialAnalysis.image_url);

  const handleRunReanalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await reanalyzeCropImage(
        initialAnalysis.analysis_id,
        initialAnalysis.image_url,
        fieldObs,
        location
      );
      onReanalysisComplete(response);
    } catch (err: any) {
      setError(err.message || 'Failed to re-analyze context.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-2xl w-full p-6 space-y-5">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-base font-bold text-slate-900">Change Context & Re-analyze</h2>
            <p className="text-xs text-slate-500">Reuses original crop image with updated field parameters</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-sm font-bold"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleRunReanalysis} className="space-y-4">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* INITIAL CONTEXT READONLY */}
            <div className="bg-slate-50 p-4 rounded border border-slate-200 space-y-2 text-xs">
              <span className="font-bold text-slate-500 uppercase tracking-wide block">Initial context</span>
              
              <div className="h-28 rounded overflow-hidden bg-slate-200 flex items-center justify-center">
                {!imgError && finalImgSrc ? (
                  <img
                    src={finalImgSrc}
                    alt="Initial foliage sample"
                    onError={() => setImgError(true)}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-[11px] font-semibold text-slate-400 text-center p-2">
                    Crop image unavailable
                  </span>
                )}
              </div>

              <div className="space-y-1 text-slate-700">
                <div>Soil: <strong className="capitalize">{initialAnalysis.field_observations.soil_condition}</strong></div>
                <div>Irrigation: <strong className="capitalize">{initialAnalysis.field_observations.irrigation}</strong></div>
                <div>Rainfall: <strong className="capitalize">{initialAnalysis.field_observations.recent_rainfall}</strong></div>
              </div>

              <div className="pt-2 border-t border-slate-200 text-slate-900 font-bold">
                Assessment: {initialAnalysis.final_assessment}
              </div>
            </div>

            {/* UPDATED CONTEXT INPUTS */}
            <div className="bg-white p-4 rounded border-2 border-emerald-700 space-y-3 text-xs">
              <span className="font-bold text-emerald-800 uppercase tracking-wide block">New field context</span>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Soil condition</label>
                <select
                  value={fieldObs.soil_condition}
                  onChange={(e) => setFieldObs({ ...fieldObs, soil_condition: e.target.value as any })}
                  className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1.5 focus:outline-none focus:border-emerald-700"
                >
                  <option value="dry">Dry</option>
                  <option value="normal">Normal</option>
                  <option value="wet">Wet / Waterlogged</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Irrigation</label>
                <select
                  value={fieldObs.irrigation}
                  onChange={(e) => setFieldObs({ ...fieldObs, irrigation: e.target.value as any })}
                  className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1.5 focus:outline-none focus:border-emerald-700"
                >
                  <option value="none">None</option>
                  <option value="normal">Normal</option>
                  <option value="excessive">Excessive</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Recent rainfall</label>
                <select
                  value={fieldObs.recent_rainfall}
                  onChange={(e) => setFieldObs({ ...fieldObs, recent_rainfall: e.target.value as any })}
                  className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1.5 focus:outline-none focus:border-emerald-700"
                >
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="heavy">Heavy</option>
                </select>
              </div>

              <span className="block text-[11px] text-slate-400">Reuses uploaded foliage image</span>
            </div>

          </div>

          {error && <p className="text-xs text-red-600 font-medium">{error}</p>}

          {/* Action buttons */}
          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded border border-slate-300 text-slate-600 text-xs font-medium hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 rounded bg-emerald-800 hover:bg-emerald-900 text-white text-xs font-bold transition-colors disabled:opacity-50"
            >
              {loading ? 'Re-evaluating...' : 'Re-analyze Context'}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
