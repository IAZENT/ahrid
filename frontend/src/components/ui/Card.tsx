import { type HTMLAttributes, type ReactNode, forwardRef } from "react";
import { cn } from "../../lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ hoverable, className, ...rest }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border border-border-subtle bg-bg-surface shadow-elevated",
        hoverable && "transition-colors duration-150 hover:border-border hover:bg-bg-elevated",
        className,
      )}
      {...rest}
    />
  ),
);
Card.displayName = "Card";

export function CardHeader({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex items-center justify-between gap-4 border-b border-border-subtle px-5 py-4",
        className,
      )}
      {...rest}
    />
  );
}

export function CardTitle({
  children, className,
}: { children: ReactNode; className?: string }) {
  return (
    <h3 className={cn("text-md font-semibold text-text-primary", className)}>
      {children}
    </h3>
  );
}

export function CardDescription({
  children, className,
}: { children: ReactNode; className?: string }) {
  return (
    <p className={cn("text-xs text-text-secondary", className)}>{children}</p>
  );
}

export function CardBody({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-5", className)} {...rest} />;
}

export function CardFooter({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex items-center justify-end gap-2 border-t border-border-subtle px-5 py-3",
        className,
      )}
      {...rest}
    />
  );
}
