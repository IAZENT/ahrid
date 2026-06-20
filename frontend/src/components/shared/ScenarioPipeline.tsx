import { useEffect, useState } from "react";
import { ChevronDown, ChevronRight, Filter } from "lucide-react";
import { Card, CardBody } from "../../components/ui/Card";
import { adminApi } from "../../api/admin";
import { trainingApi } from "../../api/training";

interface PipelineStage {
  id: string;
  label: string;
  count: string;
  items: string[];
}

const FALLBACK_STAGES: PipelineStage[] = [
  {
    id: "feeds",
    label: "OSINT Feeds",
    count: "~50 raw",
    items: ["Phishing.Database", "OpenPhish", "AlienVault OTX", "URLScan.io"],
  },
  {
    id: "classify",
    label: "Classification",
    count: "6 lure types",
    items: ["Banking", "E-commerce", "Document Share", "Account Suspension", "Package Delivery", "Generic"],
  },
  {
    id: "scenarios",
    label: "Active Scenarios",
    count: "24+ items",
    items: ["MCQ Questions", "Visual Simulations", "True/False", "Identify Threat"],
  },
];

const SCENARIO_TYPES = ["MCQ Questions", "Visual Simulations", "True/False", "Identify Threat"];

export function ScenarioPipeline() {
  const [expanded, setExpanded] = useState(false);
  const [stages, setStages] = useState<PipelineStage[]>(FALLBACK_STAGES);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [stats, categories] = await Promise.all([
          adminApi.stats(),
          trainingApi.categories(),
        ]);
        if (cancelled) return;
        setStages([
          {
            id: "feeds",
            label: "OSINT Feeds",
            count: `${stats.totals.threats_last_24h} in 24h`,
            items: ["Phishing.Database", "OpenPhish", "AlienVault OTX", "URLScan.io"],
          },
          {
            id: "classify",
            label: "Classification",
            count: `${categories.length} categories`,
            items: categories.map((c) => c.display_name),
          },
          {
            id: "scenarios",
            label: "Active Scenarios",
            count: `${stats.totals.active_scenarios} items`,
            items: SCENARIO_TYPES,
          },
        ]);
      } catch {
        // Keep fallback stages
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  return (
    <Card>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 p-4 text-left"
      >
        <Filter className="h-4 w-4 text-accent" />
        <span className="text-md font-semibold text-text-primary">Scenario Pipeline</span>
        <span className="text-xs text-text-muted">
          How threat intel becomes training scenarios
        </span>
        <span className="ml-auto text-text-muted">
          {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </span>
      </button>
      {expanded && (
        <CardBody className="border-t border-border-subtle pt-4">
          <div className="flex flex-col items-stretch gap-0 lg:flex-row lg:items-start lg:gap-4">
            {stages.map((stage, idx) => (
              <div key={stage.id} className="flex flex-1 items-stretch gap-4">
                <div className="flex flex-col items-center gap-1">
                  <div className="rounded-lg border border-border-subtle bg-bg-elevated px-4 py-3 text-center">
                    <div className="text-lg font-bold text-accent">{stage.count}</div>
                    <div className="text-xs font-semibold text-text-primary">{stage.label}</div>
                  </div>
                </div>
                {idx < stages.length - 1 && (
                  <div className="hidden items-center lg:flex">
                    <div className="h-0.5 w-8 bg-accent/40" />
                    <div className="h-0 w-0 border-y-[5px] border-l-[6px] border-y-transparent border-l-accent/40" />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Expanded detail */}
          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
            {stages.map((stage) => (
              <div key={stage.id}>
                <div className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-muted">
                  {stage.label}
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {stage.items.map((item) => (
                    <span
                      key={item}
                      className="rounded border border-border-subtle bg-bg-surface px-2 py-0.5 text-[10px] text-text-secondary"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      )}
    </Card>
  );
}
