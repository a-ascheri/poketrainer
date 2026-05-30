# Poketrainer

Proyecto de pruebas usando la PokeAPI.

## Estructura
- backend/: API y lógica de negocio (FastAPI + SQLAlchemy)
- frontend/: React + Vite + TypeScript

## Cómo empezar
1. Clona el repositorio
2. Levanta backend:
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn src.main:app --reload
3. Levanta frontend:
   cd frontend
   npm install
   npm run dev

## Pruebas publicas seguras (ngrok)
1. Levanta backend y frontend localmente.
2. Deja `frontend/.env` con esta base URL para local:
  VITE_API_BASE_URL=http://localhost:8000
3. Crea un tunel para frontend (5173):
  ngrok http 5173 --basic-auth "usuario:password-fuerte"
4. Crea un tunel para backend (8000):
  ngrok http 8000 --basic-auth "usuario:password-fuerte"
5. Para prueba publica, cambia temporalmente `frontend/.env` a la URL publica del backend:
  VITE_API_BASE_URL=https://TU-BACKEND.ngrok-free.app
6. Reinicia frontend despues de cambiar `.env`.

Notas:
- Usa credenciales fuertes y compartelas por un canal seguro.
- No dejes los tuneles abiertos mas tiempo del necesario.
- Para mayor seguridad, ngrok soporta OAuth (`--oauth google`) en lugar de basic auth.
- Con `allowedHosts` configurado para `.ngrok-free.app`, no hace falta editar `vite.config.ts` cada vez que cambie la URL de ngrok del frontend.

## Seguridad y roles
- Se crea automáticamente un admin inicial:
  - username: `originadmin`
  - password: `admin123`
- El admin inicial debe cambiar password en el primer login.
- Los endpoints para crear admins son internos y ocultos en Swagger (`/api/v1/admin/internal/admins`).
- Borrado lógico (soft delete) para usuarios/admins.

## Flujo trainer
- Registro público por `/api/v1/user/register`.
- Primer login: selección obligatoria de starter (Bulbasaur, Charmander, Squirtle).
- Gestión de experiencia y progresión de Pokémon mediante endpoints `/api/v1/game/trainer/*`.

## API versionada por dominio
- Base API: `/api/v1`
- User: `/api/v1/user/*` (registro, login, perfil, cambio de contraseña)
- Admin: `/api/v1/admin/*` (gestión administrativa y endpoints internos)
- Admin Trainer Management: `/api/v1/admin/trainers/*`
- Trainer Game: `/api/v1/game/trainer/*` (starter, captura, stats, experiencia)
- System: `/api/v1/system/*` (estado y healthcheck)

## Tests
- Backend:
  - `cd backend && source .venv/bin/activate && pytest -q`
- Frontend:
  - `cd frontend && npm run lint && npm run build`

## Contribuciones
¡Pull requests y sugerencias son bienvenidas!

## Licencia
Ver LICENSE.
