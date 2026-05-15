import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import { useManagerDashboard } from "../../hooks/useManagerData";

export function ManagerClustersPage() {
  const { dashboard, loading, error } = useManagerDashboard();
  if (loading && !dashboard) return <LoadingScreen />;
  if (error) return <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>;
  if (!dashboard) return null;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold">Behavioural clusters (KMeans)</h1>
      <p className="text-sm text-text-secondary">
        Five archetypes derived from a 6-feature behavioural vector
        (response time, accuracy, accuracy variance, fast-attempt rate,
        session count, session consistency).
      </p>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {dashboard.cluster_summary.archetypes.map((a) => (
          <Card key={a.cluster_id}>
            <CardBody>
              <div className="flex items-center justify-between">
                <h2 className="text-md font-semibold flex items-center gap-2">
                  <span
                    className="inline-block h-3 w-3 rounded-full"
                    style={{ background: a.colour }}
                  />
                  {a.label}
                </h2>
                <span className="text-xs text-text-secondary tabular-nums">
                  {a.count} · {a.percentage.toFixed(0)}%
                </span>
              </div>
              <p className="mt-2 text-xs text-text-muted">
                <strong>Recommended intervention:</strong> {a.intervention}
              </p>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}
