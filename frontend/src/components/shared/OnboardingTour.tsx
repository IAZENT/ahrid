import { useCallback, useEffect, useRef, useState } from "react";
import {
  Target,
  BarChart3,
  LayoutDashboard,
  TrendingUp,
  ChevronRight,
  X,
  Sparkles,
  type LucideIcon,
} from "lucide-react";
import { authApi } from "../../api/auth";
import { useAuthStore } from "../../store/authStore";

interface TourStep {
  icon: LucideIcon;
  title: string;
  description: string;
  hint: string;
  target: string | null;
  placement?: "right" | "bottom";
}

const TOUR_STEPS: TourStep[] = [
  {
    icon: Sparkles,
    title: "Welcome to AHRIP",
    description:
      "Your personalised cybersecurity awareness platform. Let's take a quick tour of the key areas  it only takes a minute.",
    hint: "Let's walk through the key areas",
    target: null,
  },
  {
    icon: LayoutDashboard,
    title: "Your Dashboard",
    description:
      "This is your home base. See your current risk score, sessions completed, and weekly trends at a glance.",
    hint: "Always your first stop after login",
    target: "risk-score",
    placement: "bottom",
  },
  {
    icon: Target,
    title: "Start Training",
    description:
      "Pick a Quick (5 questions) or Full (20 questions) session. Each scenario adapts to your weakest areas.",
    hint: "Click Training in the sidebar to begin",
    target: "tour-nav-training",
    placement: "right",
  },
  {
    icon: TrendingUp,
    title: "Track Your Progress",
    description:
      "View your risk score breakdown, 8-week trends, and SHAP-powered explanations of what drives your score.",
    hint: "My Score shows your full risk profile",
    target: "tour-nav-my-score",
    placement: "right",
  },
  {
    icon: BarChart3,
    title: "You're All Set",
    description:
      "Complete a training session and your risk score will update automatically. The more you train, the more accurate it gets.",
    hint: "Start your first session now",
    target: "risk-score",
    placement: "bottom",
  },
];

const SPOTLIGHT_GAP = 10;

