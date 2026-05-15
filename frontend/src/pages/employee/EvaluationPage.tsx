/**
 * Evaluation page (master spec §6.6).
 *
 * Three-stage flow:
 *   1. Pre-assessment (HAIS-Q, 7 items)  shown until submitted.
 *   2. Post-assessment (HAIS-Q again) + SUS  unlocked once the user
 *      has the pre row stored.
 *   3. Confirmation card with the per-user delta if both phases done.
 *
 * Submitting any phase optimistically updates state and refetches.
 */
import { useEffect, useState } from "react";
import { Check, ClipboardCheck } from "lucide-react";
import { Card, CardBody } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import {
  evalApi,
  type AwarenessMe,
  type AwarenessQuestion,
  type ScalePoint,
} from "../../api/evaluation";

const SUS_SCALE: ScalePoint[] = [
  { value: 1, label: "Strongly Disagree" },
  { value: 2, label: "Disagree" },
  { value: 3, label: "Neutral" },
  { value: 4, label: "Agree" },
  { value: 5, label: "Strongly Agree" },
];

interface LikertProps {
  questions: AwarenessQuestion[];
  scale: ScalePoint[];
  values: Record<string, number>;
  onChange: (id: string, value: number) => void;
}
function LikertGrid({ questions, scale, values, onChange }: LikertProps) {
  return (
    <div className="space-y-3">
      {questions.map((q, i) => (
        <div
          key={q.id}
          className="rounded-lg border border-border-subtle bg-bg-base p-3"
        >
          <p className="text-sm text-text-primary">
            <span className="text-text-muted">{i + 1}.</span> {q.text}
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {scale.map((s) => (
              <button
                key={s.value}
                type="button"
                onClick={() => onChange(q.id, s.value)}
                className={
                  "rounded-md border px-2 py-1 text-[11px] transition-colors " +
                  (values[q.id] === s.value
                    ? "border-accent bg-accent/10 text-text-primary"
                    : "border-border-subtle bg-bg-surface text-text-secondary hover:border-border-strong")
                }
              >
                {s.value}  {s.label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export function EvaluationPage() {
  const [awarenessQs, setAwarenessQs] = useState<AwarenessQuestion[]>([]);
  const [awarenessScale, setAwarenessScale] = useState<ScalePoint[]>([]);
  const [me, setMe] = useState<AwarenessMe | null>(null);
  const [susQs, setSusQs] = useState<AwarenessQuestion[]>([]);

  const [preValues, setPreValues] = useState<Record<string, number>>({});
  const [postValues, setPostValues] = useState<Record<string, number>>({});
  const [susValues, setSusValues] = useState<Record<string, number>>({});

  const [submitting, setSubmitting] = useState<"pre" | "post" | "sus" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [susResult, setSusResult] = useState<{ score: number; grade: string } | null>(null);

  const refresh = async () => {
    const meData = await evalApi.awarenessMe();
    setMe(meData);
  };

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const [aq, sq, m] = await Promise.all([
          evalApi.awarenessQuestions(),
          evalApi.susQuestions(),
          evalApi.awarenessMe(),
        ]);
        if (!active) return;
        setAwarenessQs(aq.questions);
        setAwarenessScale(aq.scale);
        setSusQs(sq.questions);
        setMe(m);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load evaluation.");
      }
    })();
    return () => { active = false; };
  }, []);

  const submitPhase = async (phase: "pre" | "post") => {
    const values = phase === "pre" ? preValues : postValues;
    if (Object.keys(values).length < awarenessQs.length) {
      setError("Please answer every question.");
      return;
    }
    setSubmitting(phase);
    setError(null);
    try {
      await evalApi.submitAwareness(phase, values);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submission failed.");
    } finally {
      setSubmitting(null);
    }
  };

  const submitSus = async () => {
    if (Object.keys(susValues).length < susQs.length) {
      setError("Please answer every question.");
      return;
    }
    setSubmitting("sus");
    setError(null);
    try {
      const row = await evalApi.submitSus(susValues);
      setSusResult({ score: row.sus_score, grade: row.grade ?? "" });
      setSusValues({});
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submission failed.");
    } finally {
      setSubmitting(null);
    }
  };

  if (!me || awarenessQs.length === 0) return <LoadingScreen />;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <header>
        <h1 className="text-lg font-semibold text-text-primary">
          Evaluation  Awareness & Usability
        </h1>
        <p className="mt-1 text-xs text-text-secondary">
          Two short questionnaires used to measure how this system affected your
          awareness over time and how usable you found it. Responses are private.
        </p>
      </header>

      {error && (
        <Card><CardBody><p className="text-sm text-risk-critical">{error}</p></CardBody></Card>
      )}

      {/* Stage 1  Pre */}
      {!me.pre ? (
        <Card>
          <CardBody>
            <h2 className="text-md font-semibold">Step 1  Pre-training awareness</h2>
            <p className="mt-1 text-xs text-text-secondary">
              Please answer the 7 questions below before you start training.
            </p>
            <div className="mt-4">
              <LikertGrid
                questions={awarenessQs}
                scale={awarenessScale}
                values={preValues}
                onChange={(id, v) => setPreValues((s) => ({ ...s, [id]: v }))}
              />
            </div>
            <div className="mt-4 flex justify-end">
              <Button
                onClick={() => submitPhase("pre")}
                disabled={submitting !== null}
              >
                {submitting === "pre" ? "Submitting" : "Submit pre-assessment"}
              </Button>
            </div>
          </CardBody>
        </Card>
      ) : (
        <Card>
          <CardBody className="flex items-center gap-3 text-sm">
            <Check className="h-4 w-4 text-success" />
            <span>
              Pre-assessment submitted on{" "}
              {me.pre.completed_at ? new Date(me.pre.completed_at).toLocaleDateString() : ""}.{" "}
              <strong>Score {me.pre.score.toFixed(1)} / 100.</strong>
            </span>
          </CardBody>
        </Card>
      )}

      {/* Stage 2  Post */}
      {me.pre && !me.post && (
        <Card>
          <CardBody>
            <h2 className="text-md font-semibold">Step 2  Post-training awareness</h2>
            <p className="mt-1 text-xs text-text-secondary">
              Please retake the same 7 questions now that you've completed
              several training sessions.
            </p>
            <div className="mt-4">
              <LikertGrid
                questions={awarenessQs}
                scale={awarenessScale}
                values={postValues}
                onChange={(id, v) => setPostValues((s) => ({ ...s, [id]: v }))}
              />
            </div>
            <div className="mt-4 flex justify-end">
              <Button
                onClick={() => submitPhase("post")}
                disabled={submitting !== null}
              >
                {submitting === "post" ? "Submitting" : "Submit post-assessment"}
              </Button>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Stage 3  Confirmation */}
      {me.pre && me.post && (
        <Card>
          <CardBody>
            <div className="flex items-start gap-3">
              <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-md bg-success/15 text-success">
                <ClipboardCheck className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-md font-semibold">Awareness assessment complete</h2>
                <p className="mt-1 text-xs text-text-secondary">
                  Pre {me.pre.score.toFixed(1)}  Post {me.post.score.toFixed(1)} (delta{" "}
                  <strong className={me.delta != null && me.delta >= 0 ? "text-success" : "text-risk-critical"}>
                    {me.delta != null ? (me.delta >= 0 ? "+" : "") + me.delta.toFixed(1) : ""}
                  </strong>
                  ). Thank you  your responses help evaluate the system.
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* SUS  always available */}
      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">System Usability Scale (SUS)</h2>
          <p className="mt-1 text-xs text-text-secondary">
            Ten standard questions about how usable you found this system.
            You can submit this independently of the awareness assessment.
          </p>
          {susResult ? (
            <p className="mt-3 text-sm text-success">
              Submitted. Your SUS score: <strong>{susResult.score.toFixed(1)}</strong>
              {susResult.grade && <> &middot; Grade: {susResult.grade}</>}.
            </p>
          ) : (
            <>
              <div className="mt-3">
                <LikertGrid
                  questions={susQs}
                  scale={SUS_SCALE}
                  values={susValues}
                  onChange={(id, v) => setSusValues((s) => ({ ...s, [id]: v }))}
                />
              </div>
              <div className="mt-4 flex justify-end">
                <Button onClick={submitSus} disabled={submitting !== null}>
                  {submitting === "sus" ? "Submitting" : "Submit SUS"}
                </Button>
              </div>
            </>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
