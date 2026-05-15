import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import { useManagerDashboard } from "../../hooks/useManagerData";

export function ManagerDashboardPage() {
  const { dashboard, history, loading, error } = useManagerDashboard();
  if (loading && !dashboard) return <LoadingScreen />;
  if (error) return <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>;
  if (!dashboard) return null;
  const k = dashboard.kpi_cards;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-lg font-semibold">Team intelligence</h1>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Kpi label="Avg risk" value={k.avg_score.toFixed(1)} />
        <Kpi label="High/critical" value={String(k.critical_count)} />
        <Kpi label="Sessions / week" value={String(k.weekly_scenarios)} />
        <Kpi label="Trend" value={`${k.trend_direction} ${k.trend_percent >= 0 ? "+" : ""}${k.trend_percent}%`} />
      </div>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Top risk users</h2>
          {dashboard.top_risk.length === 0 ? (
            <p className="mt-2 text-sm text-text-secondary">All clear.</p>
          ) : (
            <ul className="mt-3 divide-y divide-border-subtle text-sm">
              {dashboard.top_risk.map((r) => (
                <li key={r.user_id} className="flex items-center justify-between py-2">
                  <span>User #{r.user_id.slice(0, 8)}</span>
                  <span className="text-text-secondary">
                    {r.risk_level} · weakest: {r.weakest_category}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Cluster distribution</h2>
          {(() => {
            // KMeans only assigns labels once enough users have completed
            // enough attempts. Hide all-zero rows and explain the empty state.
            const populated = dashboard.cluster_summary.archetypes.filter((a) => a.count > 0);
            if (populated.length === 0) {
              return (
                <p className="mt-2 text-sm text-text-secondary">
                  No archetypes assigned yet. KMeans clustering needs at
                  least 3 users with completed sessions; trigger it via{" "}
                  <em>Admin → Retrain models</em> once the team has
                  trained.
                </p>
              );
            }
            return (
              <ul className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-2">
                {populated.map((a) => (
                  <li
                    key={a.cluster_id}
                    className="flex items-center justify-between rounded-md border border-border-subtle px-3 py-2 text-sm"
                  >
                    <span className="flex items-center gap-2">
                      <span
                        className="inline-block h-2 w-2 rounded-full"
                        style={{ background: a.colour }}
                      />
                      {a.label}
                    </span>
                    <span className="tabular-nums text-text-secondary">
                      {a.count} · {a.percentage.toFixed(0)}%
                    </span>
                  </li>
                ))}
              </ul>
            );
          })()}
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">8-week accuracy</h2>
          {(() => {
            const weeksWithData = history.filter((b) => b.avg_accuracy != null);
            if (weeksWithData.length === 0) {
              return (
                <p className="mt-2 text-sm text-text-secondary">
                  No team activity yet in the last 8 weeks.
                </p>
              );
            }
            return (
              <ul className="mt-3 divide-y divide-border-subtle text-xs tabular-nums">
                {weeksWithData.map((b) => (
                  <li key={b.week_start} className="flex items-center justify-between py-1.5">
                    <span>{b.week_start}</span>
                    <span>
                      {(b.avg_accuracy! * 100).toFixed(0)}% ({b.attempts} attempts)
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

function Kpi({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardBody>
        <div className="text-2xs uppercase tracking-wide text-text-muted">{label}</div>
        <div className="mt-2 text-2xl font-semibold tabular-nums">{value}</div>
      </CardBody>
    </Card>
  );
}
