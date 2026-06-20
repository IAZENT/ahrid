import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { useAuthStore } from "../../store/authStore";

export function ManagerReportsPage() {
  const token = useAuthStore((s) => s.accessToken);

  const downloadCsv = async () => {
    const base = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000").replace(/\/$/, "");
    const res = await fetch(`${base}/api/v1/manager/reports/summary?weeks=4`, {
      headers: { Authorization: token ? `Bearer ${token}` : "" },
    });
    if (!res.ok) {
      alert("Failed to fetch report.");
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ahrip_weekly_summary.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold">Reports</h1>
      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Weekly summary CSV</h2>
          <p className="mt-1 text-sm text-text-secondary">
            Per-week attempt counts, accuracy, and unique-user totals across the team.
          </p>
          <Button className="mt-3" onClick={downloadCsv}>
            Download CSV
          </Button>
        </CardBody>
      </Card>
    </div>
  );
}
