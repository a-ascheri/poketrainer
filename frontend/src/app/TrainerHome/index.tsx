import { useState } from 'react'; 
import GameShell from '../../components/Game/GameShell';
import PokemonSearchModal from '../../components/Pokemon/PokemonSearchModal';
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
        <button 
          className="trainer-home__title"
          onClick={openModal}
        >
          Pokédex
        </button>
      </div>

      <PokemonSearchModal 
        isOpen={isModalOpen} 
        onClose={closeModal} 
      />
    </div>
  );
}