export function OnboardingTour() {
  const [step, setStep] = useState(0);
  const [rect, setRect] = useState<DOMRect | null>(null);
  const [closing, setClosing] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [tooltipReady, setTooltipReady] = useState(false);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<number | null>(null);
  const updateUser = useAuthStore((s) => s.updateUser);
  const current = TOUR_STEPS[step];
  const Icon = current.icon;
  const isLast = step === TOUR_STEPS.length - 1;

  const findTarget = useCallback(() => {
    if (!current.target) return null;
    return document.querySelector(`[data-tour="${current.target}"]`);
  }, [current.target]);

  const measureTarget = useCallback(() => {
    const el = findTarget();
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "nearest" });
      window.setTimeout(() => {
        setRect(el.getBoundingClientRect());
        setTooltipReady(true);
      }, 200);
    } else {
      setRect(null);
      setTooltipReady(true);
    }
  }, [findTarget]);

  useEffect(() => {
    setTooltipReady(false);
    if (timerRef.current !== null) clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(measureTarget, 80);
    return () => {
      if (timerRef.current !== null) clearTimeout(timerRef.current);
    };
  }, [step, measureTarget]);

  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  useEffect(() => {
    function onResize() {
      const el = findTarget();
      if (el) setRect(el.getBoundingClientRect());
    }
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [findTarget]);

  const complete = async () => {
    setClosing(true);
    try {
      await authApi.completeTour();
      updateUser({ tour_completed: true });
    } catch {
      updateUser({ tour_completed: true });
    }
  };

  const next = () => {
    if (isLast) {
      void complete();
    } else {
      setRect(null);
      setTooltipReady(false);
      setStep((s) => s + 1);
    }
  };

  const prev = () => {
    if (step > 0) {
      setRect(null);
      setTooltipReady(false);
      setStep((s) => s - 1);
    }
  };

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (closing) return;
      if (e.key === "ArrowRight" || e.key === "Enter") {
        e.preventDefault();
        next();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        prev();
      } else if (e.key === "Escape") {
        void complete();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const spotlightStyle = rect
    ? {
        top: rect.top - SPOTLIGHT_GAP,
        left: rect.left - SPOTLIGHT_GAP,
        width: rect.width + SPOTLIGHT_GAP * 2,
        height: rect.height + SPOTLIGHT_GAP * 2,
      }
    : null;

  const placement = current.placement ?? "bottom";

  let tooltipTop: number;
  let tooltipLeft: number;

  if (rect) {
    if (placement === "right") {
      tooltipTop = rect.top;
      tooltipLeft = rect.right + SPOTLIGHT_GAP + 16;
      if (tooltipLeft + 420 > window.innerWidth) {
        tooltipLeft = rect.left - SPOTLIGHT_GAP - 436;
      }
    } else {
      tooltipTop = rect.bottom + SPOTLIGHT_GAP + 16;
      tooltipLeft = rect.left;
      if (tooltipTop + 260 > window.innerHeight) {
        tooltipTop = rect.top - SPOTLIGHT_GAP - 276;
      }
    }
    if (tooltipLeft + 420 > window.innerWidth) tooltipLeft = window.innerWidth - 436;
    if (tooltipLeft < 16) tooltipLeft = 16;
    if (tooltipTop < 16) tooltipTop = 16;
  } else {
    tooltipTop = window.innerHeight / 2 - 150;
    tooltipLeft = window.innerWidth / 2 - 200;
  }

  return (
    <div
      className={`fixed inset-0 z-50 transition-opacity duration-300 ${
        closing
          ? "pointer-events-none opacity-0"
          : mounted
            ? "opacity-100"
            : "opacity-0"
      }`}
      style={{ background: "rgba(2, 6, 18, 0.30)" }}
    >
      {spotlightStyle && (
        <div
          className="absolute rounded-lg transition-all duration-300 ease-out"
          style={{
            ...spotlightStyle,
            boxShadow: "0 0 0 9999px rgba(2, 6, 18, 0.30)",
          }}
        >
          <div
            className="absolute inset-0 rounded-lg pointer-events-none"
            style={{
              boxShadow: "0 0 0 2px rgba(99, 179, 237, 0.5), 0 0 20px 4px rgba(99, 179, 237, 0.15)",
            }}
          />
        </div>
      )}

      <div
        ref={tooltipRef}
        className={`absolute z-10 w-[400px] transition-all duration-300 ease-out ${
          closing ? "opacity-0 scale-95" : tooltipReady ? "opacity-100 scale-100" : "opacity-0 scale-95"
        }`}
        style={{ top: tooltipTop, left: tooltipLeft }}
      >
        <div className="rounded-xl border border-white/10 bg-[#0d1320]/95 shadow-[0_8px_40px_rgba(0,0,0,0.5)] backdrop-blur-sm">
          <div className="flex items-center justify-between border-b border-white/5 px-4 py-2.5">
            <div className="flex items-center gap-1">
              {TOUR_STEPS.map((_, i) => (
                <div
                  key={i}
                  className={`rounded-full transition-all duration-300 ${
                    i === step
                      ? "h-1.5 w-5 bg-sky-400"
                      : i < step
                        ? "h-1.5 w-1.5 bg-sky-400/50"
                        : "h-1.5 w-1.5 bg-white/15"
                  }`}
                />
              ))}
            </div>
            <button
              onClick={() => void complete()}
              className="rounded p-1 text-white/30 hover:bg-white/5 hover:text-white/70 transition-colors"
              aria-label="Skip tour"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="px-5 py-5">
            <div className="mb-3 flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-400/10 text-sky-400">
                <Icon className="h-[18px] w-[18px]" />
              </div>
              <div>
                <div className="text-[10px] font-medium uppercase tracking-wider text-white/30">
                  {step + 1} of {TOUR_STEPS.length}
                </div>
                <h3 className="text-sm font-semibold text-white">{current.title}</h3>
              </div>
            </div>
            <p className="text-sm leading-relaxed text-white/60">
              {current.description}
            </p>
            <div className="mt-3 rounded-md border border-sky-400/15 bg-sky-400/5 px-2.5 py-1.5 text-[11px] text-sky-300/80">
              {current.hint}
            </div>
          </div>

          <div className="flex items-center justify-between border-t border-white/5 px-4 py-2.5">
            <div className="flex items-center gap-2">
              <button
                onClick={() => void complete()}
                className="text-[11px] font-medium text-white/30 hover:text-white/60 transition-colors"
              >
                Skip tour
              </button>
              {step > 0 && (
                <button
                  onClick={prev}
                  className="text-[11px] font-medium text-white/40 hover:text-white/70 transition-colors"
                >
                  Back
                </button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-white/20">
                ← → navigate
              </span>
              <button
                onClick={next}
                className="flex items-center gap-1 rounded-md bg-sky-500 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-sky-400 transition-colors"
              >
                {isLast ? "Get started" : "Next"}
                {!isLast && <ChevronRight className="h-3 w-3" />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
