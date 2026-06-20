import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Info,
  Lightbulb,
  Play,
  RotateCcw,
  Timer,
  Trophy,
  XCircle,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { apiErrorMessage } from "../../api/client";
import {
  trainingApi,
  type AnswerResponse,
  type SessionStartResponse,
  type SessionSummary,
  type TrainingConfig,
} from "../../api/training";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import { AnswerOptions } from "../../components/training/AnswerOptions";
import { CategoryBadge } from "../../components/training/CategoryBadge";
import { ExplanationTimer } from "../../components/training/ExplanationTimer";
import { ProgressRing } from "../../components/training/ProgressRing";
import { VisualScenario } from "../../components/training/VisualScenario";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { cn } from "../../lib/utils";

type Letter = "A" | "B" | "C" | "D";

// Local fisher-yates so we can shuffle the *order* the server returned to
// us, in case the backend ever returns the same insertion order between
// two sessions. The server-side selector already shuffles, so this is a
// belt-and-braces measure.
function shuffled<T>(arr: readonly T[]): T[] {
  const out = arr.slice();
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

export function TrainingPage() {
  const [session, setSession] = useState<SessionStartResponse | null>(null);
  const [scenarios, setScenarios] = useState<SessionStartResponse["scenarios"]>([]);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<Letter | null>(null);
  const [feedback, setFeedback] = useState<AnswerResponse | null>(null);
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [elapsedSec, setElapsedSec] = useState(0);
  const [explanationReady, setExplanationReady] = useState(false);
  const [sessionType, setSessionType] = useState<"quick" | "full">("full");
  const [config, setConfig] = useState<TrainingConfig>({ quick_size: 5, full_size: 20, explanation_duration_seconds: 12 });

  const startRef = useRef<number>(0);
  const tickRef = useRef<number | null>(null);

  // Fetch training config on mount
  useEffect(() => {
    trainingApi.config().then(setConfig).catch(() => {});
  }, []);

  const start = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSummary(null);
    setFeedback(null);
    setSelected(null);
    setIndex(0);
    try {
      const data = await trainingApi.startSession(sessionType === "quick" ? config.quick_size : config.full_size);
      setSession(data);
      setScenarios(shuffled(data.scenarios));
      startRef.current = performance.now();
    } catch (err) {
      setError(apiErrorMessage(err, "Could not start session"));
    } finally {
      setLoading(false);
    }
  }, [sessionType, config]);

  // Don't auto-start  the user clicks "Start training" below.

  // When feedback arrives: correct → immediate; incorrect → timer gates it.
  useEffect(() => {
    if (!feedback) return;
    if (feedback.is_correct) {
      setExplanationReady(true);
    } else {
      setExplanationReady(false);
    }
  }, [feedback]);

  // Per-question timer  reset whenever the active question changes.
  useEffect(() => {
    if (feedback || summary || !session) return;
    setElapsedSec(0);
    startRef.current = performance.now();
    tickRef.current = window.setInterval(() => {
      setElapsedSec(Math.floor((performance.now() - startRef.current) / 1000));
    }, 250);
    return () => {
      if (tickRef.current !== null) {
        window.clearInterval(tickRef.current);
        tickRef.current = null;
      }
    };
  }, [index, feedback, summary, session]);

  const scenario = scenarios[index];
  const total = scenarios.length || 0;
  const progressPct = total ? ((index + (feedback ? 1 : 0)) / total) * 100 : 0;

  const submit = useCallback(async () => {
    if (!selected || !session || !scenario) return;
    setSubmitting(true);
    try {
      const elapsed = Math.max(0, Math.round(performance.now() - startRef.current));
      const data = await trainingApi.submitAnswer(session.session_id, {
        scenario_id: scenario.id,
        answer: selected,
        response_time_ms: Math.min(elapsed, 300_000),
        presentation_token: scenario.presentation_token,
      });
      setFeedback(data);
    } catch (err) {
      setError(apiErrorMessage(err, "Submit failed"));
    } finally {
      setSubmitting(false);
    }
  }, [selected, session, scenario]);

  const advance = useCallback(async () => {
    setFeedback(null);
    setSelected(null);
    setExplanationReady(false);
    if (!session) return;
    if (index + 1 < total) {
      setIndex((i) => i + 1);
      return;
    }
    try {
      const summ = await trainingApi.sessionSummary(session.session_id);
      setSummary(summ);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load summary"));
    }
  }, [session, index, total]);

  // Keyboard shortcuts: 1-4 / A-D to pick, Enter to submit / advance.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (summary || loading) return;
      const key = e.key.toUpperCase();
      if (!feedback && ["A", "B", "C", "D", "1", "2", "3", "4"].includes(key)) {
        const map: Record<string, Letter> = {
          A: "A", B: "B", C: "C", D: "D",
          "1": "A", "2": "B", "3": "C", "4": "D",
        };
        setSelected(map[key]);
      } else if (e.key === "Enter") {
        if (feedback && explanationReady) void advance();
        else if (selected) void submit();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [feedback, selected, summary, loading, submit, advance, explanationReady]);

  const correctSoFar = useMemo(() => {
    // Conservative: backend tracks truth  this is just the in-page tally.
    if (!feedback) return null;
    return feedback.is_correct;
  }, [feedback]);

  if (loading) return <LoadingScreen />;

  if (error && !scenarios.length) {
    return (
      <Card>
        <CardBody>
          <p className="text-sm text-risk-critical">{error}</p>
          <Button className="mt-3" onClick={start}>
            <RotateCcw className="h-3.5 w-3.5" />
            Try again
          </Button>
        </CardBody>
      </Card>
    );
  }

  // Pre-session landing  explicit Start so the user knows when the timer
  // begins. Previously the page auto-started, which surprised users and
  // also began timing before they had read the question.
  if (!session) {
    return (
      <div className="mx-auto max-w-xl">
        <Card>
          <CardBody className="flex flex-col items-center gap-4 py-10 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/15 text-accent">
              <Play className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-text-primary">
                Ready to train?
              </h2>
              <p className="mt-2 text-sm text-text-secondary">
                A short adaptive session of multiple-choice scenarios. Pick
                the safest action for each. Your responses feed the risk
                model and the timer starts only when you press Start.
              </p>
            </div>

            {/* Session type selector */}
            <div data-tour="session-selector" className="flex w-full max-w-sm gap-3">
              <button
                onClick={() => setSessionType("quick")}
                className={`flex-1 rounded-lg border px-4 py-3 text-left transition-all ${
                  sessionType === "quick"
                    ? "border-accent bg-accent/10 ring-2 ring-accent/40"
                    : "border-border-subtle bg-bg-surface hover:border-border-strong"
                }`}
              >
                <div className="text-sm font-semibold text-text-primary">Quick</div>
                <div className="mt-0.5 text-xs text-text-muted">{config.quick_size} questions</div>
              </button>
              <button
                onClick={() => setSessionType("full")}
                className={`flex-1 rounded-lg border px-4 py-3 text-left transition-all ${
                  sessionType === "full"
                    ? "border-accent bg-accent/10 ring-2 ring-accent/40"
                    : "border-border-subtle bg-bg-surface hover:border-border-strong"
                }`}
              >
                <div className="text-sm font-semibold text-text-primary">Full</div>
                <div className="mt-0.5 text-xs text-text-muted">{config.full_size} questions</div>
              </button>
            </div>

            <Button size="lg" onClick={start}>
              <Play className="h-3.5 w-3.5" />
              Start training
            </Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (summary) {
    const accuracyPct = (summary.accuracy ?? 0) * 100;
    return (
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <Card>
          <CardBody className="flex flex-col items-center gap-4 py-10 text-center">
            <Trophy className="h-8 w-8 text-warning" />
            <ProgressRing percentage={accuracyPct} />
            <div>
              <h2 className="text-xl font-semibold text-text-primary">Session complete</h2>
              <p className="mt-1 text-sm text-text-secondary">
                {summary.correct}/{summary.total_questions} correct ·{" "}
                {(summary.duration_seconds ?? 0).toFixed(0)}s ·{" "}
                {summary.categories_covered?.length ?? 0} categor
                {(summary.categories_covered?.length ?? 0) === 1 ? "y" : "ies"} covered
              </p>
            </div>
            <div className="flex gap-3">
              <Button onClick={start}>
                <RotateCcw className="h-3.5 w-3.5" />
                Start another
              </Button>
              <Link to="/app/dashboard">
                <Button variant="ghost">Back to dashboard</Button>
              </Link>
            </div>
          </CardBody>
        </Card>

        {summary.weakest_category_this_session && (
          <Card>
            <CardBody className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 h-4 w-4 text-warning" />
              <div className="text-sm">
                <p className="font-medium text-text-primary">Focus area</p>
                <p className="mt-1 text-text-secondary">
                  Your weakest category in this session was{" "}
                  <strong className="text-text-primary">
                    {summary.weakest_category_this_session.replace(/_/g, " ")}
                  </strong>
                  . The next session will weight more questions there.
                </p>
              </div>
            </CardBody>
          </Card>
        )}

        {summary.improvement_tips && summary.improvement_tips.length > 0 && (
          <Card>
            <CardBody>
              <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
                <Lightbulb className="h-4 w-4 text-warning" />
                Improvement tips
              </div>
              <ul className="list-disc space-y-1.5 pl-5 text-sm text-text-secondary">
                {summary.improvement_tips.map((t, i) => <li key={i}>{t}</li>)}
              </ul>
            </CardBody>
          </Card>
        )}
      </div>
    );
  }

  if (!scenario) {
    return (
      <Card>
        <CardBody>
          <p className="text-sm">No active scenarios available right now.</p>
          <Button className="mt-3" onClick={start}>Refresh</Button>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      {/* Progress rail */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-text-muted">
          <div className="flex items-center gap-3">
            <span className="font-medium text-text-secondary">
              Question {index + 1} of {total}
            </span>
            <span className="hidden sm:inline">·</span>
            <CategoryBadge category={scenario.category} size="sm" />
            <span className="hidden sm:inline">·</span>
            <span className="hidden sm:inline">
              Difficulty {scenario.difficulty}
            </span>
          </div>
          <div className="flex items-center gap-1.5 tabular-nums">
            <Timer className="h-3.5 w-3.5" />
            {elapsedSec}s
          </div>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-bg-elevated">
          <motion.div
            className="h-full rounded-full bg-accent"
            initial={false}
            animate={{ width: `${progressPct}%` }}
            transition={{ type: "spring", stiffness: 120, damping: 20 }}
          />
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={scenario.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.18 }}
        >
          <Card>
            <CardBody className="space-y-4">
              {scenario.selection_reason && (
                <div className="flex items-start gap-2 rounded-md border border-accent/20 bg-accent/5 px-3 py-2 text-xs text-accent">
                  <Info className="mt-0.5 h-3.5 w-3.5 flex-shrink-0" />
                  <span>{scenario.selection_reason}</span>
                </div>
              )}
              <div>
                <h2 className="text-lg font-semibold text-text-primary">
                  {scenario.title}
                </h2>
                <p className="mt-2 whitespace-pre-line break-words text-sm text-text-secondary [overflow-wrap:anywhere]">
                  {scenario.content}
                </p>
              </div>
              {scenario.visual_html && (
                <VisualScenario
                  html={scenario.visual_html}
                  visualType={scenario.visual_type}
                />
              )}
              <AnswerOptions
                options={scenario.options}
                questionType={scenario.question_type}
                selected={selected}
                correct={feedback ? (feedback.correct_answer as Letter) : null}
                disabled={submitting}
                onSelect={(l) => !feedback && setSelected(l)}
              />
            </CardBody>
          </Card>
        </motion.div>
      </AnimatePresence>

      <AnimatePresence>
        {feedback && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.18 }}
          >
            <Card
              className={cn(
                "border",
                correctSoFar
                  ? "border-success/40 bg-success/5"
                  : "border-risk-critical/40 bg-risk-critical/5",
              )}
            >
              <CardBody className="space-y-3">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  {correctSoFar ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 text-success" />
                      <span className="text-success">Correct</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-4 w-4 text-risk-critical" />
                      <span className="text-risk-critical">Incorrect</span>
                    </>
                  )}
                  <span className="ml-auto text-2xs font-normal text-text-muted">
                    Mastery in {feedback.mastery_update.category.replace(/_/g, " ")}:{" "}
                    {(feedback.mastery_update.mastery * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-sm text-text-secondary">{feedback.explanation}</p>
                {feedback.red_flags && (
                  <p className="text-xs text-text-muted">
                    <strong className="text-text-secondary">Red flags:</strong>{" "}
                    {feedback.red_flags}
                  </p>
                )}
                {feedback.learning_tip && (
                  <div className="flex items-start gap-2 rounded-md border border-border-subtle bg-bg-elevated/40 p-2 text-xs text-text-muted">
                    <Lightbulb className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-warning" />
                    <span>{feedback.learning_tip}</span>
                  </div>
                )}
                {!correctSoFar && !explanationReady && (
                  <div className="flex justify-center pt-2">
                    <ExplanationTimer
                      duration={config.explanation_duration_seconds}
                      onComplete={() => setExplanationReady(true)}
                    />
                  </div>
                )}
              </CardBody>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center justify-between">
        <span className="text-2xs text-text-muted">
          Tip: press <kbd className="rounded bg-bg-elevated px-1">A–D</kbd> to pick,{" "}
          <kbd className="rounded bg-bg-elevated px-1">Enter</kbd> to{" "}
          {feedback ? "continue" : "submit"}.
        </span>
        {feedback ? (
          <Button onClick={advance} disabled={!explanationReady}>
            {index + 1 < total ? (
              <>
                Next <ArrowRight className="h-3.5 w-3.5" />
              </>
            ) : (
              <>
                Finish <Trophy className="h-3.5 w-3.5" />
              </>
            )}
          </Button>
        ) : (
          <Button
            onClick={submit}
            disabled={!selected || submitting}
            loading={submitting}
          >
            Submit answer
          </Button>
        )}
      </div>

      {error && (
        <Card className="border-risk-critical/40">
          <CardBody>
            <p className="text-xs text-risk-critical">{error}</p>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
