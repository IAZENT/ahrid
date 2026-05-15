import { Key, Lock, Shield } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi } from "../../api/auth";
import { apiErrorMessage } from "../../api/client";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const [token, setToken] = useState("");
  const [pw, setPw] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await authApi.resetPassword(token.trim(), pw);
      navigate("/login", { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err, "Reset failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-3 text-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/15 text-accent">
            <Shield className="h-5 w-5" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Set a new password</h1>
        </div>
        <Card>
          <CardBody>
            <form onSubmit={onSubmit} className="flex flex-col gap-4">
              <Input
                label="Reset token"
                type="text"
                required
                value={token}
                onChange={(e) => setToken(e.target.value)}
                leftIcon={<Key className="h-4 w-4" />}
              />
              <Input
                label="New password"
                type="password"
                required
                value={pw}
                onChange={(e) => setPw(e.target.value)}
                leftIcon={<Lock className="h-4 w-4" />}
              />
              {error && (
                <div className="rounded-md border border-risk-critical/30 bg-risk-critical/10 px-3 py-2 text-xs text-risk-critical">
                  {error}
                </div>
              )}
              <Button type="submit" loading={loading} className="w-full" size="lg">
                Reset password
              </Button>
              <Link
                to="/login"
                className="text-center text-xs text-text-secondary hover:text-text-primary"
              >
                Back to sign in
              </Link>
            </form>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
