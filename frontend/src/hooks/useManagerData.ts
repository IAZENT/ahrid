import { useCallback, useEffect, useState } from "react";
import { apiErrorMessage } from "../api/client";
import { managerApi, type DashboardResponse, type HistoryBucket } from "../api/manager";

export function useManagerDashboard() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [history, setHistory] = useState<HistoryBucket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [d, h] = await Promise.all([managerApi.dashboard(), managerApi.history(8)]);
      setDashboard(d);
      setHistory(h);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  return { dashboard, history, loading, error, refresh };
}
