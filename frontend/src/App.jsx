import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Trainers from './components/Trainers';
import Register from './components/Register';
import { getToken, removeToken } from './utils/auth';

function App() {
  const [isAuth, setIsAuth] = useState(!!getToken());
  const [showRegister, setShowRegister] = useState(false);

  const handleLogout = () => {
    removeToken();
    setIsAuth(false);
  };

  return (
    <BrowserRouter>
      <div style={{ padding: 16 }}>
        <h1>PokeTrainer CRUD</h1>
        {isAuth && <button onClick={handleLogout} style={{ float: 'right' }}>Salir</button>}
        <Routes>
          <Route path="/login" element={
            showRegister ? (
              <Register onRegister={() => setShowRegister(false)} />
            ) : (
              <Login onLogin={() => setIsAuth(true)} />
            )
          } />
          <Route path="/" element={isAuth ? <Trainers /> : <Navigate to="/login" />} />
        </Routes>
        {!isAuth && !showRegister && (
          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <button onClick={() => setShowRegister(true)}>Crear usuario nuevo</button>
          </div>
        )}
        {!isAuth && showRegister && (
          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <button onClick={() => setShowRegister(false)}>Volver al login</button>
          </div>
        )}
      </div>
    </BrowserRouter>
  );
}

export default App;
