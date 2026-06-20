import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, Target, TrendingUp } from "lucide-react";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { useAuthStore } from "../../store/authStore";
import { useRiskScore, isRealScore } from "../../hooks/useRiskScore";
import { trainingApi, type SessionRow } from "../../api/training";
import { RiskBadge } from "../../components/shared/RiskBadge";

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const { me, history, loading } = useRiskScore();
  const [recent, setRecent] = useState<SessionRow[]>([]);

  useEffect(() => {
    void trainingApi.sessions({ limit: 5 }).then((d) => setRecent(d.sessions));
  }, []);

  const composite = isRealScore(me) ? me.composite_score : null;
  const level = isRealScore(me) ? me.risk_level : (me?.risk_level ?? "unknown");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-text-primary">
          Welcome back, {user?.first_name ?? "there"}.
        </h1>
        <p className="mt-1 text-sm text-text-secondary">
          Adaptive training tailored to your role and recent activity.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card data-tour="risk-score">
          <CardBody>
            <div className="flex items-center justify-between text-2xs uppercase tracking-wide text-text-muted">
              <span>Current risk</span>
              <Activity className="h-4 w-4" />
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-semibold tabular-nums">
                {composite !== null ? composite.toFixed(0) : ""}
              </span>
              <RiskBadge level={level} />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center justify-between text-2xs uppercase tracking-wide text-text-muted">
              <span>Sessions completed</span>
              <Target className="h-4 w-4" />
            </div>
            <div className="mt-2 text-3xl font-semibold tabular-nums">
              {recent.length}
            </div>
            <div className="mt-1 text-xs text-text-secondary">latest activity</div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className="flex items-center justify-between text-2xs uppercase tracking-wide text-text-muted">
              <span>Trend</span>
              <TrendingUp className="h-4 w-4" />
            </div>
            <div className="mt-2 text-3xl font-semibold tabular-nums">
              {history.filter((b) => b.accuracy != null).length}
            </div>
            <div className="mt-1 text-xs text-text-secondary">
              weeks with activity (last 8)
            </div>
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-md font-semibold text-text-primary">Ready to train?</h2>
              <p className="mt-1 text-sm text-text-secondary">
                Start an adaptive 20-question session tailored to your weakest category.
              </p>
            </div>
            <Link to="/app/training">
              <Button>Start session</Button>
            </Link>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold text-text-primary">Recent sessions</h2>
          {loading ? (
            <p className="mt-3 text-sm text-text-secondary">Loading…</p>
          ) : recent.length === 0 ? (
            <p className="mt-3 text-sm text-text-secondary">
              No sessions yet. Start your first one above.
            </p>
          ) : (
            <ul className="mt-3 divide-y divide-border-subtle text-sm">
              {recent.map((s) => (
                <li key={s.session_id} className="flex items-center justify-between py-2">
                  <span>
                    {s.started_at ? new Date(s.started_at).toLocaleString() : ""}
                  </span>
                  <span className="tabular-nums text-text-secondary">
                    {s.correct}/{s.total_questions} · {(s.accuracy * 100).toFixed(0)}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
