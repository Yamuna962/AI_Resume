import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScoreBadge } from '@/components/atoms/ScoreBadge';
import { ReactNode } from 'react';

interface ScoreCardProps {
  title: string;
  score: number;
  icon?: ReactNode;
  delay?: number;
}

export function ScoreCard({ title, score, icon, delay = 0 }: ScoreCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card className="glass-card overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          {icon && <div className="text-muted-foreground">{icon}</div>}
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-6">
          <ScoreBadge score={score} size="md" />
        </CardContent>
      </Card>
    </motion.div>
  );
}
