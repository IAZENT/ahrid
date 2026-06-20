import { AtSign, Lock, Shield } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { useAuth } from "../../hooks/useAuth";
import { useAuthStore } from "../../store/authStore";
import { defaultLandingForRole } from "../../lib/routing";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, loading, error, isAuthenticated } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");

  function computeRedirect(): string {
    return defaultLandingForRole(useAuthStore.getState().user?.role);
  }

  useEffect(() => {
    if (isAuthenticated) navigate(computeRedirect(), { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const ok = await login(identifier.trim().toLowerCase(), password);
    if (ok) navigate(computeRedirect(), { replace: true });
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-3 text-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/15 text-accent">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Welcome back</h1>
            <p className="mt-1 text-sm text-text-secondary">
              Sign in to continue your security training.
            </p>
          </div>
        </div>

        <Card>
          <CardBody>
            <form onSubmit={onSubmit} className="flex flex-col gap-4">
              <Input
                label="Email or username"
                name="identifier"
                type="text"
                autoComplete="username"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                leftIcon={<AtSign className="h-4 w-4" />}
                placeholder="you@company.com  or  yourname"
              />
              <Input
                label="Password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="h-4 w-4" />}
                placeholder="••••••••••••"
              />
              {error && (
                <div className="rounded-md border border-risk-critical/30 bg-risk-critical/10 px-3 py-2 text-xs text-risk-critical">
                  {error}
                </div>
              )}
              <Button type="submit" loading={loading} className="w-full" size="lg">
                Sign in
              </Button>
              <Link
                to="/forgot-password"
                className="text-center text-xs text-text-secondary hover:text-text-primary"
              >
                Forgot your password?
              </Link>
            </form>
          </CardBody>
        </Card>

        <p className="mt-6 text-center text-xs text-text-secondary">
          New to AHRIP?{" "}
          <Link to="/register" className="text-accent hover:underline">
            Create an employee account
          </Link>
        </p>
      </div>
    </div>
  );
}
