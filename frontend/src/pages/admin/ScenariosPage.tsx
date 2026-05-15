import { useEffect, useState } from "react";
import { adminApi, type ScenarioDto } from "../../api/admin";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";

export function AdminScenariosPage() {
  const [scenarios, setScenarios] = useState<ScenarioDto[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = () =>
    adminApi
      .listScenarios({ limit: 200 })
      .then((d) => setScenarios(d.scenarios))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"));

  useEffect(() => { void refresh(); }, []);

  const toggle = async (s: ScenarioDto) => {
    await adminApi.updateScenario(s.id, { is_active: !s.is_active });
    void refresh();
  };

  if (scenarios === null && !error) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold">Scenarios</h1>
      {error && <Card><CardBody><p className="text-risk-critical">{error}</p></CardBody></Card>}
      <Card>
        <CardBody>
          <table className="w-full text-sm">
            <thead className="text-xs uppercase tracking-wide text-text-muted">
              <tr className="text-left">
                <th className="pb-2">Title</th>
                <th className="pb-2">Category</th>
                <th className="pb-2">Diff</th>
                <th className="pb-2">Source</th>
                <th className="pb-2">Acc.</th>
                <th className="pb-2">Active</th>
                <th />
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {(scenarios ?? []).map((s) => (
                <tr key={s.id}>
                  <td className="py-2">{s.title}</td>
                  <td className="py-2">{s.category}</td>
                  <td className="py-2 tabular-nums">{s.difficulty}</td>
                  <td className="py-2">{s.source}</td>
                  <td className="py-2 tabular-nums">{(s.accuracy_rate * 100).toFixed(0)}%</td>
                  <td className="py-2">{s.is_active ? "yes" : "no"}</td>
                  <td className="py-2">
                    <Button size="sm" variant="ghost" onClick={() => toggle(s)}>
                      {s.is_active ? "Deactivate" : "Activate"}
                    </Button>
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
