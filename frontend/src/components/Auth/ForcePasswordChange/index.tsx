import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import './styles.scss';

const ForcePasswordChange = () => {
  const navigate = useNavigate();
  const { completePasswordChange, profile } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    try {
      await completePasswordChange(currentPassword, newPassword);
      setCurrentPassword('');
      setNewPassword('');
      setSuccess('Contraseña actualizada correctamente.');

      if (profile?.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch {
      setError('No se pudo actualizar la contraseña.');
    }
  };

  return (
    <section className="force-password">
      <h2>Cambio obligatorio de contraseña</h2>
      <p>Por seguridad, tenés que actualizar tu contraseña antes de continuar.</p>

      <form onSubmit={handleSubmit} className="force-password__form">
        <label htmlFor="current-password">Contraseña actual</label>
        <input
          id="current-password"
          type="password"
          value={currentPassword}
          onChange={(event) => setCurrentPassword(event.target.value)}
          required
        />

        <label htmlFor="new-password">Nueva contraseña</label>
        <input
          id="new-password"
          type="password"
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
          minLength={8}
          required
        />

        <button type="submit">Actualizar contraseña</button>
      </form>

      {error && <p className="force-password__feedback force-password__feedback--error">{error}</p>}
      {success && (
        <p className="force-password__feedback force-password__feedback--success">{success}</p>
      )}
    </section>
  );
};

export default ForcePasswordChange;
