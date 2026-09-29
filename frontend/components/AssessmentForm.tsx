'use client';

import React, { useState, useRef } from 'react';
import { FieldObservation, LocationInput, analyzeCropImage, QualityCheckError } from '@/lib/api';
import WeatherWidget from './WeatherWidget';

interface AssessmentFormProps {
  onAnalysisSuccess: (response: any) => void;
}

export default function AssessmentForm({ onAnalysisSuccess }: AssessmentFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [fieldObs, setFieldObs] = useState<FieldObservation>({
    crop: 'Tomato',
    growth_stage: 'vegetative',
    soil_condition: 'wet',
    irrigation: 'excessive',
    pests: 'no',
    recent_rainfall: 'heavy',
  });

  const [location, setLocation] = useState<LocationInput>({});

  const [loading, setLoading] = useState<boolean>(false);
  const [qualityError, setQualityError] = useState<QualityCheckError | null>(null);
  const [generalError, setGeneralError] = useState<string | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setQualityError(null);
    setGeneralError(null);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setQualityError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setGeneralError('Please upload a crop leaf image.');
      return;
    }

    setLoading(true);
    setQualityError(null);
    setGeneralError(null);

    try {
      const response = await analyzeCropImage(selectedFile, fieldObs, location);

      if (!response.success && response.stage === 'image_quality_check') {
        setQualityError(response as QualityCheckError);
        setLoading(false);
        return;
      }

      onAnalysisSuccess(response);
    } catch (err: any) {
      setGeneralError(err.message || 'Analysis request failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      
      {/* Two Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* LEFT COLUMN: Upload crop image */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h2 className="text-sm font-bold text-slate-900">Upload crop image</h2>
            {previewUrl && (
              <button
                type="button"
                onClick={handleClearImage}
                className="text-xs text-slate-400 hover:text-red-600"
              >
                Clear
              </button>
            )}
          </div>

          <input
            type="file"
            ref={fileInputRef}
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileSelect(e.target.files[0]);
              }
            }}
          />

          {!previewUrl ? (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="border border-dashed border-slate-300 bg-slate-50 hover:bg-slate-100/70 rounded-lg p-6 text-center cursor-pointer transition-colors space-y-2"
            >
              <div className="text-slate-400 text-sm">
                Drop crop image here, or <span className="text-emerald-800 font-semibold underline">browse</span>
              </div>
              <p className="text-[11px] text-slate-400">JPG, PNG, or WEBP crop foliage photo</p>
            </div>
          ) : (
            <div className="rounded-lg overflow-hidden border border-slate-200 relative bg-slate-900 h-52">
              <img src={previewUrl} alt="Crop preview" className="w-full h-full object-cover" />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-2 right-2 bg-slate-900/80 text-white text-xs px-2.5 py-1 rounded"
              >
                Change
              </button>
            </div>
          )}

          {/* Quality check error status */}
          {qualityError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-xs text-red-800 space-y-1">
              <p className="font-semibold text-red-900">{qualityError.message}</p>
              <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                {qualityError.issues.map((issue, idx) => (
                  <li key={idx}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Field context */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h2 className="text-sm font-bold text-slate-900">Field context</h2>
            <span className="text-xs font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded">
              Crop: Tomato
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            {/* Growth stage */}
            <div>
              <label className="block text-slate-600 font-medium mb-1">Growth stage</label>
              <select
                value={fieldObs.growth_stage}
                onChange={(e) => setFieldObs({ ...fieldObs, growth_stage: e.target.value as any })}
                className="w-full bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-emerald-700"
              >
                <option value="early">Early / Seedling</option>
                <option value="vegetative">Vegetative</option>
                <option value="flowering">Flowering</option>
                <option value="fruiting">Fruiting</option>
              </select>
            </div>

            {/* Soil condition */}
            <div>
              <label className="block text-slate-600 font-medium mb-1">Soil condition</label>
              <select
                value={fieldObs.soil_condition}
                onChange={(e) => setFieldObs({ ...fieldObs, soil_condition: e.target.value as any })}
                className="w-full bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-emerald-700"
              >
                <option value="dry">Dry</option>
                <option value="normal">Normal</option>
                <option value="wet">Wet / Waterlogged</option>
              </select>
            </div>

            {/* Recent irrigation */}
            <div>
              <label className="block text-slate-600 font-medium mb-1">Recent irrigation</label>
              <select
                value={fieldObs.irrigation}
                onChange={(e) => setFieldObs({ ...fieldObs, irrigation: e.target.value as any })}
                className="w-full bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-emerald-700"
              >
                <option value="none">None</option>
                <option value="normal">Normal</option>
                <option value="excessive">Excessive</option>
              </select>
            </div>

            {/* Pests observed */}
            <div>
              <label className="block text-slate-600 font-medium mb-1">Pests observed</label>
              <select
                value={fieldObs.pests}
                onChange={(e) => setFieldObs({ ...fieldObs, pests: e.target.value as any })}
                className="w-full bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-emerald-700"
              >
                <option value="no">No</option>
                <option value="yes">Yes</option>
                <option value="unsure">Unsure</option>
              </select>
            </div>

            {/* Recent rainfall */}
            <div className="col-span-2">
              <label className="block text-slate-600 font-medium mb-1">Recent rainfall</label>
              <select
                value={fieldObs.recent_rainfall}
                onChange={(e) => setFieldObs({ ...fieldObs, recent_rainfall: e.target.value as any })}
                className="w-full bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-emerald-700"
              >
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="heavy">Heavy</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Weather Context below the two columns */}
      <WeatherWidget
        onLocationChange={(lat, lon, city) => {
          setLocation({ latitude: lat, longitude: lon, city_search: city });
        }}
      />

      {generalError && (
        <p className="text-xs text-red-600 font-medium">{generalError}</p>
      )}

      {/* Prominent Green Analyze Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-emerald-800 hover:bg-emerald-900 text-white font-bold text-sm rounded transition-colors disabled:opacity-50"
      >
        {loading ? 'Analyzing Crop...' : 'Analyze Crop'}
      </button>

    </form>
  );
}
