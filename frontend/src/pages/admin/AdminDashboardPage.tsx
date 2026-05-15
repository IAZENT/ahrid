import {
  Activity,
  AlertTriangle,
  Brain,
  CheckCircle2,
  Clock,
  Database,
  PlayCircle,
  RefreshCw,
  Users,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { adminApi, type AdminStats } from "../../api/admin";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { cn } from "../../lib/utils";

type JobStatus = "idle" | "running" | "completed" | "failed";

function statusFor(s?: { status?: string; error?: string | null }): JobStatus {
  if (!s) return "idle";
  if (s.status === "running") return "running";
  if (s.error) return "failed";
  if (s.status === "completed") return "completed";
  return "idle";
}

function StatusPill({ status }: { status: JobStatus }) {
  const map: Record<JobStatus, { label: string; cls: string; Icon: typeof Activity }> = {
    idle:      { label: "Idle",      cls: "border-border-default text-text-muted", Icon: Clock },
    running:   { label: "Running",   cls: "border-accent/50 text-accent animate-pulse", Icon: Activity },
    completed: { label: "Completed", cls: "border-success/50 text-success", Icon: CheckCircle2 },
    failed:    { label: "Failed",    cls: "border-risk-critical/50 text-risk-critical", Icon: AlertTriangle },
  };
  const { label, cls, Icon } = map[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-2xs font-medium",
        cls,
      )}
    >
      <Icon className="h-3 w-3" />
      {label}
    </span>
  );
}

function fmtTime(iso?: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleTimeString();
  } catch {
    return iso;
  }
}

function fmtDuration(start?: string | null, end?: string | null): string {
  if (!start) return "—";
  const startMs = new Date(start).getTime();
  const endMs = end ? new Date(end).getTime() : Date.now();
  const sec = Math.max(0, Math.round((endMs - startMs) / 1000));
  if (sec < 60) return `${sec}s`;
  return `${Math.floor(sec / 60)}m ${sec % 60}s`;
}

export function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await adminApi.stats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load stats");
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Auto-poll every 4s while a job is running so the UI reflects progress.
  useEffect(() => {
    const ingestion = stats?.background_jobs?.ingestion as
      | { status?: string; error?: string | null } | undefined;
    const retrain = stats?.background_jobs?.retrain as
      | { status?: string; error?: string | null } | undefined;
    const isRunning =
      statusFor(ingestion) === "running" || statusFor(retrain) === "running";
    if (!isRunning) return;
    const t = window.setInterval(() => void refresh(), 4000);
    return () => window.clearInterval(t);
  }, [stats, refresh]);

  const triggerIngest = async () => {
    setBusy("ingest");
    try { await adminApi.triggerFeedIngestion(); }
    catch (err) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setBusy(null); void refresh(); }
  };
  const triggerRetrain = async () => {
    setBusy("retrain");
    try { await adminApi.retrainModels(); }
    catch (err) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setBusy(null); void refresh(); }
  };

  if (!stats && !error) return <LoadingScreen />;
  if (error && !stats) {
    return (
      <Card>
        <CardBody>
          <p className="text-sm text-risk-critical">{error}</p>
          <Button className="mt-3" onClick={refresh}>
            <RefreshCw className="h-3.5 w-3.5" />
            Retry
          </Button>
        </CardBody>
      </Card>
    );
  }
  if (!stats) return null;

  type JobInfo = {
    status?: string;
    started_at?: string | null;
    finished_at?: string | null;
    error?: string | null;
    result?: { scenarios_created?: number; fetched?: number } & Record<string, unknown> | null;
  };
  const ingestionJob = stats.background_jobs?.ingestion as JobInfo | undefined;
  const retrainJob = stats.background_jobs?.retrain as JobInfo | undefined;
  const ingestionState = statusFor(ingestionJob);
  const retrainState = statusFor(retrainJob);

  const rfModel = stats.ml_models?.random_forest as
    | { trained: boolean; last_trained: string | null; path: string | null; metrics?: Record<string, unknown> }
    | undefined;
  const kmModel = stats.ml_models?.kmeans as
    | { trained: boolean; last_trained: string | null; path: string | null; metrics?: Record<string, unknown> }
    | undefined;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-text-primary">Admin overview</h1>
        <Button variant="ghost" size="sm" onClick={refresh}>
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </Button>
      </div>

      {/* KPI strip */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
        <Kpi icon={Users} label="Users" value={stats.totals.users} />
        <Kpi icon={Users} label="Active" value={stats.totals.active_users} />
        <Kpi icon={Database} label="Scenarios" value={stats.totals.active_scenarios} />
        <Kpi icon={AlertTriangle} label="Threats / 24h" value={stats.totals.threats_last_24h} />
        <Kpi icon={Activity} label="Attempts / 24h" value={stats.totals.attempts_last_24h} />
        <Kpi
          icon={Brain}
          label="RF model"
          value={rfModel?.trained ? "Trained" : "Untrained"}
          tone={rfModel?.trained ? "success" : "muted"}
        />
      </div>

      {/* Background jobs */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <JobCard
          title="Threat ingestion"
          subtitle="PhishStats · OpenPhish · OTX · URLScan"
          state={ingestionState}
          job={ingestionJob}
          onTrigger={triggerIngest}
          busy={busy === "ingest"}
          summary={
            ingestionJob?.result
              ? `Created ${ingestionJob.result.scenarios_created ?? 0} new scenarios from ${ingestionJob.result.fetched ?? 0} feed entries.`
              : null
          }
        />
        <JobCard
          title="Retrain RF + KMeans"
          subtitle="Risk classifier + behavioural clustering"
          state={retrainState}
          job={retrainJob}
          onTrigger={triggerRetrain}
          busy={busy === "retrain"}
          summary={
            retrainJob?.result
              ? "Models retrained successfully — see ML status below."
              : null
          }
          variant="ghost"
        />
      </div>

      {/* ML status */}
      <Card>
        <CardBody>
          <div className="mb-3 flex items-center gap-2">
            <Brain className="h-4 w-4 text-accent" />
            <h2 className="text-md font-semibold text-text-primary">ML model status</h2>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <ModelTile
              label="Random Forest (risk)"
              trained={rfModel?.trained}
              last_trained_at={rfModel?.last_trained ?? null}
              metrics={rfModel?.metrics}
            />
            <ModelTile
              label="KMeans (clusters)"
              trained={kmModel?.trained}
              last_trained_at={kmModel?.last_trained ?? null}
              metrics={kmModel?.metrics}
            />
          </div>
        </CardBody>
      </Card>
    </div>
  );
}

