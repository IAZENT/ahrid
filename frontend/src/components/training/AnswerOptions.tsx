import { Check, X, HelpCircle } from "lucide-react";
import { cn } from "../../lib/utils";
import type { QuestionType } from "../../types/api";

type Letter = "A" | "B" | "C" | "D";

interface AnswerOptionsProps {
  options: Record<Letter, string>;
  questionType: QuestionType;
  selected?: Letter | null;
  correct?: Letter | null; // revealed after answer
  disabled?: boolean;
  onSelect: (letter: Letter) => void;
}

const LETTERS: Letter[] = ["A", "B", "C", "D"];

export function AnswerOptions({
  options,
  questionType,
  selected,
  correct,
  disabled,
  onSelect,
}: AnswerOptionsProps) {
  if (questionType === "true_false") {
    return (
      <TrueFalseOptions
        options={options}
        selected={selected}
        correct={correct}
        disabled={disabled}
        onSelect={onSelect}
      />
    );
  }

  if (questionType === "identify_threat") {
    return (
      <IdentifyThreatOptions
        options={options}
        selected={selected}
        correct={correct}
        disabled={disabled}
        onSelect={onSelect}
      />
    );
  }

  return (
    <MCQOptions
      options={options}
      selected={selected}
      correct={correct}
      disabled={disabled}
      onSelect={onSelect}
    />
  );
}

