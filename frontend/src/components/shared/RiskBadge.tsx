import { cn } from "../../lib/utils";
import type { RiskLevel } from "../../types/api";

const LABEL: Record<RiskLevel, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  unknown: "Unknown",
};

const COLOUR_VAR: Record<RiskLevel, string> = {
  critical: "var(--risk-critical)",
  high: "var(--risk-high)",
  medium: "var(--risk-medium)",
  low: "var(--risk-low)",
  unknown: "var(--risk-unknown)",
};

type Size = "sm" | "md" | "lg";

const sizeClasses: Record<Size, string> = {
  sm: "text-2xs px-2 py-0.5 gap-1",
  md: "text-xs px-2.5 py-1 gap-1.5",
  lg: "text-sm px-3 py-1.5 gap-2",
};

const dotSize: Record<Size, string> = {
  sm: "h-1.5 w-1.5",
  md: "h-2 w-2",
  lg: "h-2.5 w-2.5",
};

export function RiskBadge({
  level, size = "md", className,
}: { level: RiskLevel; size?: Size; className?: string }) {
  const colour = COLOUR_VAR[level];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border font-medium",
        sizeClasses[size],
        level === "critical" && "animate-pulse-risk",
        className,
      )}
      style={{
        color: colour,
        borderColor: colour,
        background: `color-mix(in srgb, ${colour} 10%, transparent)`,
      }}
    >
      <span
        className={cn("inline-block rounded-full", dotSize[size])}
        style={{ background: colour }}
      />
      {LABEL[level]}
    </span>
  );
}
