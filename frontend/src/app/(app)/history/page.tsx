'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ChevronRight, Clock, FileText } from 'lucide-react';
import api from '@/lib/axios';
import type { HistoryItem } from '@/types';

interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  limit: number;
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<HistoryResponse>('/history')
      .then((response) => setAnalyses(response.data.items || []))
      .catch(() => {
        setAnalyses([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-3xl w-full mx-auto text-foreground flex flex-col gap-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold mb-2">Analysis History</h1>
        <p className="text-sm text-muted-foreground">All your past resume analyses and scores.</p>
      </div>

      {loading ? (
        <div className="text-center py-16 text-muted-foreground">Loading...</div>
      ) : analyses.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-8 text-center">
          <Clock size={48} className="mx-auto text-muted-foreground" />
          <h3 className="font-semibold mt-4 mb-2">No analyses yet</h3>
          <p className="text-sm text-muted-foreground mb-4">Upload your first resume to see results here.</p>
          <Link href="/upload" className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-gradient-to-br from-primary to-indigo-600 text-white font-medium">Start New Analysis</Link>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {analyses.map((analysis) => {
            const matchScore = analysis.skill_match_percentage || 0;
            const atsScore = analysis.ats_score || 0;
            const scoreClass = (score: number) => (score >= 75 ? 'text-green-500' : score >= 50 ? 'text-yellow-500' : 'text-red-500');

            return (
              <Link key={analysis.id} href={`/history/${analysis.id}`} className="no-underline">
                <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 p-4 bg-card border border-border rounded-lg transition-shadow hover:shadow-md cursor-pointer">
                  <div className="flex items-center gap-4 min-w-0 flex-1">
                    <div className="w-10 h-10 rounded-md flex-shrink-0 bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                      <FileText size={18} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium mb-0.5 truncate">{analysis.resume_filename || 'Resume Analysis'}</div>
                      <div className="text-sm text-muted-foreground">{new Date(analysis.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between sm:justify-end gap-4 sm:gap-6 pl-14 sm:pl-0">
                    <div className="flex items-center gap-4 sm:gap-6">
                      <div className="text-center">
                        <div className="text-xs text-muted-foreground mb-1">Match</div>
                        <div className={`font-semibold ${scoreClass(matchScore)}`}>{matchScore}%</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-muted-foreground mb-1">ATS</div>
                        <div className={`font-semibold ${scoreClass(atsScore)}`}>{atsScore}</div>
                      </div>
                    </div>
                    <ChevronRight size={18} className="text-muted-foreground flex-shrink-0" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}