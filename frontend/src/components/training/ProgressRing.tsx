import { motion } from "framer-motion";
import { useMemo } from "react";
import { clamp } from "../../lib/utils";

interface ProgressRingProps {
  percentage: number; // 0-100
  size?: number;
  stroke?: number;
  colour?: string;
  trackColour?: string;
  label?: string;
  animated?: boolean;
}

export function ProgressRing({
  percentage, size = 120, stroke = 8,
  colour = "var(--accent)", trackColour = "var(--border-subtle)",
  label, animated = true,
}: ProgressRingProps) {
  const pct = clamp(percentage, 0, 100);
  const radius = (size - stroke) / 2;
  const circumference = useMemo(() => 2 * Math.PI * radius, [radius]);
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="inline-flex flex-col items-center gap-2">
      <div style={{ width: size, height: size }} className="relative">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            stroke={trackColour}
            strokeWidth={stroke}
            fill="none"
          />
          <motion.circle
            cx={size / 2} cy={size / 2} r={radius}
            stroke={colour}
            strokeWidth={stroke}
            strokeLinecap="round"
            fill="none"
            strokeDasharray={circumference}
            initial={animated ? { strokeDashoffset: circumference } : false}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-semibold tabular-nums text-text-primary">
            {Math.round(pct)}%
          </span>
        </div>
      </div>
      {label && (
        <span className="text-xs text-text-secondary">{label}</span>
      )}
    </div>
  );
}
