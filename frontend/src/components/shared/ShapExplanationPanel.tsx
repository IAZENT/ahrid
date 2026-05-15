/**
 * SHAP explanation panel for the My Score page.
 *
 * Shows the top features pushing the user's risk *up* (red) and the
 * top features pulling it *down* (green). Hidden gracefully when the
 * RF model isn't ready or SHAP failed for any reason.
 */
import { ShieldAlert, ShieldCheck } from "lucide-react";
import { Card, CardBody } from "../ui/Card";

export interface ShapDatum {
  feature: string;
  label: string;
  shap_value: number;
  direction: "increases_risk" | "reduces_risk";
}

export interface ShapExplanation {
  shap_values?: ShapDatum[];
  top_risk_factors?: string[];
  top_protective_factors?: string[];
  predicted_class_index?: number;
  error?: string;
}

interface Props {
  explanation: ShapExplanation | null | undefined;
}

export function ShapExplanationPanel({ explanation }: Props) {
  if (!explanation || explanation.error) return null;
  const risks = explanation.top_risk_factors ?? [];
  const protective = explanation.top_protective_factors ?? [];
  if (risks.length === 0 && protective.length === 0) return null;

  return (
    <Card>
      <CardBody>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-md font-semibold text-text-primary">
              Why your risk score looks this way
            </h2>
            <p className="mt-1 text-xs text-text-secondary">
              These are the strongest factors influencing the model's prediction —
              based only on your training behaviour, never on identity or role.
            </p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          {risks.length > 0 && (
            <div className="rounded-lg border border-risk-critical/30 bg-risk-critical/5 p-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-risk-critical">
                <ShieldAlert className="h-4 w-4" />
                What's raising your risk
              </div>
              <ul className="mt-2 space-y-1.5 text-xs text-text-secondary">
                {risks.map((r, i) => (
                  <li key={i} className="flex gap-1.5">
                    <span aria-hidden className="mt-1.5 inline-block h-1 w-1 shrink-0 rounded-full bg-risk-critical" />
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {protective.length > 0 && (
            <div className="rounded-lg border border-success/30 bg-success/5 p-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-success">
                <ShieldCheck className="h-4 w-4" />
                What's protecting you
              </div>
              <ul className="mt-2 space-y-1.5 text-xs text-text-secondary">
                {protective.map((r, i) => (
                  <li key={i} className="flex gap-1.5">
                    <span aria-hidden className="mt-1.5 inline-block h-1 w-1 shrink-0 rounded-full bg-success" />
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <p className="mt-4 text-[11px] italic text-text-muted">
          This explanation is based on your training behaviour only and is not
          used for any employment, access, or performance decision.
        </p>
      </CardBody>
    </Card>
  );
}
