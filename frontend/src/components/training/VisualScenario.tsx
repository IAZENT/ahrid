import { AlertTriangle } from "lucide-react";
import { useMemo } from "react";

interface VisualScenarioProps {
  html: string;
  visualType?: string | null;
}

/**
 * Render ``visual_html`` inside a sandboxed srcdoc iframe so that any markup
 * (or  defensively  any script that slipped past the sanitiser) cannot
 * touch our DOM or cookies. The outer frame never loads a remote URL.
 *
 * The sandbox attribute intentionally omits ``allow-scripts`` and
 * ``allow-same-origin`` so the iframe runs in a null origin with JS disabled.
 */
export function VisualScenario({ html, visualType }: VisualScenarioProps) {
  const srcdoc = useMemo(
    () => `
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<base target="_blank">
<style>
  html, body { margin: 0; padding: 0; background: #F8FAFC; color: #0F172A;
    font-family: Inter, system-ui, sans-serif; font-size: 14px; line-height: 1.5; }
  a { color: inherit; pointer-events: none; text-decoration: underline; }
</style>
</head>
<body>${html}</body>
</html>`.trim(),
    [html],
  );

  return (
    <div className="overflow-hidden rounded-lg border border-border-default bg-bg-surface">
      <div className="flex items-center gap-2 border-b border-border-subtle bg-warning/10 px-3 py-2 text-2xs font-medium uppercase tracking-wide text-warning">
        <AlertTriangle className="h-3.5 w-3.5" />
        Simulated Attack  this is a training scenario
        {visualType && (
          <span className="ml-auto rounded-full bg-warning/15 px-1.5 py-0.5 text-[10px] font-semibold normal-case text-warning">
            {visualType.replace(/_/g, " ")}
          </span>
        )}
      </div>
      <iframe
        title="Simulated attack preview"
        srcDoc={srcdoc}
        sandbox=""
        className="block h-[320px] w-full bg-white"
      />
    </div>
  );
}
