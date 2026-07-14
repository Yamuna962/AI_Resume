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
    <form onSubmit={onSubmit} className="flex flex-col gap-6">
      <div className="bg-card border border-border rounded-2xl p-4">
        <h2 className="font-semibold text-sm mb-4 text-muted-foreground">
          1. Upload Resume (PDF)
        </h2>
        {!file ? (
          <div
            {...getRootProps()}
            className={`border-2 rounded-xl p-6 text-center cursor-pointer transition ${isDragActive ? 'border-primary bg-primary/5' : 'border-border/10'}`}
          >
            <input {...getInputProps()} />
            <div className="w-14 h-14 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-4 text-primary">
              <UploadCloud size={24} />
            </div>
            <p className="font-semibold mb-1">Click to upload or drag &amp; drop</p>
            <p className="text-sm text-muted-foreground">PDF only · Max 10MB</p>
          </div>
        ) : (
          <div className="flex items-center gap-4 p-3 rounded-xl bg-primary/5 border border-primary/10">
            <FileText size={20} color="#a78bfa" />
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{file.name}</p>
              <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button type="button" onClick={() => onFileChange(null)} className="bg-transparent border-0 text-muted-foreground p-1">
              <X size={18} />
            </button>
          </div>
        )}
      </div>

      <div className="bg-card border border-border rounded-2xl p-4">
        <h2 className="font-semibold text-sm mb-4 text-muted-foreground">
          2. Paste Job Description
        </h2>
        <textarea
          value={jobDescription}
          onChange={(event) => onJobDescriptionChange(event.target.value)}
          placeholder="Paste the full job description here..."
          rows={10}
          className="w-full bg-transparent border border-border rounded-lg p-3 text-foreground text-sm resize-vertical font-sans focus:border-primary focus:ring-0"
        />
      </div>

      {error && (
        <div className="flex gap-3 px-4 py-3 bg-red-900/10 border border-red-900/20 rounded-md text-red-400 text-sm items-start">
          <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={!file || !jobDescription.trim() || loading}
        className={`px-4 py-3 rounded-lg text-white font-bold text-base flex items-center justify-center gap-2 ${!file || !jobDescription.trim() ? 'opacity-50 cursor-not-allowed' : 'bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg'}`}
      >
        {loading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            Analyzing...
          </>
        ) : (
          '🚀 Analyze My Resume'
        )}
      </button>
    </form>
  );
}
