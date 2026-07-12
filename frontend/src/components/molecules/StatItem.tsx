import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { ReactNode } from 'react';

interface StatItemProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  delay?: number;
}

export function StatItem({ title, value, icon, delay = 0 }: StatItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card className="glass-card">
        <CardContent className="flex items-center gap-4 p-6">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            {icon}
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <h3 className="text-2xl font-bold">{value}</h3>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
