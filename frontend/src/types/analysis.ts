export interface AnalysisSuggestion {
  title: string;
  description: string;
  priority?: string;
}

export interface AnalysisPrioritizedRecommendations {
  high_priority?: string[];
  medium_priority?: string[];
  low_priority?: string[];
}

export interface AnalysisBreakdown {
  keyword?: number;
  semantic?: number;
  experience?: number;
  responsibilities?: number;
  projects?: number;
  formatting?: number;
  education?: number;
  certifications?: number;
  domain?: number;
  transferable?: number;
}

export interface AnalysisMatchBreakdown {
  required_skills?: number;
  responsibilities?: number;
  experience?: number;
  projects?: number;
  preferred_skills?: number;
}

export interface AnalysisDetailedScores {
  skill_match_score?: number;
  experience_match_score?: number;
  project_match_score?: number;
  education_match_score?: number;
  certification_match_score?: number;
  formatting_score?: number;
  semantic_similarity_score?: number;
  required_skill_coverage?: number;
  preferred_skill_coverage?: number;
  responsibilities_match_score?: number;
  domain_match_score?: number;
  transferable_skill_score?: number;
  critical_skill_coverage?: number;
  business_impact_score?: number;
  leadership_score?: number;
}

export type AnalysisMatchWeightKey =
  | 'required_skills'
  | 'responsibilities'
  | 'experience'
  | 'projects'
  | 'preferred_skills';

export type AnalysisAtsWeightKey =
  | 'required_skills'
  | 'semantic'
  | 'experience'
  | 'responsibilities'
  | 'projects'
  | 'formatting'
  | 'education'
  | 'certifications'
  | 'domain'
  | 'transferable';

export type AnalysisApplicableSectionKey =
  | 'responsibilities'
  | 'projects'
  | 'preferred_skills'
  | 'education'
  | 'certifications';

export interface AnalysisScoreWeights {
  match_weights?: Partial<Record<AnalysisMatchWeightKey, number>>;
  ats_weights?: Partial<Record<AnalysisAtsWeightKey, number>>;
  applicable_sections?: Partial<Record<AnalysisApplicableSectionKey, boolean>>;
}

export interface AtsAnalysisResult {
  id?: string;
  status?: string;
  created_at?: string;
  ats_score?: number;
  match_score?: number;
  confidence_score?: number;
  keyword_score?: number;
  semantic_score?: number;
  experience_score?: number;
  project_score?: number;
  formatting_score?: number;
  education_score?: number;
  matched_skills?: string[];
  missing_skills?: string[];
  matched_projects?: string[];
  matched_responsibilities?: string[];
  extra_skills?: string[];
  strengths?: string[];
  weaknesses?: string[];
  recommendations?: string[];
  recommendations_prioritized?: AnalysisPrioritizedRecommendations;
  resume_summary?: string;
  project_improvements?: string[];
  interview_tips?: string[];
  breakdown?: AnalysisBreakdown;
  score_breakdown?: AnalysisBreakdown;
  match_breakdown?: AnalysisMatchBreakdown;
  score_weights?: AnalysisScoreWeights;
  detailed_scores?: AnalysisDetailedScores;
  reasoning?: string;
  skill_match_percentage?: number;
  resume_score?: number;
  suggestions?: AnalysisSuggestion[];
  rewritten_summary?: string;
  rewritten_resume?: string;
  rewritten_experience?: string[];
  matched_required_skills?: string[];
  matched_preferred_skills?: string[];
  transferable_skills?: string[];
  score_explanations?: Record<string, string>;
}

export interface WrappedAnalysisRunResponse {
  result: AtsAnalysisResult;
}

export type AnalysisRunResponse = AtsAnalysisResult | WrappedAnalysisRunResponse;

export interface ResumeUploadResponse {
  success?: boolean;
  resume_id?: string;
  id?: string;
  filename?: string;
  storage_url?: string | null;
  file_size?: number | null;
  text_extracted?: boolean;
  message?: string;
}

export const unwrapAnalysisRunResponse = (
  response: AnalysisRunResponse,
): AtsAnalysisResult => ('result' in response ? response.result : response);
