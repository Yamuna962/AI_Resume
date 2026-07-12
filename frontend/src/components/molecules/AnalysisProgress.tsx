import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

const steps = [
  { id: 0, label: 'Extracting PDF Text' },
  { id: 1, label: 'Exact Keyword Matching' },
  { id: 2, label: 'Vector Database Search' },
  { id: 3, label: 'Semantic Cross-Encoder Analysis' },
  { id: 4, label: 'AI Prompt Generation' },
  { id: 5, label: 'LLM Analysis & Scoring' },
];

export function AnalysisProgress() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Simulate progress for UI since backend might take 15-30s
    const timers = steps.map((_, i) => 
      setTimeout(() => {
        setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
      }, (i + 1) * 3500)
    );

    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="w-full max-w-md mx-auto p-6 glass-card rounded-xl">
      <div className="mb-8 text-center">
        <h3 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
          Analyzing Resume
        </h3>
        <p className="text-sm text-muted-foreground mt-2">
          Running three-layer matching engine...
        </p>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => {
          const isActive = index === currentStep;
          const isPast = index < currentStep;
          
          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.2 }}
              className={`flex items-center gap-4 p-3 rounded-lg border transition-colors ${
                isActive ? 'bg-primary/10 border-primary/30' : 'border-transparent'
              }`}
            >
              <div className="flex-shrink-0">
                {isPast ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="text-emerald-500"
                  >
                    <CheckCircle2 className="h-5 w-5" />
                  </motion.div>
                ) : isActive ? (
                  <Loader2 className="h-5 w-5 text-primary animate-spin" />
                ) : (
                  <Circle className="h-5 w-5 text-muted-foreground/30" />
                )}
              </div>
              <span className={`text-sm font-medium ${
                isActive ? 'text-foreground' : isPast ? 'text-muted-foreground' : 'text-muted-foreground/50'
              }`}>
                {step.label}
              </span>
            </motion.div>
          );
        })}
      </div>
      
      <div className="mt-8 h-1 w-full bg-muted rounded-full overflow-hidden">
        <motion.div 
          className="h-full bg-gradient-to-r from-primary to-accent"
          initial={{ width: "0%" }}
          animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );
}
