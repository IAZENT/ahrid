import type { UserRole } from "../types/api";

export function defaultLandingForRole(role: UserRole | undefined): string {
  switch (role) {
    case "admin":
      return "/app/admin";
    case "manager":
      return "/app/manager/dashboard";
    case "employee":
    default:
      return "/app/dashboard";
  }
}
