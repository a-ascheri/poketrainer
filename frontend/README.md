# PokeTrainer Frontend

Frontend modular construido con React + Vite + TypeScript.

## Tecnologías

- React 19
- Vite 8
- TypeScript 5
- Axios
- Sass
- React Router

## Estructura

```text
src/
	app/                  # Composición principal de pantallas y rutas
	components/           # Componentes reutilizables por dominio
		Auth/
		Layout/
		Pokemon/
	context/              # Estado global (AuthContext)
	services/             # API backend + servicios de PokeAPI
	assets/               # Recursos estáticos
	styles/               # Estilos globales
```

## Scripts

- `npm run dev`: levanta el entorno de desarrollo.
- `npm run build`: chequeo TypeScript + build producción.
- `npm run lint`: análisis estático de código.
- `npm run preview`: preview de build local.

## Variables y Endpoints

- Backend esperado: `http://localhost:8000`
- Login: `POST /login`
- Registro: `POST /users/`
- Pokemons: `https://pokeapi.co/api/v2/pokemon/{nameOrId}`

## Flujo inicial

1. Registro de usuario.
2. Login.
3. Acceso a home protegida con buscador Pokémon.
4. Logout elimina token y limpia contraseña en el formulario (se conserva solo usuario previo para comodidad).

## Desarrollo

Este frontend está preparado para crecer por módulos sin acoplar la UI a los servicios.
Para nuevos dominios, agregar carpetas bajo `components` y `services` manteniendo la separación de responsabilidades.
