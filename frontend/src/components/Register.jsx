import React, { useState } from 'react';
import api from '../api/api';

export default function Register({ onRegister }) {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await api.post('/users/', form); // Ajusta el endpoint si es diferente
      setSuccess('Usuario creado correctamente. Ahora puedes iniciar sesión.');
      setForm({ username: '', email: '', password: '' });
      if (onRegister) onRegister();
    } catch (err) {
      setError('Error al crear usuario. ¿Ya existe ese email o usuario?');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 300, margin: '2rem auto' }}>
      <h2>Registro</h2>
      <input
        name="username"
        placeholder="Usuario"
        value={form.username}
        onChange={handleChange}
        required
        style={{ width: '100%', marginBottom: 8 }}
      />
      <input
        name="email"
        placeholder="Email"
        type="email"
        value={form.email}
        onChange={handleChange}
        required
        style={{ width: '100%', marginBottom: 8 }}
      />
      <input
        name="password"
        placeholder="Contraseña"
        type="password"
        value={form.password}
        onChange={handleChange}
        required
        style={{ width: '100%', marginBottom: 8 }}
      />
      <button type="submit" style={{ width: '100%' }}>Registrarse</button>
      {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
      {success && <div style={{ color: 'green', marginTop: 8 }}>{success}</div>}
    </form>
  );
}
