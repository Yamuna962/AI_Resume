import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { MatchedSkill } from '@/types';
import { cn } from '@/lib/utils';

interface SkillChipProps {
  skill: MatchedSkill;
}

export function SkillChip({ skill }: SkillChipProps) {
  const getMatchColor = (type: string) => {
    switch (type) {
      case 'exact':
        return 'bg-primary/20 text-primary border-primary/30';
      case 'semantic':
        return 'bg-accent/20 text-accent border-accent/30';
      case 'vector':
        return 'bg-emerald-500/20 text-emerald-500 border-emerald-500/30';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 shadow-sm"
    >
      <span className="text-sm font-medium">{skill.skill}</span>
      <Badge variant="outline" className={cn('text-[10px] uppercase px-1.5 py-0 border leading-tight', getMatchColor(skill.match_type))}>
        {skill.match_type}
      </Badge>
    </motion.div>
  );
}
