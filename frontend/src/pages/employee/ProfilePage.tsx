import { useState, type FormEvent } from "react";
import { authApi } from "../../api/auth";
import { apiErrorMessage } from "../../api/client";
import { Button } from "../../components/ui/Button";
import { Card, CardBody } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { useAuthStore } from "../../store/authStore";

export function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const [first, setFirst] = useState(user?.first_name ?? "");
  const [last, setLast] = useState(user?.last_name ?? "");
  const [username, setUsername] = useState(user?.username ?? "");
  const [department, setDepartment] = useState(user?.department ?? "");
  const [pwCurrent, setPwCurrent] = useState("");
  const [pwNew, setPwNew] = useState("");
  const [profileMsg, setProfileMsg] = useState<string | null>(null);
  const [pwMsg, setPwMsg] = useState<string | null>(null);

  const saveProfile = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setProfileMsg(null);
    try {
      const res = await authApi.updateProfile({
        first_name: first || null,
        last_name: last || null,
        username: username || null,
        department: department || null,
      });
      updateUser(res.user);
      setProfileMsg("Profile saved.");
    } catch (err) {
      setProfileMsg(apiErrorMessage(err, "Could not save profile"));
    }
  };

  const changePw = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setPwMsg(null);
    try {
      await authApi.changePassword(pwCurrent, pwNew);
      setPwCurrent("");
      setPwNew("");
      setPwMsg("Password updated.");
    } catch (err) {
      setPwMsg(apiErrorMessage(err, "Could not change password"));
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-lg font-semibold text-text-primary">Profile</h1>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Your details</h2>
          <form className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2" onSubmit={saveProfile}>
            <Input label="First name" value={first} onChange={(e) => setFirst(e.target.value)} />
            <Input label="Last name" value={last} onChange={(e) => setLast(e.target.value)} />
            <Input label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
            <Input label="Department" value={department} onChange={(e) => setDepartment(e.target.value)} />
            <div className="md:col-span-2 flex items-center gap-3">
              <Button type="submit">Save</Button>
              {profileMsg && <span className="text-xs text-text-secondary">{profileMsg}</span>}
            </div>
          </form>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <h2 className="text-md font-semibold">Change password</h2>
          <form className="mt-3 flex max-w-md flex-col gap-3" onSubmit={changePw}>
            <Input
              label="Current password"
              type="password"
              required
              value={pwCurrent}
              onChange={(e) => setPwCurrent(e.target.value)}
            />
            <Input
              label="New password"
              type="password"
              required
              value={pwNew}
              onChange={(e) => setPwNew(e.target.value)}
            />
            <div className="flex items-center gap-3">
              <Button type="submit">Update password</Button>
              {pwMsg && <span className="text-xs text-text-secondary">{pwMsg}</span>}
            </div>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}
