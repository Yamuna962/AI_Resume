'use client';

import { useState, type FormEventHandler } from 'react';
import {
  UploadCloud,
  FileText,
  X,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';

interface UploadAnalysisFormSectionProps {
  file: File | null;
  jobDescription: string;
  loading: boolean;
  error: string;
  onFileChange: (file: File | null) => void;
  onJobDescriptionChange: (value: string) => void;
  onSubmit: FormEventHandler<HTMLFormElement>;
}

export function UploadAnalysisFormSection({
  file,
  jobDescription,
  loading,
  error,
  onFileChange,
  onJobDescriptionChange,
  onSubmit,
}: UploadAnalysisFormSectionProps) {
  const [isDragActive, setIsDragActive] = useState(false);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (files: File[]) => {
      if (files[0]) {
        onFileChange(files[0]);
      }
    },
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
    onDropAccepted: () => setIsDragActive(false),
    onDropRejected: () => setIsDragActive(false),
  });

  return (
    <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div
        style={{
          background: 'rgba(15,15,26,0.9)',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: '1.25rem',
          padding: '1.5rem',
        }}
      >
        <h2 style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '1rem', color: '#c4c4e0' }}>
          1. Upload Resume (PDF)
        </h2>
        {!file ? (
          <div
            {...getRootProps()}
            style={{
              border: `2px dashed ${isDragActive ? '#7c3aed' : 'rgba(255,255,255,0.1)'}`,
              borderRadius: '0.875rem',
              padding: '2.5rem',
              textAlign: 'center',
              cursor: 'pointer',
              background: isDragActive ? 'rgba(124,58,237,0.05)' : 'transparent',
              transition: 'all 0.2s',
            }}
          >
            <input {...getInputProps()} />
            <div
              style={{
                width: '3.5rem',
                height: '3.5rem',
                borderRadius: '0.875rem',
                background: 'rgba(124,58,237,0.12)',
                border: '1px solid rgba(124,58,237,0.25)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
                color: '#a78bfa',
              }}
            >
              <UploadCloud size={24} />
            </div>
            <p style={{ fontWeight: 600, marginBottom: '0.375rem' }}>Click to upload or drag &amp; drop</p>
            <p style={{ fontSize: '0.8rem', color: '#8888aa' }}>PDF only · Max 10MB</p>
          </div>
        ) : (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              padding: '1rem 1.25rem',
              borderRadius: '0.875rem',
              background: 'rgba(124,58,237,0.08)',
              border: '1px solid rgba(124,58,237,0.2)',
            }}
          >
            <FileText size={20} color="#a78bfa" />
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {file.name}
              </p>
              <p style={{ fontSize: '0.75rem', color: '#8888aa' }}>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button
              type="button"
              onClick={() => onFileChange(null)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#5a5a7a',
                padding: '0.25rem',
              }}
            >
              <X size={18} />
            </button>
          </div>
        )}
      </div>

      <div
        style={{
          background: 'rgba(15,15,26,0.9)',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: '1.25rem',
          padding: '1.5rem',
        }}
      >
        <h2 style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '1rem', color: '#c4c4e0' }}>
          2. Paste Job Description
        </h2>
        <textarea
          value={jobDescription}
          onChange={(event) => onJobDescriptionChange(event.target.value)}
          placeholder="Paste the full job description here..."
          rows={10}
          style={{
            width: '100%',
            background: 'rgba(13,13,22,0.8)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '0.75rem',
            padding: '0.875rem 1rem',
            color: '#f0f0ff',
            fontSize: '0.875rem',
            outline: 'none',
            resize: 'vertical',
            fontFamily: 'Inter, sans-serif',
            transition: 'border-color 0.2s',
            boxSizing: 'border-box',
          }}
          onFocus={(event) => {
            event.target.style.borderColor = 'rgba(124,58,237,0.6)';
          }}
          onBlur={(event) => {
            event.target.style.borderColor = 'rgba(255,255,255,0.08)';
          }}
        />
      </div>

      {error && (
        <div
          style={{
            display: 'flex',
            gap: '0.75rem',
            padding: '0.875rem 1rem',
            background: 'rgba(239,68,68,0.1)',
            border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: '0.75rem',
            color: '#f87171',
            fontSize: '0.875rem',
          }}
        >
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={!file || !jobDescription.trim() || loading}
        style={{
          padding: '0.875rem',
          borderRadius: '0.75rem',
          background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
          color: 'white',
          border: 'none',
          fontWeight: 700,
          fontSize: '1rem',
          cursor: !file || !jobDescription.trim() || loading ? 'not-allowed' : 'pointer',
          opacity: !file || !jobDescription.trim() ? 0.5 : 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem',
          boxShadow: '0 4px 20px rgba(124,58,237,0.3)',
          transition: 'all 0.2s',
        }}
      >
        {loading ? (
          <>
            <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
            Analyzing...
          </>
        ) : (
          '🚀 Analyze My Resume'
        )}
      </button>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </form>
  );
}
