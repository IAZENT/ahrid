import { AnimatePresence, motion } from "framer-motion";
import { useState, type ReactNode } from "react";
import { ErrorBoundary } from "../shared/ErrorBoundary";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children: ReactNode;
  title: string;
}

export function AppShell({ children, title }: AppShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-bg-base">
      <div className="hidden md:block">
        <Sidebar />
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="fixed inset-0 z-40 md:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div
              className="absolute inset-0 bg-bg-base/70 backdrop-blur-sm"
              onClick={() => setMobileOpen(false)}
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ ease: [0.16, 1, 0.3, 1], duration: 0.25 }}
              className="absolute left-0 top-0 h-full"
            >
              <Sidebar onNavigate={() => setMobileOpen(false)} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar title={title} onToggleSidebar={() => setMobileOpen((v) => !v)} />
        <main className="flex-1 overflow-y-auto">
          <ErrorBoundary>
            <div className="mx-auto max-w-7xl px-4 py-6 md:px-6 md:py-8">
              {children}
            </div>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
