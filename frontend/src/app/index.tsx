import { type ReactNode } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import UserManagement from '../components/Admin/UserManagement';
import ForcePasswordChange from '../components/Auth/ForcePasswordChange';
import LoginForm from '../components/Auth/LoginForm';
import RegisterForm from '../components/Auth/RegisterForm';
import AppHeader from '../components/Layout/AppHeader';
import StarterSelection from '../components/Trainer/StarterSelection';
import { useAuth } from '../context/AuthContext';
import TrainerHome from './TrainerHome';
import './styles.scss';

const RequireAuth = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  const { isAuthenticated, profile } = useAuth();

  const redirectByProfile = () => {
    if (!profile) {
      return '/login';
    }
    if (profile.force_password_change) {
      return '/force-password-change';
    }
    if (profile.role === 'admin') {
      return '/admin';
    }
    if (!profile.starter_pokemon_selected) {
      return '/starter';
    }
    return '/';
  };

  return (
    <div className="app-shell">
      <div className="app-shell__noise" aria-hidden="true" />
      <main className="app-shell__main">
        <AppHeader />

        <Routes>
          <Route
            path="/login"
            element={isAuthenticated ? <Navigate to={redirectByProfile()} replace /> : <LoginForm />}
          />
          <Route
            path="/register"
            element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterForm />}
          />
          <Route
            path="/force-password-change"
            element={
              <RequireAuth>
                {profile?.force_password_change ? (
                  <ForcePasswordChange />
                ) : (
                  <Navigate to={redirectByProfile()} replace />
                )}
              </RequireAuth>
            }
          />
          <Route
            path="/starter"
            element={
              <RequireAuth>
                {profile?.role === 'trainer' && !profile.starter_pokemon_selected ? (
                  <StarterSelection />
                ) : (
                  <Navigate to={redirectByProfile()} replace />
                )}
              </RequireAuth>
            }
          />
          <Route
            path="/admin"
            element={
              <RequireAuth>
                {profile?.role === 'admin' ? (
                  <UserManagement />
                ) : (
                  <Navigate to={redirectByProfile()} replace />
                )}
              </RequireAuth>
            }
          />
          <Route
            path="/"
            element={
              <RequireAuth>
                {profile?.role === 'trainer' && profile.starter_pokemon_selected ? (
                  <TrainerHome />
                ) : (
                  <Navigate to={redirectByProfile()} replace />
                )}
              </RequireAuth>
            }
          />
          <Route
            path="*"
            element={<Navigate to={isAuthenticated ? redirectByProfile() : '/login'} replace />}
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
