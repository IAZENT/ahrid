import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { RoleRedirect } from "./components/layout/RoleRedirect";
import { LoadingScreen } from "./components/shared/LoadingSpinner";
import { Toaster } from "./components/shared/Toaster";
import { useSessionBootstrap } from "./hooks/useSessionBootstrap";
import { ForgotPasswordPage } from "./pages/auth/ForgotPasswordPage";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { ResetPasswordPage } from "./pages/auth/ResetPasswordPage";
import { DashboardPage } from "./pages/employee/DashboardPage";
import { HistoryPage } from "./pages/employee/HistoryPage";
import { MyScorePage } from "./pages/employee/MyScorePage";
import { ProfilePage } from "./pages/employee/ProfilePage";
import { TrainingPage } from "./pages/employee/TrainingPage";
import { ManagerDashboardPage } from "./pages/manager/DashboardPage";
import { ManagerTeamPage } from "./pages/manager/TeamPage";
import { ManagerClustersPage } from "./pages/manager/ClustersPage";
import { ManagerReportsPage } from "./pages/manager/ReportsPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { AdminUsersPage } from "./pages/admin/UsersPage";
import { AdminScenariosPage } from "./pages/admin/ScenariosPage";
import { AdminThreatFeedPage } from "./pages/admin/ThreatFeedPage";
import { AdminPasswordResetsPage } from "./pages/admin/PasswordResetsPage";
import { EvaluationAdminPage } from "./pages/admin/EvaluationAdminPage";
import { EvaluationPage } from "./pages/employee/EvaluationPage";
import { TransparencyPage } from "./pages/TransparencyPage";

export default function App() {
  const sessionReady = useSessionBootstrap();
  if (!sessionReady) return <LoadingScreen />;
  return (
    <BrowserRouter>
      <Toaster />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<RoleRedirect fallback="/app/dashboard" />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="training" element={<TrainingPage />} />
          <Route path="my-score" element={<MyScorePage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="profile" element={<ProfilePage />} />

          <Route
            path="manager/dashboard"
            element={
              <ProtectedRoute roles={["manager", "admin"]}>
                <ManagerDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="manager/team"
            element={
              <ProtectedRoute roles={["manager", "admin"]}>
                <ManagerTeamPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="manager/clusters"
            element={
              <ProtectedRoute roles={["manager", "admin"]}>
                <ManagerClustersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="manager/reports"
            element={
              <ProtectedRoute roles={["manager", "admin"]}>
                <ManagerReportsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="admin"
            element={
              <ProtectedRoute roles={["admin"]}>
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin/users"
            element={
              <ProtectedRoute roles={["admin"]}>
                <AdminUsersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin/scenarios"
            element={
              <ProtectedRoute roles={["admin"]}>
                <AdminScenariosPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin/threats"
            element={
              <ProtectedRoute roles={["admin"]}>
                <AdminThreatFeedPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin/password-resets"
            element={
              <ProtectedRoute roles={["admin"]}>
                <AdminPasswordResetsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin/evaluation"
            element={
              <ProtectedRoute roles={["admin"]}>
                <EvaluationAdminPage />
              </ProtectedRoute>
            }
          />

          <Route path="evaluation" element={<EvaluationPage />} />
          <Route path="transparency" element={<TransparencyPage />} />
        </Route>

        <Route path="/" element={<RoleRedirect />} />
        <Route path="*" element={<RoleRedirect />} />
      </Routes>
    </BrowserRouter>
  );
}
