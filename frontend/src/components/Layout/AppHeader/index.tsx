import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import './styles.scss';

const AppHeader = () => {
  const navigate = useNavigate();
  const { isAuthenticated, signOut } = useAuth();

  const handleLogout = () => {
    signOut(true);
    navigate('/login');
  };

  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__ball" aria-hidden="true" />
        <div>
          <p className="app-header__subtitle">PokeTrainer</p>
          <h1 className="app-header__title">Pokédex Hub</h1>
        </div>
      </div>

      {isAuthenticated && (
        <button type="button" className="app-header__logout" onClick={handleLogout}>
          Salir
        </button>
      )}
    </header>
  );
};

export default AppHeader;
