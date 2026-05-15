/**
 * Transparency policy page (master spec §7.2).
 *
 * Public — accessible to every authenticated role and unauthenticated
 * visitors via a deep link. Pulls the policy text from the backend so
 * an admin can update it without a frontend deploy.
 */
import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { Card, CardBody } from "../components/ui/Card";
import { LoadingScreen } from "../components/shared/LoadingSpinner";
import { evalApi } from "../api/evaluation";

export function TransparencyPage() {
  const [policy, setPolicy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void evalApi
      .transparencyPolicy()
      .then((d) => { if (active) setPolicy(d.policy); })
      .catch((e) => {
        if (active) setError(e instanceof Error ? e.message : "Failed to load policy.");
      });
    return () => { active = false; };
  }, []);

  if (policy === null && !error) return <LoadingScreen />;

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardBody>
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-accent/15 text-accent">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-text-primary">
                Transparency policy
              </h1>
              <p className="mt-1 text-xs text-text-secondary">
                How AHRID collects, uses, and explains your training data.
              </p>
            </div>
          </div>

          {error ? (
            <p className="mt-4 text-sm text-risk-critical">{error}</p>
          ) : (
            <pre className="mt-5 whitespace-pre-wrap rounded-lg border border-border-subtle bg-bg-base p-4 text-xs leading-relaxed text-text-primary">
              {policy}
            </pre>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
