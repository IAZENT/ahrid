import { AtSign, Briefcase, Lock, Shield, User as UserIcon } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi } from "../../api/auth";
import { apiErrorMessage } from "../../api/client";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { useAuthStore } from "../../store/authStore";
import { defaultLandingForRole } from "../../lib/routing";

const JOB_ROLES = [
  "receptionist", "accountant", "hr", "it",
  "finance", "sales", "management", "other",
];

export function RegisterPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((s) => s.setSession);

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [department, setDepartment] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const res = await authApi.register({
        email: email.trim().toLowerCase(),
        username: username.trim().toLowerCase(),
        password,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        job_role: jobRole || undefined,
        department: department.trim() || undefined,
      });
      setSession({
        accessToken: res.access_token,
        refreshToken: res.refresh_token,
        user: res.user,
      });
      navigate(defaultLandingForRole(res.user.role), { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err, "Unable to register"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        <div className="mb-8 flex flex-col items-center gap-3 text-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/15 text-accent">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-text-primary">
              Join AHRIP
            </h1>
            <p className="mt-1 text-sm text-text-secondary">
              Register as an employee in the AHRIP organisation.
            </p>
          </div>
        </div>

        <Card>
          <CardBody>
            <form onSubmit={onSubmit} className="flex flex-col gap-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="First name"
                  name="first_name"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  leftIcon={<UserIcon className="h-4 w-4" />}
                />
                <Input
                  label="Last name"
                  name="last_name"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  leftIcon={<UserIcon className="h-4 w-4" />}
                />
              </div>

              <Input
                label="Work email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<AtSign className="h-4 w-4" />}
                placeholder="you@ahrip.local"
              />

              <Input
                label="Username"
                name="username"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                leftIcon={<UserIcon className="h-4 w-4" />}
                hint="3-32 chars, letters/digits/._-"
              />

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-medium text-text-secondary">
                    Job role
                  </label>
                  <div className="relative">
                    <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-text-muted">
                      <Briefcase className="h-4 w-4" />
                    </span>
                    <select
                      value={jobRole}
                      onChange={(e) => setJobRole(e.target.value)}
                      className="w-full rounded-md border border-border-subtle bg-bg-surface px-3 py-2 pl-9 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent/60 focus:border-accent"
                    >
                      <option value="">Select…</option>
                      {JOB_ROLES.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <Input
                  label="Department (optional)"
                  name="department"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                />
              </div>

              <Input
                label="Password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="h-4 w-4" />}
                hint="Min 12 chars, with uppercase, lowercase, digit, and special character."
              />
              <Input
                label="Confirm password"
                name="confirm_password"
                type="password"
                autoComplete="new-password"
                required
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                leftIcon={<Lock className="h-4 w-4" />}
              />

              {error && (
                <div className="rounded-md border border-risk-critical/30 bg-risk-critical/10 px-3 py-2 text-xs text-risk-critical">
                  {error}
                </div>
              )}

              <Button type="submit" loading={loading} className="w-full" size="lg">
                Create account
              </Button>

              <Link
                to="/login"
                className="text-center text-xs text-text-secondary hover:text-text-primary"
              >
                Already have an account? Sign in
              </Link>
            </form>
          </CardBody>
        </Card>

        <p className="mt-6 text-center text-xs text-text-secondary">
          You will be registered as an employee in the AHRIP organisation.
        </p>
      </div>
    </div>
  );
}
