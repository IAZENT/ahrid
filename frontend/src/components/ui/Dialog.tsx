import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import {
  useCallback,
  useEffect,
  type KeyboardEvent,
  type MouseEvent,
  type ReactNode,
} from "react";
import { cn } from "../../lib/utils";

interface DialogProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children?: ReactNode;
  footer?: ReactNode;
  /** When true, clicking the backdrop will NOT close the dialog. */
  staticBackdrop?: boolean;
  widthClass?: string;
}

export function Dialog({
  open, onClose, title, description, children, footer,
  staticBackdrop, widthClass = "max-w-lg",
}: DialogProps) {
  const handleKey = useCallback(
    (e: KeyboardEvent<HTMLDivElement>) => {
      if (e.key === "Escape") onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (!open) return;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = original;
    };
  }, [open]);

  const stop = (e: MouseEvent) => e.stopPropagation();

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={staticBackdrop ? undefined : onClose}
          onKeyDown={handleKey}
        >
          <div className="absolute inset-0 bg-bg-base/80 backdrop-blur-sm" />
          <motion.div
            role="dialog"
            aria-modal="true"
            onClick={stop}
            className={cn(
              "relative z-10 w-full rounded-xl border border-border-subtle bg-bg-surface shadow-elevated",
              widthClass,
            )}
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 4 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            {(title || description) && (
              <div className="flex items-start justify-between gap-4 border-b border-border-subtle px-5 py-4">
                <div>
                  {title && <h2 className="text-lg font-semibold">{title}</h2>}
                  {description && (
                    <p className="mt-1 text-xs text-text-secondary">{description}</p>
                  )}
                </div>
                <button
                  onClick={onClose}
                  aria-label="Close dialog"
                  className="rounded-md p-1.5 text-text-muted hover:bg-bg-elevated hover:text-text-primary transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
            <div className="p-5">{children}</div>
            {footer && (
              <div className="flex items-center justify-end gap-2 border-t border-border-subtle px-5 py-3">
                {footer}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
