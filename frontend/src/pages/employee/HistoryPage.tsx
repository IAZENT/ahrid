import { useEffect, useState } from "react";
import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import { trainingApi, type SessionRow } from "../../api/training";

export function HistoryPage() {
  const [sessions, setSessions] = useState<SessionRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void trainingApi
      .sessions({ limit: 50 })
      .then((d) => setSessions(d.sessions))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  if (sessions === null && !error) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-text-primary">Session history</h1>
      {error && (
        <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>
      )}
      <Card>
        <CardBody>
          {sessions && sessions.length === 0 ? (
            <p className="text-sm text-text-secondary">No sessions yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-xs uppercase tracking-wide text-text-muted">
                <tr className="text-left">
                  <th className="pb-2">Started</th>
                  <th className="pb-2">Duration</th>
                  <th className="pb-2">Score</th>
                  <th className="pb-2">Accuracy</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                {sessions?.map((s) => (
                  <tr key={s.session_id}>
                    <td className="py-2">
                      {s.started_at ? new Date(s.started_at).toLocaleString() : ""}
                    </td>
                    <td className="py-2 tabular-nums">{s.duration_seconds.toFixed(0)}s</td>
                    <td className="py-2 tabular-nums">
                      {s.correct}/{s.total_questions}
                    </td>
                    <td className="py-2 tabular-nums">
                      {(s.accuracy * 100).toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
