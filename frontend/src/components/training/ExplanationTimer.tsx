import { useEffect, useRef, useState } from "react";

interface ExplanationTimerProps {
  duration: number;
  onComplete: () => void;
}

export function ExplanationTimer({ duration, onComplete }: ExplanationTimerProps) {
  const [secondsLeft, setSecondsLeft] = useState(duration);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    setSecondsLeft(duration);
    const id = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(id);
          setTimeout(() => onCompleteRef.current(), 0);
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [duration]);

  const progress = (duration - secondsLeft) / duration;
  const circumference = 2 * Math.PI * 38;
  const strokeDashoffset = circumference * (1 - progress);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative">
        <svg width="80" height="80" viewBox="0 0 80 80">
          <circle
            cx="40"
            cy="40"
            r="38"
            fill="none"
            stroke="var(--border-subtle)"
            strokeWidth="3"
          />
          <circle
            cx="40"
            cy="40"
            r="38"
            fill="none"
            stroke={secondsLeft > 0 ? "var(--accent)" : "var(--success)"}
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 40 40)"
            className="transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-semibold text-text-primary">
            {secondsLeft}s
          </span>
        </div>
      </div>
      <span className="text-[10px] text-text-muted">Read the explanation</span>
    </div>
  );
}
