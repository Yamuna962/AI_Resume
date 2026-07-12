import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateString: string) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

export function formatScore(score: number | null | undefined) {
  if (score === null || score === undefined) return 0;
  return Math.round(score);
}

export function getScoreColor(score: number) {
  if (score >= 80) return '#10b981'; // Emerald
  if (score >= 60) return '#f59e0b'; // Amber
  return '#f43f5e'; // Rose
}

export function getMatchTypeBadgeColor(type: string) {
  switch (type) {
    case 'exact': return 'default';
    case 'semantic': return 'secondary';
    case 'vector': return 'outline';
    default: return 'outline';
  }
}
