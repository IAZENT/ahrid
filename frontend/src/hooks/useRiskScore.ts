import { useCallback, useEffect, useState } from "react";
import { apiErrorMessage } from "../api/client";
import { scoresApi, type ClusterResponse, type HistoryBucket } from "../api/scores";
import type { RiskLevel, RiskScoreDto } from "../types/api";

type MeResponse = RiskScoreDto | { risk_level: RiskLevel; message: string };

export function isRealScore(value: MeResponse | null): value is RiskScoreDto {
  return !!value && "composite_score" in value;
}

export function useRiskScore() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [history, setHistory] = useState<HistoryBucket[]>([]);
  const [cluster, setCluster] = useState<ClusterResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [meRes, historyRes, clusterRes] = await Promise.all([
        scoresApi.me(),
        scoresApi.history(),
        scoresApi.cluster(),
      ]);
      setMe(meRes as MeResponse);
      setHistory(historyRes);
      setCluster(clusterRes);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  return { me, history, cluster, loading, error, refresh };
}
