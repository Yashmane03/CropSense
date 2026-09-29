'use client';

import React, { useState } from 'react';
import { AnalysisRecord } from '@/lib/api';

interface ResultsViewProps {
  analysis: AnalysisRecord;
  onReanalyzeClick: () => void;
  onViewHistoryClick: () => void;
  onReset: () => void;
  comparisonBanner?: {
    initialAssessment: string;
    updatedAssessment: string;
    message: string;
  } | null;
}

export default function ResultsView({
  analysis,
  onReanalyzeClick,
  onViewHistoryClick,
  onReset,
  comparisonBanner,
}: ResultsViewProps) {
  const {
    crop,
    final_assessment,
    confidence,
    is_uncertain,
    image_url,
    visual_predictions,
    weather_data,
    field_observations,
    evidence,
    advisory,
  } = analysis;

  const [imageError, setImageError] = useState(false);

  // Helper function to resolve relative /uploads/ URLs to full backend URL if needed
  const resolveImageUrl = (url?: string) => {
    if (!url) return '';
    if (url.startsWith('/uploads')) {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      return `${baseUrl}${url}`;
    }
    return url;
  };

  const finalImgSrc = resolveImageUrl(image_url);

  return (
    <div className="space-y-6">

      {/* Comparison Banner if Context Updated */}
      {comparisonBanner && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg space-y-1">
          <p className="text-xs font-bold text-emerald-900 uppercase tracking-wide">Context Comparison</p>
          <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-slate-800">
            <span>INITIAL ASSESSMENT: <strong className="text-slate-900">{comparisonBanner.initialAssessment}</strong></span>
            <span>→</span>
            <span>UPDATED ASSESSMENT: <strong className="text-emerald-800">{comparisonBanner.updatedAssessment}</strong></span>
          </div>
          <p className="text-xs text-emerald-800 font-medium pt-1">
            Assessment updated based on new contextual evidence.
          </p>
        </div>
      )}

      {/* Top Header */}
      <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Crop Assessment</span>
          <h1 className="text-2xl font-bold text-slate-900">{final_assessment}</h1>
        </div>

        <div className="flex items-center space-x-2">
          <span
            className={`px-2.5 py-1 rounded text-xs font-bold ${
              is_uncertain || confidence === 'Uncertain'
                ? 'bg-amber-100 text-amber-900 border border-amber-200'
                : confidence === 'High'
                ? 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                : 'bg-slate-100 text-slate-800 border border-slate-200'
            }`}
          >
            {is_uncertain ? 'Assessment Uncertain' : `${confidence} Confidence`}
          </span>
        </div>
      </div>

      {/* Top Section: Left Image, Right Assessment Summary */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        
        {/* Left: Uploaded Image */}
        <div className="md:col-span-4 bg-white p-3 border border-slate-200 rounded-lg">
          <div className="h-56 rounded overflow-hidden bg-slate-100 flex items-center justify-center">
            {!imageError && finalImgSrc ? (
              <img
                src={finalImgSrc}
                alt="Crop leaf sample"
                onError={() => setImageError(true)}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="text-xs font-semibold text-slate-400 text-center p-4">
                Crop image unavailable
              </div>
            )}
          </div>
          <span className="block text-[11px] text-slate-400 mt-2 text-center">Crop: {crop}</span>
        </div>

        {/* Right: Overview */}
        <div className="md:col-span-8 bg-white p-5 border border-slate-200 rounded-lg space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">{final_assessment}</h2>
            <p className="text-xs text-slate-600 mt-1">
              {is_uncertain
                ? 'Visual predictions and contextual evidence yielded close or ambiguous scores. Expert review recommended.'
                : `Diagnosis established through visual foliage signals combined with real-time field weather and soil conditions.`}
            </p>
          </div>

          <div className="flex flex-wrap gap-2 pt-2">
            <button
              onClick={onReanalyzeClick}
              className="px-4 py-2 bg-emerald-800 hover:bg-emerald-900 text-white text-xs font-bold rounded transition-colors"
            >
              Change Context & Re-analyze
            </button>
            <button
              onClick={onViewHistoryClick}
              className="px-3.5 py-2 bg-white border border-slate-300 text-slate-700 text-xs font-medium rounded hover:bg-slate-50 transition-colors"
            >
              View History
            </button>
            <button
              onClick={onReset}
              className="px-3.5 py-2 bg-slate-100 text-slate-600 text-xs font-medium rounded hover:bg-slate-200 transition-colors"
            >
              New Assessment
            </button>
          </div>
        </div>
      </div>

      {/* Three Compact Sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* 1. Visual evidence */}
        <div className="bg-white p-4 border border-slate-200 rounded-lg space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-1">
            1. Visual Evidence
          </h3>
          <div className="space-y-1.5 text-xs">
            {Object.entries(evidence.posterior_probabilities || visual_predictions.probabilities || {}).map(
              ([cls, prob]) => {
                const name = cls.replace('Tomato___', '').replace('_', ' ');
                const pct = (prob * 100).toFixed(0);
                return (
                  <div key={cls} className="flex justify-between items-center text-slate-700">
                    <span>{name}</span>
                    <span className="font-mono font-semibold">{pct}%</span>
                  </div>
                );
              }
            )}
          </div>
        </div>

        {/* 2. Weather context */}
        <div className="bg-white p-4 border border-slate-200 rounded-lg space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-1">
            2. Weather Context
          </h3>
          <div className="space-y-1.5 text-xs text-slate-700">
            <div className="flex justify-between">
              <span className="text-slate-500">Location:</span>
              <span className="font-medium truncate max-w-[140px]">{weather_data.location_name || 'Field'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Temperature:</span>
              <span className="font-semibold">{weather_data.temperature_c}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Humidity:</span>
              <span className="font-semibold">{weather_data.humidity_percent}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Recent Rain:</span>
              <span className="font-semibold">{weather_data.recent_rainfall_mm} mm</span>
            </div>
          </div>
        </div>

        {/* 3. Field context */}
        <div className="bg-white p-4 border border-slate-200 rounded-lg space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-1">
            3. Field Context
          </h3>
          <div className="space-y-1.5 text-xs text-slate-700">
            <div className="flex justify-between">
              <span className="text-slate-500">Growth Stage:</span>
              <span className="font-medium capitalize">{field_observations.growth_stage}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Soil Condition:</span>
              <span className="font-medium capitalize">{field_observations.soil_condition}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Irrigation:</span>
              <span className="font-medium capitalize">{field_observations.irrigation}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Pests Observed:</span>
              <span className="font-medium capitalize">{field_observations.pests}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Why this assessment? */}
      <div className="bg-white p-5 border border-slate-200 rounded-lg space-y-3">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
          Why this assessment?
        </h3>
        <ul className="space-y-1.5 text-xs text-slate-700">
          {evidence.why_this_assessment?.map((point, i) => (
            <li key={i} className="flex items-start space-x-2">
              <span className="text-emerald-700 font-bold">•</span>
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommended next steps */}
      <div className="bg-white p-5 border border-slate-200 rounded-lg space-y-4">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
          Recommended next steps
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <h4 className="font-semibold text-slate-800 mb-1">Field Monitoring</h4>
            <ul className="list-disc pl-4 space-y-1 text-slate-600">
              {advisory.monitoring?.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-slate-800 mb-1">Immediate Actions</h4>
            <ul className="list-disc pl-4 space-y-1 text-slate-600">
              {advisory.field_actions?.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        </div>

        {advisory.escalation && advisory.escalation.length > 0 && (
          <div className="p-3 bg-amber-50 rounded border border-amber-200 text-xs text-amber-900">
            <span className="font-semibold block mb-0.5">Escalation Criteria</span>
            <ul className="list-disc pl-4 space-y-0.5 text-amber-800 text-[11px]">
              {advisory.escalation.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

    </div>
  );
}
