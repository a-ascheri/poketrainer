import { useEffect, useState } from 'react';
import { deleteUser, listUsers, updateUser } from '@services/admin/adminService';
import { type UserProfile } from '@services/auth/authService';
import './styles.scss';

const UserManagement = () => {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [username, setUsername] = useState('');

  const loadUsers = async () => {
    setError('');
    try {
      setUsers(await listUsers());
    } catch {
      setError('No se pudo cargar la lista de usuarios.');
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const startEdit = (user: UserProfile) => {
    setEditingId(user.id);
    setUsername(user.username);
  };

  const saveEdit = async () => {
    if (!editingId) {
      return;
    }

    try {
      await updateUser(editingId, { username });
      setEditingId(null);
      setUsername('');
      await loadUsers();
    } catch {
      setError('No se pudo actualizar el usuario.');
    }
  };

  const remove = async (userId: number) => {
    try {
      await deleteUser(userId);
      await loadUsers();
    } catch {
      setError('No se pudo eliminar el usuario.');
    }
  };

  return (
    <section className="admin-users">
      <h2>Administración de usuarios</h2>
      <p>Panel exclusivo para admins. Edición y soft delete de cuentas.</p>

      {error && <p className="admin-users__error">{error}</p>}

      <div className="admin-users__table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>
                  {editingId === user.id ? (
                    <input
                      value={username}
                      onChange={(event) => setUsername(event.target.value)}
                    />
                  ) : (
                    user.username
                  )}
                </td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{user.is_active ? 'Activo' : 'Inactivo'}</td>
                <td>
                  {editingId === user.id ? (
                    <button onClick={saveEdit}>Guardar</button>
                  ) : (
                    <button onClick={() => startEdit(user)}>Editar</button>
                  )}
                  <button onClick={() => remove(user.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default UserManagement;
