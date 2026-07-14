'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ChevronRight, Clock, FileText, UploadCloud } from 'lucide-react';
import api from '@/lib/axios';
import type { HistoryItem } from '@/types';

interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  limit: number;
}

const scoreBadge = (score: number) =>
  score >= 75
    ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/25'
    : score >= 50
    ? 'bg-amber-500/10 text-amber-500 border-amber-500/25'
    : 'bg-red-500/10 text-red-500 border-red-500/25';

function HistorySkeleton() {
  return (
    <div className="flex flex-col gap-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 bg-card border border-border rounded-xl">
          <div className="skeleton w-10 h-10 rounded-lg flex-shrink-0" />
          <div className="flex-1 flex flex-col gap-2 min-w-0">
            <div className="skeleton h-3.5 w-48 rounded" />
            <div className="skeleton h-3 w-24 rounded" />
          </div>
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="skeleton h-6 w-12 rounded-full" />
            <div className="skeleton h-6 w-12 rounded-full" />
          </div>
          <div className="skeleton h-4 w-4 rounded flex-shrink-0" />
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="bg-card border border-border rounded-2xl p-10 text-center">
      <div className="w-14 h-14 rounded-2xl bg-muted flex items-center justify-center mx-auto mb-4">
        <Clock size={28} className="text-muted-foreground" />
      </div>
      <h3 className="font-semibold text-base mb-1">No analyses yet</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-xs mx-auto">
        Upload your first resume and paste a job description to see your results here.
      </p>
      <Link
        href="/upload"
        className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-sm font-semibold shadow hover:from-violet-500 hover:to-indigo-500 transition-all"
      >
        <UploadCloud size={16} />
        Start New Analysis
      </Link>
    </div>
  );
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<HistoryResponse>('/history')
      .then((res) => setAnalyses(res.data.items || []))
      .catch(() => setAnalyses([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-3xl w-full mx-auto flex flex-col gap-6 text-foreground">
      {/* Page header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-1">
          Analysis History
        </h1>
        <p className="text-sm text-muted-foreground">All your past resume analyses and scores.</p>
      </div>

      {loading ? (
        <HistorySkeleton />
      ) : analyses.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="flex flex-col gap-2.5">
          {analyses.map((analysis) => {
            const matchScore = analysis.skill_match_percentage || 0;
            const atsScore = analysis.ats_score || 0;

            return (
              <Link
                key={analysis.id}
                href={`/history/${analysis.id}`}
                className="group no-underline"
              >
                {/*
                  Single-row layout that works on both mobile and desktop:
                  - Icon: fixed 40×40, flex-shrink-0
                  - Text block: flex-1 min-w-0 so truncate works
                  - Score badges: flex-shrink-0, hidden label on mobile (xs), shown on sm+
                  - Chevron: flex-shrink-0
                  No pl-14 indent hack — scores align naturally as flex siblings.
                */}
                <div className="flex items-center gap-3 sm:gap-4 p-4 bg-card border border-border rounded-xl transition-all hover:border-primary/30 hover:shadow-sm cursor-pointer">
                  {/* Icon */}
                  <div className="w-10 h-10 rounded-lg flex-shrink-0 bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                    <FileText size={18} />
                  </div>

                  {/* Filename + date */}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate leading-snug">
                      {analysis.resume_filename || 'Resume Analysis'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {new Date(analysis.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </p>
                  </div>

                  {/* Score badges */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <div className="text-center">
                      <div className="text-[10px] text-muted-foreground mb-1 hidden sm:block">
                        Match
                      </div>
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded-full border ${scoreBadge(matchScore)}`}
                      >
                        {matchScore}%
                      </span>
                    </div>
                    <div className="text-center">
                      <div className="text-[10px] text-muted-foreground mb-1 hidden sm:block">
                        ATS
                      </div>
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded-full border ${scoreBadge(atsScore)}`}
                      >
                        {atsScore}
                      </span>
                    </div>
                  </div>

                  {/* Chevron */}
                  <ChevronRight
                    size={16}
                    className="text-muted-foreground flex-shrink-0 transition-transform group-hover:translate-x-0.5"
                  />
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}