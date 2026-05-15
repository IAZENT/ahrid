import { AtSign, Shield } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { authApi } from "../../api/auth";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";

export function ForgotPasswordPage() {
  const [identifier, setIdentifier] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    try {
      await authApi.forgotPassword(identifier.trim().toLowerCase());
    } catch { /* anti-enumeration: always succeed */ }
    finally {
      setSubmitted(true);
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
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Forgot password?</h1>
          <p className="text-sm text-text-secondary">
            We'll queue a reset request for your administrator to action.
          </p>
        </div>
        <Card>
          <CardBody>
            {submitted ? (
              <div className="text-sm text-text-secondary">
                If that account exists, your administrator will issue a reset
                token. Once you have the token, return here to set a new password.
              </div>
            ) : (
              <form onSubmit={onSubmit} className="flex flex-col gap-4">
                <Input
                  label="Email or username"
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  leftIcon={<AtSign className="h-4 w-4" />}
                />
                <Button type="submit" loading={loading} className="w-full" size="lg">
                  Queue reset request
                </Button>
              </form>
            )}
            <Link
              to="/login"
              className="mt-4 block text-center text-xs text-text-secondary hover:text-text-primary"
            >
              Back to sign in
            </Link>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
