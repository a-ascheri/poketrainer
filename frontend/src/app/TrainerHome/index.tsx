import { useState } from 'react'; 
import GameShell from '../../components/Game/GameShell';
import PokemonSearchModal from '../../components/Pokemon/PokemonSearchModal';
//import PokemonSearch from '../../components/Pokemon/PokemonSearch';
import './trainer-home.scss';

/**
 * Vista principal del entrenador:
 * consola de juego arriba + buscador de pokémon abajo.
 */
export default function TrainerHome() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = () => setIsModalOpen(true); 
  const closeModal = () => setIsModalOpen(false); 

  return (
    <div className="trainer-home">
      <GameShell />
      <div className="trainer-home__pokedex-header">
        <h2 className="trainer-home__title">Pokédex</h2>
        <button 
          className="trainer-home__search-trigger"
          onClick={openModal}
        >
          Buscar Pokémon
        </button>
      </div>

      <PokemonSearchModal 
        isOpen={isModalOpen} 
        onClose={closeModal} 
      />
      {/* FIN del bloque agregado */}
    </div>
  );
}
