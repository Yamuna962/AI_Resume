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
    if (!file || !jobDesc.trim()) return;

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

      if (!resumeId) throw new Error('Failed to retrieve resume ID after upload.');

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
      setError(
        uploadError.response?.data?.detail ||
          uploadError.message ||
          'Analysis failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setFile(null);
    setJobDesc('');
    setError('');
  };

  return (
    /*
      max-w-3xl + w-full + mx-auto: centres the column on desktop,
      full-width on mobile. gap-6 matches the rest of the app shell.
      Removed the extra mb-4 wrapper — gap-6 handles spacing uniformly.
    */
    <div className="max-w-3xl w-full mx-auto text-foreground flex flex-col gap-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-1">
          Upload &amp; Analyze
        </h1>
        <p className="text-sm text-muted-foreground">
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
        <div className="flex flex-col gap-6">
          <UploadAnalysisScoreSection result={result} />
          <UploadAnalysisResultsSection
            result={result}
            showRewrite={showRewrite}
            onToggleRewrite={() => setShowRewrite((prev) => !prev)}
            onReset={handleReset}
          />
        </div>
      )}
    </div>
  );
}