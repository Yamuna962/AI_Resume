import { create } from 'zustand';
import type { AtsAnalysisResult } from '@/types/analysis';

interface AnalysisState {
  currentAnalysis: AtsAnalysisResult | null;
  isAnalyzing: boolean;
  setAnalysis: (analysis: AtsAnalysisResult | null) => void;
  setIsAnalyzing: (isAnalyzing: boolean) => void;
  clearAnalysis: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  currentAnalysis: null,
  isAnalyzing: false,
  setAnalysis: (analysis) => set({ currentAnalysis: analysis }),
  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),
  clearAnalysis: () => set({ currentAnalysis: null }),
}));
