import { useState } from 'react';
import api from '@/lib/axios';
import { getApiErrorMessage } from '@/lib/api-error';
import type { ResumeUploadResponse } from '@/types/analysis';

export function useUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadResume = async (file: File): Promise<ResumeUploadResponse> => {
    try {
      setIsUploading(true);
      setError(null);
      setUploadProgress(0);

      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post<ResumeUploadResponse>('/resume/upload', formData, {
        headers: {
          'Content-Type': undefined,
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || file.size)
          );
          setUploadProgress(percentCompleted);
        },
      });

      return response.data;
    } catch (error: unknown) {
      setError(getApiErrorMessage(error, 'An error occurred during upload'));
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  return { uploadResume, isUploading, error, uploadProgress };
}
