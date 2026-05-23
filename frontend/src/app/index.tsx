import { type ReactNode } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import LoginForm from '@components/Auth/LoginForm';
import RegisterForm from '@components/Auth/RegisterForm';
import AppHeader from '@components/Layout/AppHeader';
import PokemonSearch from '@components/Pokemon/PokemonSearch';
import { useAuth } from '@context/AuthContext';
import './styles.scss';

const RequireAuth = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="app-shell">
      <div className="app-shell__noise" aria-hidden="true" />
      <main className="app-shell__main">
        <AppHeader />

        <Routes>
          <Route
            path="/login"
            element={isAuthenticated ? <Navigate to="/" replace /> : <LoginForm />}
          />
          <Route
            path="/register"
            element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterForm />}
          />
          <Route
            path="/"
            element={
              <RequireAuth>
                <PokemonSearch />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to={isAuthenticated ? '/' : '/login'} replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
