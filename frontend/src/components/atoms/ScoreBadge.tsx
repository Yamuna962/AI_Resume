import { useEffect, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { getScoreColor } from '@/lib/utils';

interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export function ScoreBadge({ score, size = 'md' }: ScoreBadgeProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const controls = useAnimation();
  const color = getScoreColor(score);

  const dimensions = {
    sm: 'w-12 h-12 text-sm border-4',
    md: 'w-24 h-24 text-2xl border-8',
    lg: 'w-32 h-32 text-4xl border-[12px]',
  };

  useEffect(() => {
    let startTime: number;
    const duration = 1500; // 1.5 seconds
    
    const animate = (time: number) => {
      if (!startTime) startTime = time;
      const progress = (time - startTime) / duration;
      
      if (progress < 1) {
        setDisplayScore(Math.floor(score * progress));
        requestAnimationFrame(animate);
      } else {
        setDisplayScore(score);
      }
    };
    
    requestAnimationFrame(animate);
    
    controls.start({
      pathLength: score / 100,
      transition: { duration: 1.5, ease: "easeOut" }
    });
  }, [score, controls]);

  return (
    <div className={`relative flex items-center justify-center rounded-full ${dimensions[size]} bg-card`} style={{ borderColor: `${color}30` }}>
      <svg className="absolute inset-0 h-full w-full -rotate-90 transform" viewBox="0 0 100 100">
        <motion.circle
          cx="50"
          cy="50"
          r="44"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={controls}
        />
      </svg>
      <span className="font-bold" style={{ color }}>{displayScore}</span>
    </div>
  );
}
