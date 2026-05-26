import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../../../services/auth/authService';
import { useAuth } from '../../../context/AuthContext';
import './styles.scss';

const LoginForm = () => {
  const navigate = useNavigate();
  const { rememberedUsername, signIn } = useAuth();

  const [username, setUsername] = useState<string>(rememberedUsername);
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await login({ username, password });
      await signIn(response.access_token, username);
      setPassword('');
      if (response.force_password_change) {
        navigate('/force-password-change');
      } else if (response.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch {
      setError('No se pudo iniciar sesión. Revisá tus credenciales.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="auth-card">
      <h2>Ingresar</h2>
      <p>Entrá con tu cuenta para buscar Pokémon.</p>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="username">Usuario</label>
        <input
          id="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="ash_ketchum"
          required
        />

        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="********"
          required
        />

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Ingresando...' : 'Entrar'}
        </button>
      </form>

      {error && <p className="auth-feedback auth-feedback--error">{error}</p>}

      <p className="auth-card__link">
        ¿No tenés cuenta? <Link to="/register">Crear usuario</Link>
      </p>
    </section>
  );
};

export default LoginForm;
