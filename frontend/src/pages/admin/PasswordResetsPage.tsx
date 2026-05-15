import { useEffect, useState } from "react";
import { adminApi, type PasswordResetRow } from "../../api/admin";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";

export function AdminPasswordResetsPage() {
  const [rows, setRows] = useState<PasswordResetRow[] | null>(null);
  const [token, setToken] = useState<{ id: string; token: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = () =>
    adminApi
      .listPasswordResets("pending")
      .then((d) => setRows(d.requests))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"));

  useEffect(() => { void refresh(); }, []);

  const approve = async (id: string) => {
    const res = await adminApi.approvePasswordReset(id);
    setToken({ id, token: res.reset_token });
    void refresh();
  };
  const reject = async (id: string) => {
    await adminApi.rejectPasswordReset(id);
    void refresh();
  };

  if (rows === null && !error) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold">Password reset queue</h1>

      {token && (
        <Card>
          <CardBody>
            <h2 className="text-md font-semibold text-success">Reset token issued</h2>
            <p className="mt-1 text-xs text-text-secondary">
              Hand this token to the user out-of-band — it will not be shown again.
            </p>
            <pre className="mt-2 overflow-auto rounded-md border border-border-subtle bg-bg-elevated p-2 text-2xs">
              {token.token}
            </pre>
            <Button className="mt-3" variant="ghost" onClick={() => setToken(null)}>
              Dismiss
            </Button>
          </CardBody>
        </Card>
      )}

      {error && <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>}
      <Card>
        <CardBody>
          {(rows ?? []).length === 0 ? (
            <p className="text-sm text-text-secondary">Queue empty.</p>
          ) : (
            <ul className="divide-y divide-border-subtle text-sm">
              {(rows ?? []).map((r) => (
                <li key={r.id} className="flex items-center justify-between py-2">
                  <div>
                    <div>{r.user_email ?? r.user_id.slice(0, 8)}</div>
                    <div className="text-2xs text-text-muted">
                      filed {r.created_at ? new Date(r.created_at).toLocaleString() : "—"}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => approve(r.id)}>Approve</Button>
                    <Button size="sm" variant="ghost" onClick={() => reject(r.id)}>Reject</Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
