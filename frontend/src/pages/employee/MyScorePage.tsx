import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import { RiskBadge } from "../../components/shared/RiskBadge";
import { ShapExplanationPanel } from "../../components/shared/ShapExplanationPanel";
import { useRiskScore, isRealScore } from "../../hooks/useRiskScore";

export function MyScorePage() {
  const { me, history, cluster, loading, error } = useRiskScore();

  if (loading && !me) return <LoadingScreen />;
  if (error) {
    return <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>;
  }
  if (!me) return null;

  return (
    <div className="flex flex-col gap-6">
      <Card data-tour="my-risk-score">
        <CardBody>
          <h2 className="text-md font-semibold text-text-primary">Risk score</h2>
          {isRealScore(me) ? (
            <div className="mt-3 flex items-center gap-4">
              <div className="text-4xl font-semibold tabular-nums">
                {me.composite_score.toFixed(1)}
              </div>
              <RiskBadge level={me.risk_level} />
              <div className="text-xs text-text-secondary">
                Based on {me.attempts_count ?? 0} attempts.
              </div>
            </div>
          ) : (
            <p className="mt-2 text-sm text-text-secondary">{me.message}</p>
          )}
        </CardBody>
      </Card>

      {isRealScore(me) && (
        <ShapExplanationPanel explanation={me.shap_explanation ?? null} />
      )}

      {isRealScore(me) && me.rf_prediction && (
        <Card>
          <CardBody>
            <h2 className="text-md font-semibold text-text-primary">Random Forest prediction</h2>
            <div className="mt-2 flex items-center gap-3">
              <RiskBadge level={me.rf_prediction.predicted_risk_level} />
              <span className="text-sm text-text-secondary">
                Confidence {(me.rf_prediction.confidence * 100).toFixed(0)}%
              </span>
            </div>
            {Object.keys(me.rf_prediction.feature_importances).length > 0 && (
              <div className="mt-3 text-xs text-text-secondary">
                <strong>Top features driving the prediction:</strong>
                <ul className="mt-1 space-y-1">
                  {Object.entries(me.rf_prediction.feature_importances).map(([k, v]) => (
                    <li key={k} className="flex items-center justify-between gap-2">
                      <span className="truncate text-text-muted">
                        {k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                      </span>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-bg-elevated">
                          <div
                            className="h-full rounded-full bg-accent"
                            style={{ width: `${Math.min(100, v * 100 * 5)}%` }}
                          />
                        </div>
                        <span className="tabular-nums text-text-muted">{v.toFixed(3)}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardBody>
        </Card>
      )}

      {cluster?.archetype_label && (
        <Card>
          <CardBody>
            <h2 className="text-md font-semibold text-text-primary">Behavioural archetype</h2>
            <div className="mt-2 flex items-center gap-3">
              <span
                className="inline-block h-3 w-3 rounded-full"
                style={{ background: cluster.archetype_colour ?? "#888" }}
              />
              <strong>{cluster.archetype_label}</strong>
            </div>
            {cluster.archetype_description && (
              <p className="mt-2 text-sm text-text-secondary">
                {cluster.archetype_description}
              </p>
            )}
            {cluster.intervention && (
              <p className="mt-2 text-xs text-text-muted">
                <strong>Recommended:</strong> {cluster.intervention}
              </p>
            )}
          </CardBody>
        </Card>
      )}

      <Card data-tour="category-trend">
        <CardBody>
          <h2 className="text-md font-semibold text-text-primary">8-week trend</h2>
          {(() => {
            // Only show weeks that actually have data  empty weeks add
            // visual noise without conveying useful information.
            const weeksWithData = history.filter((b) => b.accuracy != null);
            if (weeksWithData.length === 0) {
              return (
                <p className="mt-2 text-sm text-text-secondary">
                  No history yet  complete a training session to see your trend.
                </p>
              );
            }
            return (
              <ul className="mt-3 divide-y divide-border-subtle text-xs tabular-nums">
                {weeksWithData.map((b) => (
                  <li key={b.week_start} className="flex items-center justify-between py-1.5">
                    <span>{b.week_start} → {b.week_end}</span>
                    <span>
                      {(b.accuracy! * 100).toFixed(0)}% acc · {b.composite_score?.toFixed(0)} risk
                    </span>
                  </li>
                ))}
              </ul>
            );
          })()}
        </CardBody>
      </Card>
    </div>
  );
}
