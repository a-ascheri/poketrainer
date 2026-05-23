import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '@services/auth/authService';
import { setLastUsername } from '@services/auth/authStorage';
import './styles.scss';

const RegisterForm = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setIsSubmitting(true);

    try {
      await register({ username, email, password });
      setLastUsername(username);
      setSuccess('Usuario creado. Ya podés iniciar sesión.');
      setPassword('');
      setTimeout(() => navigate('/login'), 800);
    } catch {
      setError('No fue posible crear el usuario. Verificá los datos.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="auth-card">
      <h2>Crear cuenta</h2>
      <p>Te registramos como poketrainer para empezar.</p>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="register-username">Usuario</label>
        <input
          id="register-username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          required
        />

        <label htmlFor="register-email">Email</label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="register-password">Contraseña</label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          minLength={6}
        />

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Creando...' : 'Registrarme'}
        </button>
      </form>

      {error && <p className="auth-feedback auth-feedback--error">{error}</p>}
      {success && <p className="auth-feedback auth-feedback--success">{success}</p>}

      <p className="auth-card__link">
        ¿Ya tenés cuenta? <Link to="/login">Iniciar sesión</Link>
      </p>
    </section>
  );
};

export default RegisterForm;
