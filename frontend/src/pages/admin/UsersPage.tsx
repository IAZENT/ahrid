import { useEffect, useState, type FormEvent } from "react";
import { adminApi } from "../../api/admin";
import { apiErrorMessage } from "../../api/client";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { LoadingScreen } from "../../components/shared/LoadingSpinner";
import type { User } from "../../types/api";

export function AdminUsersPage() {
  const [users, setUsers] = useState<User[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    email: "", username: "", password: "", role: "employee", job_role: "it",
    first_name: "", last_name: "", department: "",
  });
  const [creating, setCreating] = useState(false);
  const [createMsg, setCreateMsg] = useState<string | null>(null);

  const refresh = () =>
    adminApi
      .listUsers()
      .then((d) => setUsers(d.users))
      .catch((e) => setError(apiErrorMessage(e)));

  useEffect(() => { void refresh(); }, []);

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setCreating(true);
    setCreateMsg(null);
    try {
      await adminApi.createUser(form);
      setForm({ ...form, email: "", username: "", password: "" });
      setCreateMsg("User created.");
      await refresh();
    } catch (err) {
      setCreateMsg(apiErrorMessage(err, "Could not create user"));
    } finally {
      setCreating(false);
    }
  };

  if (users === null && !error) return <LoadingScreen />;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-lg font-semibold">Users</h1>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Create user</h2>
          <form onSubmit={submit} className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
            <Input label="Email" type="email" required value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <Input label="Username" required value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })} />
            <Input label="Password" type="password" required value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <div>
              <label className="mb-1 block text-xs font-medium text-text-secondary">Role</label>
              <select
                className="h-9 w-full rounded-md border border-border-subtle bg-bg-surface px-2 text-sm"
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                <option value="employee">Employee</option>
                <option value="manager">Manager</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-text-secondary">Job role</label>
              <select
                className="h-9 w-full rounded-md border border-border-subtle bg-bg-surface px-2 text-sm"
                value={form.job_role}
                onChange={(e) => setForm({ ...form, job_role: e.target.value })}
              >
                {["receptionist", "accountant", "hr", "it", "finance", "sales", "management"].map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <Input label="First name" value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            <Input label="Last name" value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            <Input label="Department" value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })} />
            <div className="md:col-span-2 flex items-center gap-3">
              <Button type="submit" loading={creating}>Create</Button>
              {createMsg && <span className="text-xs text-text-secondary">{createMsg}</span>}
            </div>
          </form>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Existing users</h2>
          {error && <p className="mt-2 text-sm text-risk-critical">{error}</p>}
          <table className="mt-3 w-full text-sm">
            <thead className="text-xs uppercase tracking-wide text-text-muted">
              <tr className="text-left">
                <th className="pb-2">Email</th>
                <th className="pb-2">Username</th>
                <th className="pb-2">Role</th>
                <th className="pb-2">Job</th>
                <th className="pb-2">Active</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {(users ?? []).map((u) => (
                <tr key={u.id}>
                  <td className="py-2">{u.email}</td>
                  <td className="py-2">{u.username ?? "—"}</td>
                  <td className="py-2">{u.role}</td>
                  <td className="py-2">{u.job_role ?? "—"}</td>
                  <td className="py-2">{u.is_active ? "yes" : "no"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
