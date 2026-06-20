/**
 * Admin Evaluation panel (master spec §6.6 admin tab).
 *
 * Shows three cards:
 *   1. RF metrics  F1, baseline F1, improvement, class distribution.
 *   2. Awareness uplift  pre/post mean, delta, Cohen's d, p-value.
 *   3. SUS summary  mean score + grade + per-grade distribution bars.
 */
import { useEffect, useState } from "react";
import { Activity, BarChart3, BrainCircuit, Sparkles } from "lucide-react";
import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import {
  evalApi,
  type AwarenessUplift,
  type RfMetrics,
  type SusSummary,
} from "../../api/evaluation";

function StatRow({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <span className="text-xs text-text-secondary">{label}</span>
      <span className="text-sm tabular-nums text-text-primary">
        {value}
        {hint && <span className="ml-1 text-xs text-text-muted">{hint}</span>}
      </span>
    </div>
  );
}

export function EvaluationAdminPage() {
  const [rf, setRf]       = useState<RfMetrics | null>(null);
  const [rfErr, setRfErr] = useState<string | null>(null);
  const [up, setUp]       = useState<AwarenessUplift | null>(null);
  const [sus, setSus]     = useState<SusSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const [upRes, susRes] = await Promise.all([
          evalApi.awarenessUplift(),
          evalApi.susSummary(),
        ]);
        if (!active) return;
        setUp(upRes);
        setSus(susRes);
      } catch (e) {
        if (!active) return;
        // non-fatal  page can still render the parts that loaded.
        console.warn("Eval load failed", e);
      }

      try {
        const r = await evalApi.rfMetrics();
        if (!active) return;
        setRf(r);
      } catch (e: unknown) {
        if (!active) return;
        setRfErr(e instanceof Error ? e.message : "RF metrics unavailable.");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  if (loading && !up && !sus) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-text-primary">Evaluation</h1>
        <p className="mt-1 text-xs text-text-secondary">
          Quantitative evidence for the thesis: model quality, awareness uplift,
          and perceived usability.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* RF Metrics */}
        <Card>
          <CardBody>
            <div className="flex items-center gap-2">
              <BrainCircuit className="h-4 w-4 text-accent" />
              <h2 className="text-md font-semibold">RF model quality</h2>
            </div>
            {rfErr && (
              <p className="mt-3 text-xs text-risk-critical">
                {rfErr}  train the model via <em>Retrain models</em> first.
              </p>
            )}
            {rf && (
              <div className="mt-3 space-y-1.5">
                {rf.accuracy != null && (
                  <StatRow label="Accuracy" value={`${(rf.accuracy * 100).toFixed(0)}%`} />
                )}
                <StatRow label="F1 (weighted)"     value={rf.f1_weighted.toFixed(3)} />
                {rf.cross_validation?.mean != null && (
                  <StatRow
                    label="CV F1 (macro)"
                    value={`${rf.cross_validation.mean.toFixed(3)}${rf.cross_validation.std != null ? ` \u00b1${rf.cross_validation.std.toFixed(3)}` : ""}`}
                  />
                )}
                <StatRow label="Baseline F1 (rule-based)" value={rf.baseline_f1.toFixed(3)} />
                <StatRow
                  label="Improvement"
                  value={`${rf.improvement_pp >= 0 ? "+" : ""}${rf.improvement_pp.toFixed(1)} pp`}
                />
                <StatRow label="Training samples" value={String(rf.n_samples ?? rf.n_test_samples)} />
                {rf.n_features != null && (
                  <StatRow label="Features" value={String(rf.n_features)} />
                )}
                {rf.smote && (
                  <StatRow label="SMOTE" value={rf.smote.applied ? "Applied" : "Not applied"} />
                )}
                {rf.class_distribution && Object.keys(rf.class_distribution).length > 0 && (
                  <div className="mt-3 border-t border-border-subtle pt-2 text-xs">
                    <span className="text-text-muted">Class distribution:</span>
                    <ul className="mt-1 grid grid-cols-2 gap-1 tabular-nums">
                      {Object.entries(rf.class_distribution).map(([k, v]) => (
                        <li key={k} className="flex justify-between rounded-md border border-border-subtle px-2 py-1">
                          <span>{k}</span><span className="text-text-muted">{v}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </CardBody>
        </Card>

        {/* Awareness Uplift */}
        <Card>
          <CardBody>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-success" />
              <h2 className="text-md font-semibold">Awareness uplift</h2>
            </div>
            {up && up.n_participants > 0 ? (
              <div className="mt-3 space-y-1.5">
                <StatRow label="Participants"       value={String(up.n_participants)} />
                <StatRow label="Mean pre-score"     value={`${up.mean_pre_score?.toFixed(1) ?? ""}/100`} />
                <StatRow label="Mean post-score"    value={`${up.mean_post_score?.toFixed(1) ?? ""}/100`} />
                <StatRow
                  label="Mean delta"
                  value={up.mean_delta != null ? `${up.mean_delta >= 0 ? "+" : ""}${up.mean_delta.toFixed(1)}` : ""}
                />
                <StatRow label="Cohen's d"          value={up.cohens_d != null ? up.cohens_d.toFixed(2) : ""} hint={up.cohens_d != null && up.cohens_d >= 0.5 ? " medium+" : undefined} />
                <StatRow label="Paired t-test p-value" value={up.p_value != null ? up.p_value.toFixed(4) : ""} hint={up.p_value != null && up.p_value < 0.05 ? "(sig.)" : undefined} />
              </div>
            ) : (
              <p className="mt-3 text-xs text-text-secondary">
                No paired pre/post responses yet. Run <code>seed_eval_data.py</code> or wait
                for participants to complete the post-assessment.
              </p>
            )}
          </CardBody>
        </Card>

        {/* SUS */}
        <Card>
          <CardBody>
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-warning" />
              <h2 className="text-md font-semibold">System Usability Scale</h2>
            </div>
            {sus && sus.n > 0 ? (
              <div className="mt-3 space-y-1.5">
                <StatRow label="Responses" value={String(sus.n)} />
                <StatRow label="Mean SUS"   value={sus.mean != null ? `${sus.mean.toFixed(1)}/100` : ""} hint={sus.grade ? `(${sus.grade})` : undefined} />
                <div className="mt-3 space-y-1">
                  {Object.entries(sus.distribution).map(([grade, n]) => {
                    const pct = sus.n ? Math.round((n / sus.n) * 100) : 0;
                    return (
                      <div key={grade} className="flex items-center gap-2 text-xs">
                        <span className="w-20 shrink-0 text-text-secondary">{grade}</span>
                        <div className="h-2 flex-1 overflow-hidden rounded-full bg-bg-elevated">
                          <div
                            className="h-full bg-accent"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="w-10 text-right tabular-nums text-text-muted">{n}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <p className="mt-3 text-xs text-text-secondary">No SUS responses yet.</p>
            )}
          </CardBody>
        </Card>

        {/* Help card */}
        <Card>
          <CardBody>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-accent" />
              <h2 className="text-md font-semibold">How these metrics map to the thesis</h2>
            </div>
            <ul className="mt-3 space-y-2 text-xs text-text-secondary">
              <li>
                <strong className="text-text-primary">RF F1 vs baseline</strong> answers RQ1
                / H1: does an adaptive ML pipeline outperform a rule-based threshold?
              </li>
              <li>
                <strong className="text-text-primary">Awareness uplift (Cohen's d)</strong>
                {" "}quantifies the training effect; d  0.5 indicates a medium effect.
              </li>
              <li>
                <strong className="text-text-primary">SUS</strong> &gt; 68 is the industry
                threshold for "above average usability".
              </li>
            </ul>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
