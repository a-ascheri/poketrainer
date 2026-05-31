import GameShell from '../../components/Game/GameShell';
import PokemonSearch from '../../components/Pokemon/PokemonSearch';
import './trainer-home.scss';

/**
 * Vista principal del entrenador:
 * consola de juego arriba + buscador de pokémon abajo.
 */
export default function TrainerHome() {
  return (
    <div className="trainer-home">
      <GameShell />
      <PokemonSearch />
    </div>
  );
}
