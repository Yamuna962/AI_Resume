'use client';

import { useState, type FormEvent } from 'react';
import api from '@/lib/axios';
import { UploadAnalysisFormSection } from '@/components/organisms/upload/UploadAnalysisFormSection';
import { UploadAnalysisScoreSection } from '@/components/organisms/upload/UploadAnalysisScoreSection';
import { UploadAnalysisResultsSection } from '@/components/organisms/upload/UploadAnalysisResultsSection';
import {
  type AtsAnalysisResult,
  type ResumeUploadResponse,
  unwrapAnalysisRunResponse,
  type AnalysisRunResponse,
} from '@/types/analysis';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AtsAnalysisResult | null>(null);
  const [error, setError] = useState('');
  const [showRewrite, setShowRewrite] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file || !jobDesc.trim()) {
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await api.post<ResumeUploadResponse>('/resume/upload', formData, {
        headers: { 'Content-Type': undefined },
      });
      const resumeId = uploadResponse.data.resume_id ?? uploadResponse.data.id;

      if (!resumeId) {
        throw new Error('Failed to retrieve resume ID after upload.');
      }

      const analysisResponse = await api.post<AnalysisRunResponse>('/analysis/run', {
        resume_id: resumeId,
        job_description: jobDesc,
      });

      setResult(unwrapAnalysisRunResponse(analysisResponse.data));
      setFile(null);
    } catch (err: unknown) {
      const uploadError = err as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      setError(uploadError.response?.data?.detail || uploadError.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setFile(null);
    setJobDesc('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', color: '#f0f0ff', maxWidth: '800px' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.375rem' }}>
          Upload & Analyze
        </h1>
        <p style={{ color: '#8888aa', fontSize: '0.95rem' }}>
          Upload your resume and paste the job description to get an instant AI-powered analysis.
        </p>
      </div>

      {!result ? (
        <UploadAnalysisFormSection
          file={file}
          jobDescription={jobDesc}
          loading={loading}
          error={error}
          onFileChange={setFile}
          onJobDescriptionChange={setJobDesc}
          onSubmit={handleSubmit}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <UploadAnalysisScoreSection result={result} />
          <UploadAnalysisResultsSection
            result={result}
            showRewrite={showRewrite}
            onToggleRewrite={() => setShowRewrite((current) => !current)}
            onReset={handleReset}
          />
        </div>
      )}
    </div>
  );
}
