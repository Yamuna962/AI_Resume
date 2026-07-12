import { useState } from 'react';
import api from '@/lib/axios';
import { getApiErrorMessage } from '@/lib/api-error';
import { useAnalysisStore } from '@/stores/analysis.store';
import {
  type AnalysisRunResponse,
  type AtsAnalysisResult,
  unwrapAnalysisRunResponse,
} from '@/types/analysis';

export function useAnalysis() {
  const [error, setError] = useState<string | null>(null);
  const { setAnalysis, setIsAnalyzing, isAnalyzing } = useAnalysisStore();

  const runAnalysis = async (resumeId: string, jobDescription: string): Promise<AtsAnalysisResult> => {
    try {
      setIsAnalyzing(true);
      setError(null);

      const response = await api.post<AnalysisRunResponse>('/analysis/run', {
        resume_id: resumeId,
        job_description: jobDescription,
      });
      const analysis = unwrapAnalysisRunResponse(response.data);

      setAnalysis(analysis);
      return analysis;
    } catch (error: unknown) {
      setError(getApiErrorMessage(error, 'An error occurred during analysis'));
      throw error;
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getAnalysis = async (id: string): Promise<AtsAnalysisResult> => {
    try {
      setError(null);
      const response = await api.get<AtsAnalysisResult>(`/analysis/${id}`);
      setAnalysis(response.data);
      return response.data;
    } catch (error: unknown) {
      setError(getApiErrorMessage(error, 'Failed to fetch analysis'));
      throw error;
    }
  };

  return { runAnalysis, getAnalysis, isAnalyzing, error };
}
