import { useEffect, useState } from "react";
import { adminApi, type ThreatRow } from "../../api/admin";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";

export function AdminThreatFeedPage() {
  const [threats, setThreats] = useState<ThreatRow[] | null>(null);
  const [sources, setSources] = useState<Record<string, { total: number; converted: number; latest: string | null }>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      const [list, srcs] = await Promise.all([
        adminApi.listThreats({ limit: 100 }),
        adminApi.threatsBySource(),
      ]);
      setThreats(list.threats);
      setSources(srcs.sources);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    }
  };

  useEffect(() => { void refresh(); }, []);

  const triggerIngest = async () => {
    setBusy(true);
    try { await adminApi.triggerFeedIngestion(); } finally { setBusy(false); void refresh(); }
  };

  if (threats === null && !error) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Threat feeds</h1>
        <Button onClick={triggerIngest} loading={busy}>Run ingestion</Button>
      </div>

      {error && <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>}

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {Object.entries(sources).map(([name, s]) => (
          <Card key={name}>
            <CardBody>
              <div className="text-2xs uppercase tracking-wide text-text-muted">{name}</div>
              <div className="mt-2 text-xl font-semibold tabular-nums">{s.total}</div>
              <div className="text-xs text-text-secondary">{s.converted} converted</div>
              {s.latest && (
                <div className="mt-1 text-2xs text-text-muted">
                  latest {new Date(s.latest).toLocaleString()}
                </div>
              )}
            </CardBody>
          </Card>
        ))}
      </div>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Latest entries</h2>
          <table className="mt-3 w-full text-sm">
            <thead className="text-xs uppercase tracking-wide text-text-muted">
              <tr className="text-left">
                <th className="pb-2">Source</th>
                <th className="pb-2">URL</th>
                <th className="pb-2">Category</th>
                <th className="pb-2">Lure</th>
                <th className="pb-2">Converted</th>
                <th className="pb-2">Ingested</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {(threats ?? []).map((t) => (
                <tr key={t.id}>
                  <td className="py-2">{t.source}</td>
                  <td className="py-2 max-w-[260px] truncate" title={t.original_url}>
                    {t.original_url}
                  </td>
                  <td className="py-2">{t.category ?? ""}</td>
                  <td className="py-2">{t.lure_type ?? ""}</td>
                  <td className="py-2">{t.was_converted ? "yes" : "no"}</td>
                  <td className="py-2 text-2xs">
                    {t.ingested_at ? new Date(t.ingested_at).toLocaleString() : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
