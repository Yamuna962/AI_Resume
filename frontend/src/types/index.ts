export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Resume {
  id: string;
  filename: string;
  storage_url: string;
  created_at: string;
}

export interface MatchedSkill {
  skill: string;
  match_type: 'exact' | 'semantic' | 'vector';
}

export interface Suggestion {
  title: string;
  description: string;
}

export interface AnalysisResult {
  id: string;
  resume_score: number;
  ats_score: number;
  skill_match_percentage: number;
  matched_skills: MatchedSkill[];
  missing_skills: string[];
  strengths: string[];
  weaknesses: string[];
  improvement_areas: string[];
  suggestions: Suggestion[];
  project_suggestions: string[];
  exact_match_score: number;
  vector_similarity_score: number;
  semantic_match_score: number;
  rewritten_summary: string;
  rewritten_resume: string;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  resume_filename: string | null;
  job_description: string;
  ats_score: number | null;
  resume_score: number | null;
  skill_match_percentage: number | null;
  status: string;
  created_at: string;
}
