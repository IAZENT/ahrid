import { forwardRef, type InputHTMLAttributes, type ReactNode } from "react";
import { cn } from "../../lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string | null;
  leftIcon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, hint, error, leftIcon, className, id, ...rest }, ref) => {
    const inputId = id || (rest.name ? `input-${rest.name}` : undefined);
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-xs font-medium text-text-secondary">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-text-muted">
              {leftIcon}
            </span>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              "w-full rounded-md border bg-bg-surface px-3 py-2 text-sm text-text-primary",
              "placeholder:text-text-muted",
              "focus:outline-none focus:ring-2 focus:ring-accent/60 focus:border-accent",
              "transition-colors duration-150",
              leftIcon && "pl-9",
              error
                ? "border-risk-critical/60 focus:ring-risk-critical/40 focus:border-risk-critical"
                : "border-border-subtle hover:border-border",
              className,
            )}
            {...rest}
          />
        </div>
        {error ? (
          <p className="text-2xs text-risk-critical">{error}</p>
        ) : hint ? (
          <p className="text-2xs text-text-muted">{hint}</p>
        ) : null}
      </div>
    );
  },
);
Input.displayName = "Input";
