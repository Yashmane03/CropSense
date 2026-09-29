'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import AssessmentForm from '@/components/AssessmentForm';
import ResultsView from '@/components/ResultsView';
import ContextComparisonModal from '@/components/ContextComparisonModal';
import { AnalysisRecord, ReanalyzeSuccessResponse } from '@/lib/api';

export default function HomePage() {
  const router = useRouter();
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisRecord | null>(null);
  const [showReanalyzeModal, setShowReanalyzeModal] = useState<boolean>(false);
  const [comparisonBanner, setComparisonBanner] = useState<{
    initialAssessment: string;
    updatedAssessment: string;
    message: string;
  } | null>(null);

  const handleAnalysisSuccess = (response: any) => {
    setCurrentAnalysis(response.analysis);
    setComparisonBanner(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleReanalysisComplete = (result: ReanalyzeSuccessResponse) => {
    if (result.initial_record) {
      setComparisonBanner({
        initialAssessment: result.initial_record.final_assessment,
        updatedAssessment: result.updated_record.final_assessment,
        message: result.message,
      });
    }
    setCurrentAnalysis(result.updated_record);
    setShowReanalyzeModal(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleReset = () => {
    setCurrentAnalysis(null);
    setComparisonBanner(null);
  };

  return (
    <div className="space-y-6">
      {!currentAnalysis ? (
        <AssessmentForm onAnalysisSuccess={handleAnalysisSuccess} />
      ) : (
        <ResultsView
          analysis={currentAnalysis}
          onReanalyzeClick={() => setShowReanalyzeModal(true)}
          onViewHistoryClick={() => router.push('/history')}
          onReset={handleReset}
          comparisonBanner={comparisonBanner}
        />
      )}

      {showReanalyzeModal && currentAnalysis && (
        <ContextComparisonModal
          initialAnalysis={currentAnalysis}
          onClose={() => setShowReanalyzeModal(false)}
          onReanalysisComplete={handleReanalysisComplete}
        />
      )}
    </div>
  );
}