function Kpi({
  icon: Icon, label, value, tone = "default",
}: {
  icon: typeof Users;
  label: string;
  value: number | string;
  tone?: "default" | "success" | "muted";
}) {
  return (
    <Card>
      <CardBody>
        <div className="flex items-center justify-between text-2xs uppercase tracking-wide text-text-muted">
          <span>{label}</span>
          <Icon className="h-4 w-4" />
        </div>
        <div
          className={cn(
            "mt-2 text-2xl font-semibold tabular-nums",
            tone === "success" && "text-success",
            tone === "muted" && "text-text-muted",
          )}
        >
          {value}
        </div>
      </CardBody>
    </Card>
  );
}

interface JobCardProps {
  title: string;
  subtitle: string;
  state: JobStatus;
  job:
    | { status?: string; started_at?: string | null; finished_at?: string | null; error?: string | null }
    | undefined;
  onTrigger: () => void;
  busy: boolean;
  summary: string | null;
  variant?: "primary" | "ghost";
}

function JobCard({
  title, subtitle, state, job, onTrigger, busy, summary, variant = "primary",
}: JobCardProps) {
  return (
    <Card>
      <CardBody className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-md font-semibold text-text-primary">{title}</h3>
            <p className="text-xs text-text-muted">{subtitle}</p>
          </div>
          <StatusPill status={state} />
        </div>

        <dl className="grid grid-cols-3 gap-3 text-xs">
          <div>
            <dt className="text-2xs uppercase tracking-wide text-text-muted">Started</dt>
            <dd className="mt-0.5 tabular-nums text-text-secondary">
              {fmtTime(job?.started_at)}
            </dd>
          </div>
          <div>
            <dt className="text-2xs uppercase tracking-wide text-text-muted">Finished</dt>
            <dd className="mt-0.5 tabular-nums text-text-secondary">
              {fmtTime(job?.finished_at)}
            </dd>
          </div>
          <div>
            <dt className="text-2xs uppercase tracking-wide text-text-muted">Duration</dt>
            <dd className="mt-0.5 tabular-nums text-text-secondary">
              {fmtDuration(job?.started_at, job?.finished_at)}
            </dd>
          </div>
        </dl>

        {summary && state === "completed" && (
          <p className="text-xs text-text-secondary">{summary}</p>
        )}

        {state === "running" && (
          <p className="text-xs text-accent">
            Job is running in the background. This panel auto-refreshes every 4 seconds.
          </p>
        )}

        {job?.error && (
          <p className="text-xs text-risk-critical">{job.error}</p>
        )}

        <Button
          onClick={onTrigger}
          loading={busy || state === "running"}
          disabled={state === "running"}
          variant={variant === "ghost" ? "ghost" : "primary"}
          className="w-full"
        >
          <PlayCircle className="h-3.5 w-3.5" />
          {state === "running" ? "Running…" : `Run ${title.toLowerCase()}`}
        </Button>
      </CardBody>
    </Card>
  );
}

function ModelTile({
  label, trained, last_trained_at, metrics,
}: {
  label: string;
  trained?: boolean;
  last_trained_at?: string | null;
  metrics?: Record<string, unknown>;
}) {
  return (
    <div className="rounded-lg border border-border-subtle bg-bg-elevated/40 p-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-text-primary">{label}</span>
        <StatusPill status={trained ? "completed" : "idle"} />
      </div>
      <div className="mt-2 text-2xs text-text-muted">
        Last trained: {last_trained_at ? new Date(last_trained_at).toLocaleString() : "never"}
      </div>
      {metrics && Object.keys(metrics).length > 0 && (
        <ul className="mt-2 space-y-0.5 text-2xs text-text-secondary">
          {Object.entries(metrics).slice(0, 6).map(([k, v]) => (
            <li key={k} className="flex items-center justify-between gap-2 tabular-nums">
              <span className="truncate text-text-muted">{k.replace(/_/g, " ")}</span>
              <span>{typeof v === "number" ? v.toFixed(3) : String(v)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