/* ------------------------------------------------------------------ */
/* MCQ (default)                                                      */
/* ------------------------------------------------------------------ */
function MCQOptions({
  options,
  selected,
  correct,
  disabled,
  onSelect,
}: Omit<AnswerOptionsProps, "questionType">) {
  const revealed = Boolean(correct);

  return (
    <div className="flex flex-col gap-2.5">
      {LETTERS.map((letter) => {
        const isSelected = selected === letter;
        const isCorrect = correct === letter;
        const isWrongSelected = revealed && isSelected && !isCorrect;
        const empty = !options[letter]?.trim();
        if (empty && !isCorrect && !isSelected) return null;

        return (
          <button
            key={letter}
            type="button"
            disabled={disabled || revealed || empty}
            onClick={() => onSelect(letter)}
            className={cn(
              "flex w-full items-start gap-3 rounded-lg border px-4 py-3 text-left text-text-primary transition-all duration-200",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60",
              !revealed && !empty && !isSelected &&
                "bg-bg-surface border-border-subtle hover:border-border-strong hover:bg-bg-elevated",
              !revealed && isSelected &&
                "bg-accent/10 border-accent text-text-primary ring-2 ring-accent/40",
              revealed && isCorrect &&
                "bg-success/10 border-success text-success",
              isWrongSelected &&
                "bg-risk-critical/10 border-risk-critical text-risk-critical",
              revealed && !isCorrect && !isSelected &&
                "opacity-50 border-border-subtle bg-bg-surface",
              disabled && !revealed && "cursor-wait",
              empty && "opacity-40 cursor-not-allowed",
            )}
          >
            <span
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-md border text-xs font-semibold",
                !revealed && !empty && !isSelected && "border-border text-text-secondary",
                !revealed && isSelected && "border-accent bg-accent text-bg-base",
                revealed && isCorrect &&
                  "border-success bg-success text-bg-base",
                isWrongSelected &&
                  "border-risk-critical bg-risk-critical text-white",
                revealed && !isCorrect && !isSelected && "border-border-subtle text-text-muted",
              )}
            >
              {revealed && isCorrect ? (
                <Check className="h-3.5 w-3.5" />
              ) : isWrongSelected ? (
                <X className="h-3.5 w-3.5" />
              ) : (
                letter
              )}
            </span>
            <span className="flex-1 text-sm leading-relaxed">
              {options[letter]}
            </span>
          </button>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* True / False  big binary buttons                                  */
/* ------------------------------------------------------------------ */
function TrueFalseOptions({
  options,
  selected,
  correct,
  disabled,
  onSelect,
}: Omit<AnswerOptionsProps, "questionType">) {
  const revealed = Boolean(correct);

  const rows: { letter: Letter; label: string; accent: string }[] = [
    {
      letter: "A",
      label: options.A || "True",
      accent: "emerald",
    },
    {
      letter: "B",
      label: options.B || "False",
      accent: "rose",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {rows.map(({ letter, label, accent }) => {
        const isSelected = selected === letter;
        const isCorrect = correct === letter;
        const isWrongSelected = revealed && isSelected && !isCorrect;
        const isGood = accent === "emerald";

        return (
          <button
            key={letter}
            type="button"
            disabled={disabled || revealed}
            onClick={() => onSelect(letter)}
            className={cn(
              "relative flex flex-col items-center justify-center gap-2 rounded-xl border px-4 py-6 text-center transition-all duration-200",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60",
              !revealed && !isSelected &&
                (isGood
                  ? "border-emerald-500/30 bg-emerald-500/5 hover:bg-emerald-500/10 hover:border-emerald-500/50 text-emerald-400"
                  : "border-rose-500/30 bg-rose-500/5 hover:bg-rose-500/10 hover:border-rose-500/50 text-rose-400"),
              !revealed && isSelected &&
                (isGood
                  ? "border-emerald-500 bg-emerald-500/15 text-emerald-300 ring-2 ring-emerald-500/40"
                  : "border-rose-500 bg-rose-500/15 text-rose-300 ring-2 ring-rose-500/40"),
              revealed && isCorrect &&
                "bg-success/10 border-success text-success",
              isWrongSelected &&
                "bg-risk-critical/10 border-risk-critical text-risk-critical",
              disabled && !revealed && "cursor-wait opacity-70",
            )}
          >
            <span className="text-2xl font-bold">{label}</span>
            {revealed && isCorrect && (
              <Check className="h-5 w-5 text-success" />
            )}
            {isWrongSelected && (
              <X className="h-5 w-5 text-risk-critical" />
            )}
          </button>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Identify Threat  category-badge tiles                             */
/* ------------------------------------------------------------------ */
function IdentifyThreatOptions({
  options,
  selected,
  correct,
  disabled,
  onSelect,
}: Omit<AnswerOptionsProps, "questionType">) {
  const revealed = Boolean(correct);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {LETTERS.map((letter) => {
        const isSelected = selected === letter;
        const isCorrect = correct === letter;
        const isWrongSelected = revealed && isSelected && !isCorrect;
        const empty = !options[letter]?.trim();
        if (empty) return null;

        return (
          <button
            key={letter}
            type="button"
            disabled={disabled || revealed || empty}
            onClick={() => onSelect(letter)}
            className={cn(
              "relative flex items-center gap-3 rounded-lg border px-4 py-3 text-left transition-all duration-200",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60",
              !revealed && !empty && !isSelected &&
                "bg-bg-surface border-border-subtle hover:border-border-strong hover:bg-bg-elevated",
              !revealed && isSelected &&
                "bg-accent/10 border-accent text-text-primary ring-2 ring-accent/40",
              revealed && isCorrect &&
                "bg-success/10 border-success text-success",
              isWrongSelected &&
                "bg-risk-critical/10 border-risk-critical text-risk-critical",
              revealed && !isCorrect && !isSelected &&
                "opacity-50 border-border-subtle bg-bg-surface",
              disabled && !revealed && "cursor-wait",
            )}
          >
            <span
              className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-xs font-bold",
                !revealed && !empty && !isSelected && "border-border text-text-secondary",
                !revealed && isSelected && "border-accent bg-accent text-bg-base",
                revealed && isCorrect &&
                  "border-success bg-success text-bg-base",
                isWrongSelected &&
                  "border-risk-critical bg-risk-critical text-white",
                revealed && !isCorrect && !isSelected && "border-border-subtle text-text-muted",
              )}
            >
              {revealed && isCorrect ? (
                <Check className="h-3.5 w-3.5" />
              ) : isWrongSelected ? (
                <X className="h-3.5 w-3.5" />
              ) : (
                <HelpCircle className="h-3.5 w-3.5" />
              )}
            </span>
            <span className="flex-1 text-sm font-medium leading-relaxed">
              {options[letter]}
            </span>
          </button>
        );
      })}
    </div>
  );
}
