import { useEffect, useState } from "react";
import { GraduationCap } from "lucide-react";
import { managerApi, type TeamRow } from "../../api/manager";
import { Card, CardBody } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Dialog } from "../../components/ui/Dialog";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import { RiskBadge } from "../../components/shared/RiskBadge";
import { CATEGORIES, type CategoryId } from "../../lib/categories";
import { useAuthStore } from "../../store/authStore";
import type { RiskLevel } from "../../types/api";

export function ManagerTeamPage() {
  const role = useAuthStore((s) => s.user?.role);
  const canAssign = role === "admin";
  const [team, setTeam] = useState<TeamRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [target, setTarget] = useState<TeamRow | null>(null);
  const [picked, setPicked] = useState<Set<CategoryId>>(new Set());
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    void managerApi
      .team()
      .then((d) => setTeam(d.team))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"));
  }, []);

  const openAssign = (row: TeamRow) => {
    setTarget(row);
    // Pre-select the user's weakest category as a sensible default.
    setPicked(
      row.weakest_category
        ? new Set<CategoryId>([row.weakest_category as CategoryId])
        : new Set(),
    );
    setNote("");
  };

  const closeAssign = () => {
    setTarget(null);
    setSubmitting(false);
  };

  const togglePicked = (cat: CategoryId) => {
    setPicked((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  const submitAssign = async () => {
    if (!target || picked.size === 0) return;
    setSubmitting(true);
    try {
      await managerApi.assignTraining(target.user_id, {
        categories: Array.from(picked),
        note: note.trim() || undefined,
      });
      setFeedback(`Training assigned to ${target.job_role ?? "user"}.`);
      closeAssign();
    } catch (e) {
      setFeedback(e instanceof Error ? e.message : "Failed to assign training.");
      setSubmitting(false);
    }
  };

  if (team === null && !error) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold">Team</h1>
      {error && (
        <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>
      )}
      {feedback && (
        <Card>
          <CardBody>
            <p className="text-sm text-success">{feedback}</p>
          </CardBody>
        </Card>
      )}
      <Card>
        <CardBody>
          <table className="w-full text-sm">
            <thead className="text-xs uppercase tracking-wide text-text-muted">
              <tr className="text-left">
                <th className="pb-2">Job role</th>
                <th className="pb-2">Department</th>
                <th className="pb-2">Risk</th>
                <th className="pb-2">Archetype</th>
                <th className="pb-2">Weakest</th>
                <th className="pb-2">Last active</th>
                {canAssign && <th className="pb-2 text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {(team ?? []).map((u) => (
                <tr key={u.user_id}>
                  <td className="py-2">{u.job_role ?? ""}</td>
                  <td className="py-2">{u.department ?? ""}</td>
                  <td className="py-2"><RiskBadge level={u.risk_level as RiskLevel} /></td>
                  <td className="py-2">{u.cluster_label ?? ""}</td>
                  <td className="py-2">{u.weakest_category ?? ""}</td>
                  <td className="py-2">
                    {u.last_active ? new Date(u.last_active).toLocaleDateString() : ""}
                  </td>
                  {canAssign && (
                    <td className="py-2 text-right">
                      <Button size="sm" variant="ghost" onClick={() => openAssign(u)}>
                        <GraduationCap className="h-3.5 w-3.5" />
                        Assign
                      </Button>
                    </td>
                  )}
                </tr>
              ))}
              {team && team.length === 0 && (
                <tr>
                  <td colSpan={canAssign ? 7 : 6} className="py-4 text-text-secondary">
                    No team members.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </CardBody>
      </Card>

      <Dialog
        open={target !== null}
        onClose={closeAssign}
        title="Assign training"
        description={
          target
            ? `Pick one or more categories to surface in this user's next session.`
            : undefined
        }
        widthClass="max-w-xl"
        footer={
          <>
            <Button variant="ghost" onClick={closeAssign} disabled={submitting}>
              Cancel
            </Button>
            <Button
              onClick={submitAssign}
              disabled={picked.size === 0 || submitting}
            >
              {submitting ? "Assigning…" : `Assign ${picked.size || ""}`.trim()}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            {Object.values(CATEGORIES).map((c) => {
              const Icon = c.icon;
              const active = picked.has(c.id);
              return (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => togglePicked(c.id)}
                  className={
                    "flex items-start gap-2 rounded-lg border px-3 py-2 text-left text-xs transition-colors " +
                    (active
                      ? "border-accent bg-accent/10 text-text-primary"
                      : "border-border-subtle bg-bg-base hover:border-border-strong")
                  }
                >
                  <span
                    className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md"
                    style={{ background: c.colour + "22", color: c.colour }}
                  >
                    <Icon className="h-3.5 w-3.5" />
                  </span>
                  <span>
                    <span className="block font-medium text-text-primary">{c.displayName}</span>
                    <span className="block text-text-secondary">{c.description}</span>
                  </span>
                </button>
              );
            })}
          </div>
          <label className="block text-xs">
            <span className="mb-1 block font-medium text-text-secondary">
              Optional note for the user
            </span>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
              maxLength={400}
              placeholder="Why this is being assigned…"
              className="w-full rounded-md border border-border-subtle bg-bg-base px-2 py-1.5 text-sm text-text-primary focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
            />
          </label>
        </div>
      </Dialog>
    </div>
  );
}

