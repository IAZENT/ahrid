import { cn } from "../../lib/utils";

export function LoadingSpinner({
  size = 20, className,
}: { size?: number; className?: string }) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={cn(
        "inline-block animate-spin rounded-full border-2 border-border-default border-t-accent",
        className,
      )}
      style={{ width: size, height: size }}
    />
  );
}

export function LoadingScreen({ label }: { label?: string }) {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-3 py-16 text-text-secondary">
      <LoadingSpinner size={28} />
      {label && <p className="text-sm">{label}</p>}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "bg-shimmer animate-shimmer rounded-md",
        className,
      )}
    />
  );
}
