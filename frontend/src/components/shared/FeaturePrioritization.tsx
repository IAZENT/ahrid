import { useState } from "react";
import { ChevronDown, ChevronRight, Target } from "lucide-react";
import { Card, CardBody } from "../../components/ui/Card";

interface FeatureDot {
  label: string;
  x: number;
  y: number;
  selected?: boolean;
}

const FEATURES: FeatureDot[] = [
  { label: "Engagement Timer", x: 22, y: 82, selected: true },
  { label: "Onboarding Walkthrough", x: 28, y: 75, selected: true },
  { label: "Micro-Session", x: 18, y: 68, selected: true },
  { label: "Gamification", x: 72, y: 78 },
  { label: "Video Explanations", x: 68, y: 72 },
  { label: "Automated Escalation", x: 88, y: 55 },
  { label: "Leaderboard", x: 75, y: 45 },
  { label: "Email Digest", x: 25, y: 22 },
];

export function FeaturePrioritization() {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 p-4 text-left"
      >
        <Target className="h-4 w-4 text-accent" />
        <span className="text-md font-semibold text-text-primary">Feature Prioritization</span>
        <span className="text-xs text-text-muted">Impact vs effort analysis</span>
        <span className="ml-auto text-text-muted">
          {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </span>
      </button>
      {expanded && (
        <CardBody className="border-t border-border-subtle pt-4">
          <div className="relative mx-auto" style={{ maxWidth: 520 }}>
            {/* Y-axis label */}
            <div className="absolute -left-1 top-0 flex h-full items-center">
              <span
                className="-rotate-90 whitespace-nowrap text-[10px] font-semibold uppercase tracking-wider text-text-muted"
                style={{ transformOrigin: "center" }}
              >
                Impact on User Behaviour
              </span>
            </div>

            <div className="ml-8 mb-8">
              <div className="relative h-72 w-full border-l border-b border-border-default">
                {/* Grid lines */}
                {[25, 50, 75].map((pct) => (
                  <div
                    key={`h-${pct}`}
                    className="absolute w-full border-t border-border-subtle/50"
                    style={{ bottom: `${pct}%` }}
                  />
                ))}
                {[25, 50, 75].map((pct) => (
                  <div
                    key={`v-${pct}`}
                    className="absolute h-full border-l border-border-subtle/50"
                    style={{ left: `${pct}%` }}
                  />
                ))}

                {/* Selected circle */}
                <div
                  className="absolute rounded-full border-[1.5px] border-success/60"
                  style={{ left: "6%", bottom: "58%", width: "200px", height: "170px" }}
                />

                {/* Dots */}
                {FEATURES.map((dot) => (
                  <div
                    key={dot.label}
                    className="absolute flex flex-col items-center"
                    style={{
                      left: `${dot.x}%`,
                      bottom: `${dot.y}%`,
                      transform: "translate(-50%, 50%)",
                    }}
                  >
                    <div
                      className={`h-3 w-3 rounded-full ${
                        dot.selected
                          ? "bg-success shadow-[0_0_8px_rgba(16,185,129,0.4)]"
                          : "bg-accent"
                      }`}
                    />
                    <span
                      className="mt-1 whitespace-nowrap text-[10px] font-medium text-text-secondary"
                      style={{ fontFamily: "Arial, sans-serif" }}
                    >
                      {dot.label}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-2 text-center text-[10px] font-semibold uppercase tracking-wider text-text-muted">
                Implementation Effort
              </div>
              <div className="mt-1 flex justify-between text-[9px] text-text-muted">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>

            <div className="flex items-center justify-center gap-6 text-[10px] text-text-secondary">
              <div className="flex items-center gap-1.5">
                <div className="h-2.5 w-2.5 rounded-full bg-success" />
                <span>Selected (High Impact, Low Effort)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="h-2.5 w-2.5 rounded-full bg-accent" />
                <span>Considered</span>
              </div>
            </div>
          </div>
        </CardBody>
      )}
    </Card>
  );
}
