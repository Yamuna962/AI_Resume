import { motion } from 'framer-motion';
import type { AnalysisResult } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileEdit, CheckCircle2, Download, Copy } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface RewritePanelProps {
  analysis: AnalysisResult;
}

export function RewritePanel({ analysis }: RewritePanelProps) {
  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`${type} copied to clipboard`);
    } catch {
      toast.error('Failed to copy text');
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <FileEdit className="h-8 w-8 text-primary" />
            AI Rewritten Resume
          </h2>
          <p className="text-muted-foreground mt-1">
            Tailored specifically for this job description based on your experience.
          </p>
        </div>
      </div>

      <Card className="glass-card overflow-hidden border-primary/20">
        <CardHeader className="bg-primary/5 border-b border-border flex flex-row items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-primary" />
            Professional Summary
          </CardTitle>
          <Button variant="outline" size="sm" onClick={() => copyToClipboard(analysis.rewritten_summary, 'Summary')}>
            <Copy className="h-4 w-4 mr-2" />
            Copy
          </Button>
        </CardHeader>
        <CardContent className="p-6">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{analysis.rewritten_summary}</p>
        </CardContent>
      </Card>

      <Card className="glass-card overflow-hidden">
        <CardHeader className="bg-muted/50 border-b border-border flex flex-row items-center justify-between">
          <CardTitle className="text-lg">Full Resume Content</CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => copyToClipboard(analysis.rewritten_resume, 'Resume')}>
              <Copy className="h-4 w-4 mr-2" />
              Copy All
            </Button>
            <Button variant="default" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="bg-background/50 p-6 font-mono text-sm leading-relaxed whitespace-pre-wrap overflow-x-auto">
            {analysis.rewritten_resume}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
