import { motion } from 'framer-motion';
import { AnalysisResult } from '@/types';
import { ScoreCard } from '@/components/molecules/ScoreCard';
import { SkillChip } from '@/components/atoms/SkillChip';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, AlertTriangle, Info, Target, Network, BookOpen, Lightbulb } from 'lucide-react';

interface AnalysisPanelProps {
  analysis: AnalysisResult;
}

export function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      variants={container} 
      initial="hidden" 
      animate="show" 
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={item} className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Analysis Results</h2>
          <p className="text-muted-foreground mt-1">Detailed breakdown of your resume matching</p>
        </div>
        <Badge variant="outline" className="px-3 py-1 text-sm bg-background">
          Generated on {new Date(analysis.created_at).toLocaleDateString()}
        </Badge>
      </motion.div>

      {/* Main Scores */}
      <div className="grid gap-6 md:grid-cols-3">
        <ScoreCard 
          title="Overall Resume Score" 
          score={analysis.resume_score} 
          icon={<Target className="h-4 w-4" />}
          delay={0.1}
        />
        <ScoreCard 
          title="ATS Compatibility" 
          score={analysis.ats_score} 
          icon={<Network className="h-4 w-4" />}
          delay={0.2}
        />
        <ScoreCard 
          title="Skill Match %" 
          score={analysis.skill_match_percentage} 
          icon={<BookOpen className="h-4 w-4" />}
          delay={0.3}
        />
      </div>

      {/* Engine Breakdown */}
      <motion.div variants={item}>
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-lg">Three-Layer Matching Engine Scores</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-primary font-medium">Exact Keyword Match</span>
                <span>{analysis.exact_match_score}%</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary" style={{ width: `${analysis.exact_match_score}%` }} />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-emerald-500 font-medium">Vector Semantic Search</span>
                <span>{analysis.vector_similarity_score}%</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500" style={{ width: `${analysis.vector_similarity_score}%` }} />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-accent font-medium">Cross-Encoder Inference</span>
                <span>{analysis.semantic_match_score}%</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-accent" style={{ width: `${analysis.semantic_match_score}%` }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Skills Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        <motion.div variants={item}>
          <Card className="glass-card h-full">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                Matched Skills
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {analysis.matched_skills.map((skill, i) => (
                <SkillChip key={i} skill={skill} />
              ))}
              {analysis.matched_skills.length === 0 && (
                <p className="text-sm text-muted-foreground">No matching skills found.</p>
              )}
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div variants={item}>
          <Card className="glass-card h-full border-rose-500/20">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-rose-500" />
                Missing Skills
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {analysis.missing_skills.map((skill, i) => (
                <Badge key={i} variant="outline" className="bg-rose-500/10 text-rose-500 border-rose-500/20 px-3 py-1">
                  {skill}
                </Badge>
              ))}
              {analysis.missing_skills.length === 0 && (
                <p className="text-sm text-muted-foreground">No missing skills detected! Great job.</p>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid gap-6 md:grid-cols-2">
        <motion.div variants={item}>
          <Card className="glass-card h-full border-emerald-500/20">
            <CardHeader>
              <CardTitle className="text-lg text-emerald-500">Strengths</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {analysis.strengths.map((str, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
                    <span className="text-sm">{str}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div variants={item}>
          <Card className="glass-card h-full border-amber-500/20">
            <CardHeader>
              <CardTitle className="text-lg text-amber-500">Areas for Improvement</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {analysis.weaknesses.map((weak, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
                    <span className="text-sm">{weak}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Suggestions */}
      <motion.div variants={item}>
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-accent" />
              Actionable Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {analysis.suggestions.map((sug, i) => (
              <div key={i} className="flex gap-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/20 text-accent font-bold">
                  {i + 1}
                </div>
                <div>
                  <h4 className="font-semibold">{sug.title}</h4>
                  <p className="text-sm text-muted-foreground mt-1">{sug.description}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </motion.div>
      
      {/* Projects */}
      <motion.div variants={item}>
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Info className="h-5 w-5 text-primary" />
              Recommended Projects to Build
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-2 text-sm text-muted-foreground">
              {analysis.project_suggestions.map((proj, i) => (
                <li key={i}>{proj}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
