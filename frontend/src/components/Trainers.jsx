import React, { useEffect, useState } from 'react';
import api from '../api/api';

export default function Trainers() {
  const [trainers, setTrainers] = useState([]);
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');

  const fetchTrainers = async () => {
    try {
      const res = await api.get('/trainers/');
      setTrainers(res.data);
    } catch (err) {
      setError('Error al cargar entrenadores');
    }
  };

  useEffect(() => {
    fetchTrainers();
  }, []);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    try {
      if (editingId) {
        await api.put(`/trainers/${editingId}`, form);
      } else {
        await api.post('/trainers/', form);
      }
      setForm({ username: '', email: '', password: '' });
      setEditingId(null);
      fetchTrainers();
    } catch (err) {
      setError('Error al guardar');
    }
  };

  const handleEdit = trainer => {
    setForm({ username: trainer.username, email: trainer.email, password: '' });
    setEditingId(trainer.id);
  };

  const handleDelete = async id => {
    if (!window.confirm('¿Eliminar entrenador?')) return;
    try {
      await api.delete(`/trainers/${id}`);
      fetchTrainers();
    } catch (err) {
      setError('Error al eliminar');
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto' }}>
      <h2>Entrenadores</h2>
      <form onSubmit={handleSubmit} style={{ marginBottom: 16 }}>
        <input
          name="username"
          placeholder="Usuario"
          value={form.username}
          onChange={handleChange}
          required
          style={{ marginRight: 8 }}
        />
        <input
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
          style={{ marginRight: 8 }}
        />
        <input
          name="password"
          placeholder="Contraseña"
          type="password"
          value={form.password}
          onChange={handleChange}
          required={!editingId}
          style={{ marginRight: 8 }}
        />
        <button type="submit">{editingId ? 'Actualizar' : 'Crear'}</button>
        {editingId && <button type="button" onClick={() => { setEditingId(null); setForm({ username: '', email: '', password: '' }); }}>Cancelar</button>}
      </form>
      {error && <div style={{ color: 'red', marginBottom: 8 }}>{error}</div>}
      <table border="1" cellPadding="8" style={{ width: '100%' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Usuario</th>
            <th>Email</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {trainers.map(tr => (
            <tr key={tr.id}>
              <td>{tr.id}</td>
              <td>{tr.username}</td>
              <td>{tr.email}</td>
              <td>
                <button onClick={() => handleEdit(tr)}>Editar</button>
                <button onClick={() => handleDelete(tr.id)} style={{ marginLeft: 8 }}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
